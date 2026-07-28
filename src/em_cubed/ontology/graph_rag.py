"""Neurosymbolic Graph-Path RAG Engine.

Traverses multi-hop semantic triple paths (Subject -> Predicate -> Object -> Predicate' -> Object')
to retrieve logically grounded context subgraphs instead of flat semantic vector passages.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


@dataclass
class SubgraphPath:
    """Represents a multi-hop traversal path across semantic triples."""

    nodes: list[str]
    predicates: list[str]
    triples: list[OntologyTriple] = field(default_factory=list)
    confidence: float = 1.0

    def to_summary_string(self) -> str:
        """Format path as readable chain: NodeA -[Pred1]-> NodeB -[Pred2]-> NodeC."""
        chain: list[str] = []
        for i in range(len(self.predicates)):
            chain.append(f"{self.nodes[i]} -[{self.predicates[i]}]-> ")
        if self.nodes:
            chain.append(self.nodes[-1])
        return "".join(chain)


class GraphPathRAG:
    """Engine executing graph-path traversal over semantic triple repositories."""

    def __init__(self, triples: list[OntologyTriple] | None = None) -> None:
        self.triples: list[OntologyTriple] = triples or []

    def add_triple(self, triple: OntologyTriple) -> None:
        """Add a semantic triple to the repository."""
        self.triples.append(triple)

    def find_paths(
        self,
        start_entity: str,
        target_entity: str | None = None,
        max_depth: int = 3,
    ) -> list[SubgraphPath]:
        """Find multi-hop graph traversal paths starting from start_entity.

        Parameters
        ----------
        start_entity : str
            Entity ID to begin traversal from.
        target_entity : str | None
            Optional target entity ID to reach.
        max_depth : int
            Maximum path depth (default 3).

        Returns
        -------
        list[SubgraphPath]
            Matching traversal paths.
        """
        logger.info("Finding graph paths from '%s' (max_depth=%d)...", start_entity, max_depth)
        paths: list[SubgraphPath] = []

        def dfs(
            current_entity: str,
            current_nodes: list[str],
            current_preds: list[str],
            current_triples: list[OntologyTriple],
            depth: int,
        ) -> None:
            if depth >= max_depth:
                return

            for t in self.triples:
                if t.subject == current_entity and t.object not in current_nodes:
                    next_nodes = current_nodes + [t.object]
                    next_preds = current_preds + [t.predicate]
                    next_triples = current_triples + [t]
                    path_obj = SubgraphPath(nodes=next_nodes, predicates=next_preds, triples=next_triples)

                    if target_entity is None or t.object == target_entity:
                        paths.append(path_obj)

                    dfs(t.object, next_nodes, next_preds, next_triples, depth + 1)

        dfs(start_entity, [start_entity], [], [], 0)
        logger.info("Discovered %d graph paths from '%s'.", len(paths), start_entity)
        return paths

    def retrieve_grounded_context(self, entity_id: str, max_depth: int = 2) -> str:
        """Generate a formatted markdown context string of graph paths for LLM steering."""
        paths = self.find_paths(start_entity=entity_id, max_depth=max_depth)
        if not paths:
            return f"No grounded graph paths found for entity '{entity_id}'."

        context_lines = [f"### Grounded Knowledge Subgraph for '{entity_id}':"]
        for p in paths:
            context_lines.append(f"- {p.to_summary_string()}")

        return "\n".join(context_lines)
