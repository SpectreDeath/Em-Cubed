"""Types and dataclasses for N-ary Hyperedges."""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Hyperedge:
    """Represents an N-ary hyperedge connecting N entities simultaneously."""

    edge_id: str
    member_entities: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def __hash__(self) -> int:
        """Hash hyperedge by edge_id for set and dictionary key operations."""
        return hash(self.edge_id)

    def __eq__(self, other: object) -> bool:
        """Check equality based on edge_id."""
        if not isinstance(other, Hyperedge):
            return False
        return self.edge_id == other.edge_id

    def to_dict(self) -> dict[str, Any]:
        """Serialize hyperedge to dictionary format."""
        return {
            "edge_id": self.edge_id,
            "member_entities": sorted(self.member_entities),
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Hyperedge":
        """Deserialize hyperedge from dictionary format."""
        return cls(
            edge_id=data["edge_id"],
            member_entities=set(data.get("member_entities", [])),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", time.time()),
        )

    def compute_hash(self) -> str:
        """Compute SHA-256 canonical hash of the hyperedge state."""
        canonical = {
            "edge_id": self.edge_id,
            "member_entities": sorted(self.member_entities),
            "metadata": self.metadata,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
