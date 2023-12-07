"""
This file contains the CrossLanguageRetriever class.
"""

from BM25 import BM25

class CrossLanguageRetriever:

    def __init__(self, languages):
        """
            Initialize the retriever with the given languages.
        """
        
        self.languages = languages

        # initialize the retrievers
        self.retrievers = {language: BM25(language) for language in self.languages}


    def search(self, query, k=10):
        """
            Search the query in the index and return the top k results.
        """

        # search in all languages
        results = []
        for language in self.languages:
            hits = self.retrievers[language].search(query, k=k)
            results.append(hits)

        return results
    

if __name__ == "__main__":

    # initialize the retriever
    retriever = CrossLanguageRetriever(["english", "czech", "chinese", "danish"])

    # search
    results = retriever.search("chicken egg potato")

    # print the results
    for i in range(len(results)):
        print(f'\n\nResults for {retriever.languages[i]}:')
        for j in range(len(results[i])):
            print(f'{j+1:2} {results[i][j].docid:4} {results[i][j].score:.5f}')