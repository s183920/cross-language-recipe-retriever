"""
This file contains the CrossLanguageRetriever class.
"""
import argparse
from BM25 import BM25
import numpy as np
from translator import Translator

class CrossLanguageRetriever:

    def __init__(self, languages, translation_approach = "dictionary", verbose=True):
        """
            Initialize the retriever with the given languages.
        """
        
        self.languages = languages
        self.verbose = verbose

        # initialize the translation model
        self.translation_model = Translator(self.languages, approach=translation_approach, verbose=verbose)

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

            if self.verbose:
                print(f"Translated query into {language}:", translated_query)
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
        
        # only return the top k results
        results_merged = results_merged[:k]

        return results_merged, results_by_language



