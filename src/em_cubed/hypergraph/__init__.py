"""Wolfram-inspired Pragmatic Hypergraph engine for em-cubed.

Provides N-ary hyperedges, fast store indexing, deterministic compaction,
append-only causal DAG provenance, and branchial scenario metrics.
"""

from em_cubed.hypergraph.causal_dag import CausalDAG, CausalNode
from em_cubed.hypergraph.compaction import CompactionPipeline
from em_cubed.hypergraph.metrics import (
    hyperedge_jaccard,
    identify_pivot_points,
    jaccard_similarity,
    overlap_coefficient,
    store_jaccard_similarity,
)
from em_cubed.hypergraph.store import HypergraphStore
from em_cubed.hypergraph.types import Hyperedge

__all__ = [
    "Hyperedge",
    "HypergraphStore",
    "CompactionPipeline",
    "CausalNode",
    "CausalDAG",
    "jaccard_similarity",
    "overlap_coefficient",
    "hyperedge_jaccard",
    "store_jaccard_similarity",
    "identify_pivot_points",
]
