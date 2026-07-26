"""Categorical Multi-Surface Morphisms.

Implements structure-preserving category translation between Python Pydantic models,
Prolog predicates, Z3 SMT assertions, and Datalog rules.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel

from em_cubed.ontology.schema import OntologyTriple

logger = logging.getLogger(__name__)


class SurfaceMorphism:
    """Categorical Morphism performing structure-preserving surface translations."""

    @staticmethod
    def pydantic_to_prolog_facts(model: BaseModel) -> list[str]:
        """Map Pydantic model instance into Prolog facts: fact_name(entity_id, value)."""
        model_name = model.__class__.__name__.lower()
        data = model.model_dump()
        entity_id = data.get("id") or data.get("order_id") or data.get("user_id") or "entity_01"

        facts: list[str] = []
        for k, v in data.items():
            if k in ("id", "order_id", "user_id"):
                continue
            clean_v = str(v).replace("'", "").replace('"', "")
            facts.append(f"{model_name}_{k}('{entity_id}', '{clean_v}').")

        logger.info("Transformed Pydantic %s into %d Prolog facts.", model.__class__.__name__, len(facts))
        return facts

    @staticmethod
    def pydantic_to_z3_assertions(model: BaseModel) -> list[str]:
        """Map numeric fields of Pydantic model into Z3 SMT constraint assertions."""
        model_name = model.__class__.__name__.lower()
        data = model.model_dump()

        assertions: list[str] = []
        for k, v in data.items():
            if isinstance(v, (int, float)):
                assertions.append(f"(assert (>= {model_name}_{k} {v}))")

        logger.info("Transformed Pydantic %s into %d Z3 SMT assertions.", model.__class__.__name__, len(assertions))
        return assertions

    @staticmethod
    def triple_to_datalog(triple: OntologyTriple) -> str:
        """Map OntologyTriple into Datalog fact: predicate(subject, object)."""
        subj = triple.subject.lower().replace("-", "_")
        pred = triple.predicate.lower().replace("-", "_")
        obj = triple.object.lower().replace("-", "_")
        return f"{pred}({subj}, {obj})."

    @staticmethod
    def triple_to_prolog(triple: OntologyTriple) -> str:
        """Map OntologyTriple into Prolog fact: predicate('Subject', 'Object')."""
        clean_pred = triple.predicate.replace(":", "_").replace("-", "_")
        return f"{clean_pred}('{triple.subject}', '{triple.object}')."
