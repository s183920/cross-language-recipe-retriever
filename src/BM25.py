
from pyserini.search.lucene import LuceneSearcher

"""
    This module implements the BM25 algorithm for ranking documents.
"""

# test english index
searcher = LuceneSearcher('../indexes/english_index')
hits = searcher.search('chicken egg potato')

for i in range(len(hits)):
    print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')


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

for i in range(len(hits)):
    print(f'{i+1:2} {hits[i].docid:4} {hits[i].score:.5f}')