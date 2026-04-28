import pytest
from core.indexer import Indexer

class TestIndexer:
    def test_index_and_search(self):
        idx = Indexer()
        idx.index({'id': 1, 'content': 'hello world'})
        results = idx.search('hello')
        assert len(results) == 1
