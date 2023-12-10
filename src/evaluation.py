from cross_language_retriever import CrossLanguageRetriever
from ranking_fetcher import fetch_rankings
import json
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

LANGUAGES = ["english", "czech", "chinese", "danish"]

get_lang_idx = lambda x: LANGUAGES.index(x)


class CrossLanguageEvaluator():

    def __init__(self, translation_approach = "dictionary") -> None:
        self.create_labels()
        self.retriever = CrossLanguageRetriever(LANGUAGES, verbose=False, translation_approach = translation_approach)
    
    
    def create_labels(self):
        # load rankings
        rankings = fetch_rankings(LANGUAGES)


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
        relevance_score = ranking[ranking["docid"] == docid]["ranking_manual"]
        
        if len(relevance_score) > 1:
            # raise ValueError(f"More than one relevance score found for query '{query}' and docid '{docid}'")
            print(f"WARNING: More than one relevance score found for query '{query}' and docid '{docid}'")

        relevance_score = relevance_score.iloc[0]
        
        return relevance_score
    
    def get_relevance_scores(self, query, k=10, language = None):
        # get search results
        results_merged, results_by_lan = self.retriever.search(query, k = k)
        results = results_merged if language is None else results_by_lan[get_lang_idx(language)]
        
        # get the relevance scores
        relevance_scores = np.array([self.get_relevance(query, result.docid) for result in results])
        
        return relevance_scores

    def DCGs(self, query, p = 10, language = None):
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
    
    def DCG(self, query, p = 10, language = None):
        return self.DCGs(query, p = p, language = language)[p-1]
    
    def NDCGs(self, query, p = 10, language = None):
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
        dcgs = self.DCGs(query, p = p, language = language)
        
        # get ideal dcg
        ideal_dcgs = relevance_scores[np.argsort(relevance_scores)[::-1]].copy().astype(float)
        ideal_dcgs[1:] = ideal_dcgs[1:] / np.log2(np.arange(2, len(ideal_dcgs) + 1))
        ideal_dcgs = np.cumsum(ideal_dcgs)
        
        return (dcgs / ideal_dcgs)
    
    def NDCG(self, query, p = 10, language = None):
        return self.NDCGs(query, p = p, language = language)[p-1]
    
    def AP(self, query, p = 10, language = None):
        """
        Computes AP@p for a given query
            
        Parameters
        ---------
        query:
            The query for which to compute the AP
        p:
            The number of results to consider
        language:
            The language for which to compute the AP.    
            If language is None, the AP is computed for all languages meaning p results are fetched for each language and the AP scores will thus have a length of num languages * p
        """
        # get relevance scores
        relevance_scores = self.get_relevance_scores(query, k = p, language = language)
                
        # create document ranks
        ranks = np.arange(1, len(relevance_scores) + 1)
        
        # compute a mask showing the relevant documents
        relevance_mask = relevance_scores > 0 # ensure binary relevance labels by treating all non-zero labels as relevant
        
        # extract the ranks of the relevant documents using the mask
        relevant_ranks = ranks[relevance_mask]
        
        # compute the precision for each relevant document
        precisions = np.arange(1, len(relevant_ranks)+1) / relevant_ranks
        
        return precisions.mean()
    
    def evaluate(self, test_queries,p = 10):
        """
        Evaluates the cross language retriever on the given test queries.
        
        Parameters
        ---------
        test_queries:
            A list of test queries
        p:
            The number of results to consider
        """
        # create data frame
        results_df = pd.DataFrame()
        
        # evaluate each query
        for query in test_queries:
            # get the relevance scores
            relevance_scores = self.get_relevance_scores(query, k = p)
            
            # get the dcg
            dcg = self.DCG(query, p = p)
            
            # get the ndcg
            ndcg = self.NDCG(query, p = p)
            
            # get the ap
            ap = self.AP(query, p = p)
            
            # create data frame
            df_ = pd.DataFrame({"query": query, "relevance_scores": [relevance_scores], "dcg": dcg, "ndcg": ndcg, "ap": ap})
            
            # add to results df
            results_df = pd.concat([results_df, df_], axis = 0)
            
        # reset index
        results_df = results_df.reset_index(drop = True)
        
        return results_df
    

def plot_evaluation(results, save_path = None):   
    fig, ax = plt.subplots(figsize = (10, 5))
    
    p = len(results["relevance_scores"].iloc[0])   
    x = np.arange(1, p+1)
    
    # ax.scatter(x, results["dcg"], label = "DCG")
    ax.scatter(x, results["ndcg"], label = f"NDCG@{p}")
    ax.scatter(x, results["ap"], label = f"AP@{p}")
    ax.axhline(results["ndcg"].mean(), color = "blue", linestyle = "--", label = f"Mean NDCG@{p}")
    ax.axhline(results["ap"].mean(), color = "orange", linestyle = "--", label = f"MAP@{p}")
    
    # ax.set_xticklabels(results["query"], rotation = 45, ha = "right")
    ax.set_xticks(x)
    ax.set_xlabel("Query")
    ax.set_ylabel("Score")
    ax.set_title(f"Cross Language Retrieval Evaluation (p = {p})")
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    # plt.tight_layout()
    fig.tight_layout()
    
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":

    # translation methods
    translation_approaches = ["dictionary", "hf", "translatepy"]

    # initialize the evaluator
    evaluator = CrossLanguageEvaluator(translation_approach = "translatepy")
    
    # test on test queries
    p = 10
    test_queries = [line.strip() for line in open("../test_queries.txt", "r").readlines()]
    results = evaluator.evaluate(test_queries, p = p)
    print(results)
    print(f"Mean DCG@{p}:", results["dcg"].mean())
    print(f"Mean NDCG@{p}:", results["ndcg"].mean())
    print(f"MAP@{p}:", results["ap"].mean())
    
    # plot results
    import os
    os.makedirs("../plots", exist_ok = True)
    plot_evaluation(results, save_path = f"../plots/evaluation_{p}.pdf")
    
    
    
    # test query
    # print(evaluator.DCG("sugar spinach seaweed"))
    # print(evaluator.NDCG("sugar spinach seaweed"))
    # print(evaluator.AP("sugar spinach seaweed"))
    
    