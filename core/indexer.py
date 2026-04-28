# Indexer and search engine
from typing import List, Dict, Any

class Indexer:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def index(self, doc: Dict[str, Any]) -> None:
        self.documents.append(doc)

    def search(self, query: str) -> List[Dict[str, Any]]:
        return [d for d in self.documents if query.lower() in str(d).lower()]
