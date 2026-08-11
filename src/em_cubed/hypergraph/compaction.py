"""Monotonic Compaction and Lifecycle Mutation Logic for Hypergraphs."""

import time
from typing import Any, Dict, Optional, Set
from em_cubed.hypergraph.store import HypergraphStore
from em_cubed.hypergraph.types import Hyperedge


class CompactionPipeline:
    """Deterministic compaction routines to consolidate hyperedges and control graph memory growth."""

    @staticmethod
    def consolidate_shared_entities(
        store: HypergraphStore,
        shared_entities: Set[str],
        new_edge_id: str,
        new_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Hyperedge]:
        """Consolidate multiple hyperedges sharing an entity set into a single summary hyperedge.

        Finds all hyperedges containing all `shared_entities`, merges their member entities and
        metadata, removes the input hyperedges, and adds the newly consolidated hyperedge.
        """
        matching_edges = store.query_by_intersection(shared_entities)
        if len(matching_edges) <= 1:
            return None

        merged_members: Set[str] = set()
        merged_metadata: Dict[str, Any] = {}

        for edge in matching_edges:
            merged_members.update(edge.member_entities)
            merged_metadata.update(edge.metadata)
            store.remove_edge(edge.edge_id)

        if new_metadata:
            merged_metadata.update(new_metadata)

        consolidated_edge = Hyperedge(
            edge_id=new_edge_id,
            member_entities=merged_members,
            metadata=merged_metadata,
            created_at=time.time(),
        )
        store.add_edge(consolidated_edge)
        return consolidated_edge

    @staticmethod
    def bounded_local_compaction(
        store: HypergraphStore,
        root_entities: Set[str],
        max_hops: int = 1,
    ) -> Set[str]:
        """Discover entity IDs reachable within `max_hops` of `root_entities` for bounded local processing."""
        visited_entities: Set[str] = set(root_entities)
        frontier: Set[str] = set(root_entities)

        for _ in range(max_hops):
            next_frontier: Set[str] = set()
            for entity in frontier:
                edges = store.get_edges_for_entity(entity)
                for edge in edges:
                    for member in edge.member_entities:
                        if member not in visited_entities:
                            visited_entities.add(member)
                            next_frontier.add(member)
            frontier = next_frontier
            if not frontier:
                break

        return visited_entities

    @staticmethod
    def prune_subsumed_edges(store: HypergraphStore) -> int:
        """Prune hyperedges whose member entities are a proper subset of another hyperedge.

        Returns the total number of pruned edges.
        """
        all_edges = store.all_edges()
        to_remove: Set[str] = set()

        for i, edge_a in enumerate(all_edges):
            if edge_a.edge_id in to_remove:
                continue
            for j, edge_b in enumerate(all_edges):
                if i == j or edge_b.edge_id in to_remove:
                    continue

                # Check if edge_a is strictly a proper subset of edge_b
                if edge_a.member_entities.issubset(edge_b.member_entities) and len(
                    edge_a.member_entities
                ) < len(edge_b.member_entities):
                    to_remove.add(edge_a.edge_id)
                    break

        pruned_count = 0
        for edge_id in to_remove:
            if store.remove_edge(edge_id):
                pruned_count += 1

        return pruned_count
