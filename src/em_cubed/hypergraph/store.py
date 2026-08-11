"""In-memory hypergraph store with fast inverted entity indexing."""

from typing import Any, Dict, List, Optional, Set
from em_cubed.hypergraph.types import Hyperedge


class HypergraphStore:
    """Storage container for hyperedges with bi-directional indexing."""

    def __init__(self) -> None:
        self._edges: Dict[str, Hyperedge] = {}
        self._entity_index: Dict[str, Set[str]] = {}

    def add_edge(self, edge: Hyperedge) -> None:
        """Add or update a hyperedge in the store and update inverted index."""
        if edge.edge_id in self._edges:
            self.remove_edge(edge.edge_id)

        self._edges[edge.edge_id] = edge
        for entity in edge.member_entities:
            if entity not in self._entity_index:
                self._entity_index[entity] = set()
            self._entity_index[entity].add(edge.edge_id)

    def remove_edge(self, edge_id: str) -> Optional[Hyperedge]:
        """Remove a hyperedge by ID and clean up inverted index entries."""
        edge = self._edges.pop(edge_id, None)
        if edge:
            for entity in edge.member_entities:
                if entity in self._entity_index:
                    self._entity_index[entity].discard(edge_id)
                    if not self._entity_index[entity]:
                        del self._entity_index[entity]
        return edge

    def get_edge(self, edge_id: str) -> Optional[Hyperedge]:
        """Retrieve hyperedge by ID."""
        return self._edges.get(edge_id)

    def get_edges_for_entity(self, entity: str) -> Set[Hyperedge]:
        """Find all hyperedges containing the specified entity."""
        edge_ids = self._entity_index.get(entity, set())
        return {self._edges[eid] for eid in edge_ids if eid in self._edges}

    def get_edges_for_entities(
        self, entities: Set[str], match_all: bool = False
    ) -> Set[Hyperedge]:
        """Find hyperedges containing given entities (any or all)."""
        if not entities:
            return set()

        if match_all:
            result_ids: Optional[Set[str]] = None
            for entity in entities:
                current_ids = self._entity_index.get(entity, set())
                if result_ids is None:
                    result_ids = set(current_ids)
                else:
                    result_ids &= current_ids
                if not result_ids:
                    break
            final_ids = result_ids or set()
        else:
            final_ids = set()
            for entity in entities:
                final_ids.update(self._entity_index.get(entity, set()))

        return {self._edges[eid] for eid in final_ids if eid in self._edges}

    def query_by_intersection(self, min_entities: Set[str]) -> Set[Hyperedge]:
        """Alias for get_edges_for_entities with match_all=True."""
        return self.get_edges_for_entities(min_entities, match_all=True)

    def query_by_metadata(self, key: str, value: Any) -> Set[Hyperedge]:
        """Query hyperedges matching a metadata key-value pair."""
        return {
            edge
            for edge in self._edges.values()
            if edge.metadata.get(key) == value
        }

    def all_edges(self) -> List[Hyperedge]:
        """Return list of all stored hyperedges."""
        return list(self._edges.values())

    def all_entities(self) -> Set[str]:
        """Return set of all indexed entity names across hyperedges."""
        return set(self._entity_index.keys())

    def __len__(self) -> int:
        return len(self._edges)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire store to dictionary representation."""
        return {
            "edges": [edge.to_dict() for edge in self._edges.values()]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HypergraphStore":
        """Deserialize store from dictionary representation."""
        store = cls()
        for edge_data in data.get("edges", []):
            store.add_edge(Hyperedge.from_dict(edge_data))
        return store
