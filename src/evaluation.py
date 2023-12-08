from cross_language_retriever import CrossLanguageRetriever
import json
import pandas as pd
import re
import numpy as np

LANGUAGES = ["english", "czech", "chinese", "danish"]

get_lang_idx = lambda x: LANGUAGES.index(x)


class CrossLanguageEvaluator():
    def __init__(self) -> None:
        self.create_labels()
        self.retriever = CrossLanguageRetriever(LANGUAGES, verbose=False)
    
    
    def create_labels(self):
        # load rankings
        rankings = {}
        for lang in LANGUAGES:
            rankings[lang] = json.load(open(f"../rankings/{lang}.json"))


        # create data frame
        labels_df = pd.DataFrame()

        for lang in LANGUAGES:
            lang_rankings = rankings[lang]
            for query_name in lang_rankings.keys():
                df_ = pd.DataFrame(lang_rankings[query_name]).T.reset_index(names = "docid")
                df_["docid"] = df_["docid"].apply(lambda x: re.sub('[^\w\-_\. ]', '', x))
                df_["query_name"] = query_name
                df_["query"] = query_name.replace("+", " ")
                df_["language"] = lang
                labels_df = pd.concat([labels_df, df_], axis = 0)
                
        # reset index and add to self
        self.labels_df = labels_df.reset_index(drop = True)
        
    def get_relevance(self, query, docid):
        """
        Returns the relevance score for a given query and docid
        """
        if docid not in self.labels_df["docid"].values:
            raise ValueError(f"Docid '{docid}' not found in labels")
        
        # get the ranking entry for the query
        ranking = self.labels_df[self.labels_df["query"] == query]
        
        # return 0 relevance if found recipe was not for the given query
        if docid not in ranking["docid"].values:
            return 0
        
        # get the relevance score
        relevance_score = ranking[ranking["docid"] == docid]["ranking_manual"].item()
        
        return relevance_score
    
    def get_relevance_scores(self, query, k=10, language = None):
        # get search results
        results_merged, results_by_lan = self.retriever.search(query, k = k)
        results = results_merged if language is None else results_by_lan[get_lang_idx(language)]
        
        # get the relevance scores
        relevance_scores = np.array([self.get_relevance(query, result.docid) for result in results])
        
        return relevance_scores

    def DCG(self, query, p = 10, language = None):
        """
        Computes DCG@p for a given query
            
        Parameters
        ---------
        query:
            The query for which to compute the DCG
        p:
            The number of results to consider
        language:
            The language for which to compute the DCG.    
            If language is None, the DCG is computed for all languages meaning p results are fetched for each language and the DCG scores will thus have a length of num languages * p
        """
        # get relevance scores
        relevance_scores = self.get_relevance_scores(query, k = p, language = language)
        
        # calculate DCG
        dcg = np.zeros(len(relevance_scores))
        dcg[0] = relevance_scores[0]
        dcg[1:] = relevance_scores[1:] / np.log2(np.arange(2, len(relevance_scores) + 1))
        dcg = np.cumsum(dcg)
        
        
        return dcg
    
    def NDCG(self, query, p = 10, language = None):
        """
        Computes NDCG@p for a given query
            
        Parameters
        ---------
        query:
            The query for which to compute the NDCG
        p:
            The number of results to consider
        language:
            The language for which to compute the NDCG.    
            If language is None, the NDCG is computed for all languages meaning p results are fetched for each language and the NDCG scores will thus have a length of num languages * p
        """
        # get relevance scores
        relevance_scores = self.get_relevance_scores(query, k = p, language = language)
        
        # get dcg
        dcg = self.DCG(query, p = p, language = language)
        
        # get ideal dcg
        ideal_dcg = relevance_scores[np.argsort(relevance_scores)[::-1]].copy().astype(float)
        ideal_dcg[1:] = ideal_dcg[1:] / np.log2(np.arange(2, len(ideal_dcg) + 1))
        ideal_dcg = np.cumsum(ideal_dcg)
        
        return dcg / ideal_dcg
    

if __name__ == "__main__":
    evaluator = CrossLanguageEvaluator()
    
    # test query
    print(evaluator.DCG("sugar spinach seaweed", language="english"))
    print(evaluator.NDCG("sugar spinach seaweed", language="english"))