"""Branchial and Topological Distance Metrics for Hypergraphs and Scenario Trees."""

from typing import Any

from em_cubed.hypergraph.causal_dag import CausalDAG
from em_cubed.hypergraph.store import HypergraphStore
from em_cubed.hypergraph.types import Hyperedge


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Calculate Jaccard Index: J(A, B) = |A ∩ B| / |A ∪ B|."""
    if not set_a and not set_b:
        return 1.0
    union_len = len(set_a | set_b)
    if union_len == 0:
        return 0.0
    return len(set_a & set_b) / union_len


def overlap_coefficient(set_a: set[str], set_b: set[str]) -> float:
    """Calculate Overlap Coefficient: Overlap(A, B) = |A ∩ B| / min(|A|, |B|)."""
    if not set_a or not set_b:
        return 0.0
    min_len = min(len(set_a), len(set_b))
    if min_len == 0:
        return 0.0
    return len(set_a & set_b) / min_len


def hyperedge_jaccard(edge_a: Hyperedge, edge_b: Hyperedge) -> float:
    """Calculate Jaccard similarity between member entity sets of two hyperedges."""
    return jaccard_similarity(edge_a.member_entities, edge_b.member_entities)


def store_jaccard_similarity(
    store_a: HypergraphStore, store_b: HypergraphStore
) -> float:
    """Calculate Jaccard similarity between entity sets of two hypergraph stores."""
    entities_a = store_a.all_entities()
    entities_b = store_b.all_entities()
    return jaccard_similarity(entities_a, entities_b)


def identify_pivot_points(dag_a: CausalDAG, dag_b: CausalDAG) -> list[dict[str, Any]]:
    """Identify exact decision/divergence nodes (pivot points) between two scenario DAG branches.

    Compares causal nodes present in both DAG branches and identifies nodes where
    child mutations diverge or payloads differ.
    """
    nodes_a = {node.node_id: node for node in dag_a.all_nodes()}
    nodes_b = {node.node_id: node for node in dag_b.all_nodes()}

    common_node_ids = set(nodes_a.keys()) & set(nodes_b.keys())
    pivot_points: list[dict[str, Any]] = []

    for nid in common_node_ids:
        node_a = nodes_a[nid]
        node_b = nodes_b[nid]

        is_divergent = False
        reasons: list[str] = []

        if node_a.state_hash != node_b.state_hash:
            is_divergent = True
            reasons.append("state_hash_mismatch")
        if node_a.mutation_type != node_b.mutation_type:
            is_divergent = True
            reasons.append("mutation_type_mismatch")
        if node_a.payload != node_b.payload:
            is_divergent = True
            reasons.append("payload_mismatch")

        if is_divergent:
            pivot_points.append(
                {
                    "node_id": nid,
                    "reasons": reasons,
                    "branch_a_hash": node_a.state_hash,
                    "branch_b_hash": node_b.state_hash,
                }
            )

    return pivot_points
