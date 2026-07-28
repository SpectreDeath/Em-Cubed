"""Federated Ontology Registry.

Manages distributed, versioned semantic triple synchronization across agent swarm nodes
with SHA-256 state checksum verification.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


@dataclass
class SwarmNodeState:
    """Represents state checksum and registered triples of a federated swarm node."""

    node_id: str
    triples: list[OntologyTriple] = field(default_factory=list)
    state_checksum: str = ""


class FederatedOntologyRegistry:
    """Registry managing distributed triple synchronization and state checksum verification."""

    def __init__(self) -> None:
        self.nodes: dict[str, SwarmNodeState] = {}

    def register_node(self, node_id: str) -> SwarmNodeState:
        """Register a new federated node in the registry."""
        if node_id not in self.nodes:
            self.nodes[node_id] = SwarmNodeState(node_id=node_id)
        return self.nodes[node_id]

    def compute_state_checksum(self, triples: list[OntologyTriple]) -> str:
        """Compute deterministic SHA-256 checksum over a list of OntologyTriples."""
        raw_list = [f"{t.subject}:{t.predicate}:{t.object}:{t.confidence:.2f}" for t in triples]
        raw_str = "|".join(sorted(raw_list))
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def sync_triples(self, node_id: str, new_triples: list[OntologyTriple]) -> tuple[bool, str]:
        """Synchronize new triples for node_id and update node state checksum."""
        node = self.register_node(node_id)
        node.triples.extend(new_triples)
        node.state_checksum = self.compute_state_checksum(node.triples)

        logger.info(
            "Synchronized %d triples for node '%s'. Checksum: %s", len(new_triples), node_id, node.state_checksum[:8]
        )
        return True, node.state_checksum

    def verify_swarm_alignment(self) -> tuple[bool, str]:
        """Verify if all registered nodes in the swarm share identical state checksums."""
        if not self.nodes:
            return True, "No nodes registered"

        checksums = {node.state_checksum for node in self.nodes.values()}
        if len(checksums) == 1:
            return True, f"Swarm fully aligned (Checksum: {next(iter(checksums))[:8]})"

        return False, f"Swarm misalignment detected across {len(checksums)} distinct checksum states"
