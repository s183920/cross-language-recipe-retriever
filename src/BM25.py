from pyserini.search import SimpleSearcher

"""
    This module implements the BM25 algorithm for ranking documents.
"""



searcher = SimpleSearcher.from_prebuilt_index('robust04')

hits = searcher.search('black bear attacks', 1000)

# Prints the first 10 hits
for i in range(0, 10):
    print(f'{i+1:2} {hits[i].docid:15} {hits[i].score:.5f}')