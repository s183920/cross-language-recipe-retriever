"""
This file contains the CrossLanguageRetriever class.
"""

from BM25 import BM25
import numpy as np
from translator import Translator

class CrossLanguageRetriever:

    def __init__(self, languages):
        """
            Initialize the retriever with the given languages.
        """
        
        self.languages = languages

        # initialize the translation model
        self.translation_model = Translator(self.languages, dictionary_approach=True)

        # initialize the retrievers
        self.retrievers = {language: BM25(language) for language in self.languages}



    def search(self, query, k=10):
        """
            Search the query in the index and return the top k results.
        """

        # search in all languages
        results_by_language = []
        for language in self.languages:

            # translate the query
            translated_query = self.translation_model.translate(query, language)

            print(translated_query)
            # search in the given language
            hits = self.retrievers[language].search(translated_query, k=k)
            
            # save the results
            results_by_language.append(hits)

        # flatten the results by language
        results = []
        for i in range(len(results_by_language)):
            results += results_by_language[i]

        # sort the results by the score
        results_merged = sorted(results, key=lambda x: x.score, reverse=True)

        return results_merged, results_by_language
    

if __name__ == "__main__":

    # initialize the retriever
    retriever = CrossLanguageRetriever(["english", "czech", "chinese", "danish"])

    # search
    # test_query = "chicken egg potato"
    test_query = "beef pasta mushrooms"


    results_merged, results_by_lan = retriever.search(test_query)

    # print the results by language
    for i in range(len(results_by_lan)):
        print(f'\n\nResults for {retriever.languages[i]}:')
        for j in range(len(results_by_lan[i])):
            print(f'{j+1:2} {results_by_lan[i][j].docid:4} {results_by_lan[i][j].score:.5f}')

    # print the merged results
    print("\n\nMerged results:")
    for i in range(len(results_merged)):
        print(f'{i+1:2} {results_merged[i].docid:4} {results_merged[i].score:.5f}')