
from pyserini.search.lucene import LuceneSearcher

"""
    This module implements the BM25 algorithm for ranking documents.
"""


searcher = LuceneSearcher('../indexes/test_index/')
hits = searcher.search('document')

for i in range(len(hits)):
    print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')