"""SQLite Persistent Storage Adapter for Hypergraph Store and Causal DAG."""

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from em_cubed.hypergraph.causal_dag import CausalDAG, CausalNode
from em_cubed.hypergraph.store import HypergraphStore
from em_cubed.hypergraph.types import Hyperedge


class SQLiteHypergraphAdapter:
    """Persistent storage adapter storing Hypergraph stores and Causal DAGs in SQLite."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self) -> None:
        """Create database tables if they do not exist."""
        with self._connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS hyperedges (
                    edge_id TEXT PRIMARY KEY,
                    member_entities TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS causal_nodes (
                    node_id TEXT PRIMARY KEY,
                    parent_ids TEXT NOT NULL,
                    mutation_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    state_hash TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
                """
            )
            conn.commit()

    def save_store(self, store: HypergraphStore) -> None:
        """Persist all hyperedges from HypergraphStore to SQLite database."""
        with self._connection() as conn:
            conn.execute("DELETE FROM hyperedges")
            for edge in store.all_edges():
                conn.execute(
                    """
                    INSERT INTO hyperedges (edge_id, member_entities, metadata, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        edge.edge_id,
                        json.dumps(sorted(edge.member_entities)),
                        json.dumps(edge.metadata),
                        edge.created_at,
                    ),
                )
            conn.commit()

    def load_store(self) -> HypergraphStore:
        """Load HypergraphStore from SQLite database."""
        store = HypergraphStore()
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM hyperedges").fetchall()
            for row in rows:
                edge = Hyperedge(
                    edge_id=row["edge_id"],
                    member_entities=set(json.loads(row["member_entities"])),
                    metadata=json.loads(row["metadata"]),
                    created_at=row["created_at"],
                )
                store.add_edge(edge)
        return store

    def save_dag(self, dag: CausalDAG) -> None:
        """Persist CausalDAG ledger nodes to SQLite database."""
        with self._connection() as conn:
            conn.execute("DELETE FROM causal_nodes")
            for node in dag.all_nodes():
                conn.execute(
                    """
                    INSERT INTO causal_nodes (node_id, parent_ids, mutation_type, payload, state_hash, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        node.node_id,
                        json.dumps(node.parent_ids),
                        node.mutation_type,
                        json.dumps(node.payload),
                        node.state_hash,
                        node.timestamp,
                    ),
                )
            conn.commit()

    def load_dag(self) -> CausalDAG:
        """Load CausalDAG ledger from SQLite database."""
        dag = CausalDAG()
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM causal_nodes").fetchall()
            for row in rows:
                node = CausalNode(
                    node_id=row["node_id"],
                    parent_ids=json.loads(row["parent_ids"]),
                    mutation_type=row["mutation_type"],
                    payload=json.loads(row["payload"]),
                    state_hash=row["state_hash"],
                    timestamp=row["timestamp"],
                )
                dag._nodes[node.node_id] = node
                for pid in node.parent_ids:
                    if pid not in dag._children:
                        dag._children[pid] = set()
                    dag._children[pid].add(node.node_id)
        return dag
