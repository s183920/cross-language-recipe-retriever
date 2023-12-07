
from pyserini.search.lucene import LuceneSearcher

"""
    This module implements the BM25 algorithm for ranking documents.
"""

# test english index
# searcher = LuceneSearcher('../indexes/english_index')
# hits = searcher.search('chicken egg potato')

# for i in range(len(hits)):
#     print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')


# test czech index
searcher = LuceneSearcher('../indexes/czech_index')
searcher.set_language('cs') # set the language
hits = searcher.search('kuřecí rýže')

for i in range(len(hits)):
    print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')