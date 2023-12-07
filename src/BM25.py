
from pyserini.search.lucene import LuceneSearcher

"""
    This module implements the BM25 algorithm for ranking documents.
"""

class BM25:

    def __init__(self, language):

        self.language = language
        
        # initialize the BM25 searcher
        self.searcher = LuceneSearcher(f'../indexes/{language}_index')
        self.searcher.set_language(language)


    def search(self, query, k=10):
        """
            Search the query in the index and return the top k results.
        """

        hits = self.searcher.search(query, k=k)
        return hits




# test english index
# searcher = LuceneSearcher('../indexes/english_index')
# hits = searcher.search('chicken egg potato')

# for i in range(len(hits)):
#     print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')


# test czech index
# searcher = LuceneSearcher('../indexes/czech_index')
# searcher.set_language('cs') # set the language
# hits = searcher.search('kuřecí rýže')

# for i in range(len(hits)):
#     print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')

# test danish index
# searcher = LuceneSearcher('../indexes/danish_index')
# searcher.set_language('da') # set the language
# hits = searcher.search('kylling ris')

# test chinese index
# searcher = LuceneSearcher('../indexes/chinese_index')
# searcher.set_language('zh') # set the language
# hits = searcher.search('鸡 蛋 土豆')

# for i in range(len(hits)):
#     print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')


if __name__ == "__main__":

    bm25 = BM25('english')
    hits = bm25.search('chicken egg potato')

    for i in range(len(hits)):
        print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')