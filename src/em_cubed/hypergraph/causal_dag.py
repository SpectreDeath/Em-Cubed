"""Append-Only Causal DAG for Auditability and Provenance Tracking."""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CausalNode:
    """Represents an atomic state mutation or event in the causal DAG ledger."""

    node_id: str
    parent_ids: list[str] = field(default_factory=list)
    mutation_type: str = "GENERIC_MUTATION"
    payload: dict[str, Any] = field(default_factory=dict)
    state_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    def compute_hash(self) -> str:
        """Compute cryptographic hash of parent IDs, mutation type, and payload."""
        canonical = {
            "node_id": self.node_id,
            "parent_ids": sorted(self.parent_ids),
            "mutation_type": self.mutation_type,
            "payload": self.payload,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Serialize causal node to dictionary."""
        return {
            "node_id": self.node_id,
            "parent_ids": self.parent_ids,
            "mutation_type": self.mutation_type,
            "payload": self.payload,
            "state_hash": self.state_hash,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CausalNode":
        """Deserialize causal node from dictionary."""
        return cls(
            node_id=data["node_id"],
            parent_ids=data.get("parent_ids", []),
            mutation_type=data.get("mutation_type", "GENERIC_MUTATION"),
            payload=data.get("payload", {}),
            state_hash=data.get("state_hash", ""),
            timestamp=data.get("timestamp", time.time()),
        )


class CausalDAG:
    """Append-only Directed Acyclic Graph ledger for event lineage and auditability."""

    def __init__(self) -> None:
        self._nodes: dict[str, CausalNode] = {}
        self._children: dict[str, set[str]] = {}

    def record_mutation(
        self,
        mutation_type: str,
        payload: dict[str, Any],
        parent_ids: list[str] | None = None,
        node_id: str | None = None,
    ) -> CausalNode:
        """Append a new mutation event node to the causal ledger."""
        parents = parent_ids or []

        # Validate parents exist
        for pid in parents:
            if pid not in self._nodes:
                raise ValueError(f"Parent node '{pid}' does not exist in CausalDAG.")

        if not node_id:
            node_id = f"node_{len(self._nodes) + 1}_{int(time.time() * 1000)}"

        node = CausalNode(
            node_id=node_id,
            parent_ids=parents,
            mutation_type=mutation_type,
            payload=payload,
            timestamp=time.time(),
        )
        node.state_hash = node.compute_hash()

        self._nodes[node_id] = node
        for pid in parents:
            if pid not in self._children:
                self._children[pid] = set()
            self._children[pid].add(node_id)

        return node

    def get_node(self, node_id: str) -> CausalNode | None:
        """Retrieve node by ID."""
        return self._nodes.get(node_id)

    def verify_integrity(self) -> bool:
        """Verify hash validity for every node in the ledger."""
        for node in self._nodes.values():
            if node.state_hash != node.compute_hash():
                return False
            for pid in node.parent_ids:
                if pid not in self._nodes:
                    return False
        return True

    def trace_provenance(self, node_id: str) -> list[CausalNode]:
        """Trace full ancestor chain leading to the specified node in topological order."""
        if node_id not in self._nodes:
            return []

        visited: set[str] = set()
        provenance: list[CausalNode] = []

        def dfs(curr_id: str) -> None:
            if curr_id in visited:
                return
            visited.add(curr_id)
            node = self._nodes[curr_id]
            for pid in node.parent_ids:
                dfs(pid)
            provenance.append(node)

        dfs(node_id)
        return provenance

    def get_leaves(self) -> list[CausalNode]:
        """Return nodes that have no children (current terminal branches)."""
        all_parent_ids = {pid for n in self._nodes.values() for pid in n.parent_ids}
        return [n for nid, n in self._nodes.items() if nid not in all_parent_ids]

    def all_nodes(self) -> list[CausalNode]:
        """Return all recorded causal nodes."""
        return list(self._nodes.values())

    def __len__(self) -> int:
        return len(self._nodes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize causal DAG to dictionary representation."""
        return {
            "nodes": [node.to_dict() for node in self._nodes.values()]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CausalDAG":
        """Deserialize causal DAG from dictionary representation."""
        dag = cls()
        for node_data in data.get("nodes", []):
            node = CausalNode.from_dict(node_data)
            dag._nodes[node.node_id] = node
            for pid in node.parent_ids:
                if pid not in dag._children:
                    dag._children[pid] = set()
                dag._children[pid].add(node.node_id)
        return dag
