"""Wolfram-inspired Pragmatic Hypergraph engine for em-cubed.

Provides N-ary hyperedges, fast store indexing, deterministic compaction,
append-only causal DAG provenance, branchial scenario metrics, GEXF Gephi exporters,
and SQLite persistence.
"""

from em_cubed.hypergraph.causal_dag import CausalDAG, CausalNode
from em_cubed.hypergraph.compaction import CompactionPipeline
from em_cubed.hypergraph.exporter import export_dag_to_gexf, export_store_to_gexf
from em_cubed.hypergraph.metrics import (
    hyperedge_jaccard,
    identify_pivot_points,
    jaccard_similarity,
    overlap_coefficient,
    store_jaccard_similarity,
)
from em_cubed.hypergraph.persistence import SQLiteHypergraphAdapter
from em_cubed.hypergraph.store import HypergraphStore
from em_cubed.hypergraph.types import Hyperedge

__all__ = [
    "CausalDAG",
    "CausalNode",
    "CompactionPipeline",
    "Hyperedge",
    "HypergraphStore",
    "SQLiteHypergraphAdapter",
    "export_dag_to_gexf",
    "export_store_to_gexf",
    "hyperedge_jaccard",
    "identify_pivot_points",
    "jaccard_similarity",
    "overlap_coefficient",
    "store_jaccard_similarity",
]
