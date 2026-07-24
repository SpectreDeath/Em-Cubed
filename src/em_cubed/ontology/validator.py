"""Neuro-Symbolic Ontology Ledger Validator.

Implements "Pydantic at the Door, Ontology at the Ledger":
- Step 1: Structural Pydantic/Type Validation
- Step 2: Ontological Logic Invariant Validation (Functional Properties, Disjoint Classes, Domain/Range Inferences)
"""

from __future__ import annotations

import logging
from typing import Any, Type

from pydantic import BaseModel, ValidationError

from em_cubed.ontology.schema import (
    DisjointClassConstraint,
    DomainRangeInference,
    FunctionalPropertyConstraint,
    OntologyTriple,
)

logger = logging.getLogger(__name__)


class OntologyLedgerValidator:
    """Validator enforcing structural and ontological constraints on agent state mutations."""

    def __init__(self) -> None:
        self.triples: list[OntologyTriple] = []
        self.entity_classes: dict[str, set[str]] = {}
        self.functional_constraints: list[FunctionalPropertyConstraint] = []
        self.disjoint_constraints: list[DisjointClassConstraint] = []
        self.domain_range_inferences: list[DomainRangeInference] = []

    def add_functional_property(self, predicate: str) -> None:
        """Register a functional property constraint (at most one value allowed per subject/predicate)."""
        self.functional_constraints.append(FunctionalPropertyConstraint(predicate=predicate))

    def add_disjoint_classes(self, class_a: str, class_b: str) -> None:
        """Register a disjoint class constraint."""
        self.disjoint_constraints.append(DisjointClassConstraint(class_a=class_a, class_b=class_b))

    def add_domain_range_inference(self, predicate: str, domain_class: str, range_class: str) -> None:
        """Register a domain/range inference rule."""
        self.domain_range_inferences.append(
            DomainRangeInference(predicate=predicate, domain_class=domain_class, range_class=range_class)
        )

    def validate_and_commit(
        self,
        new_triple: OntologyTriple,
        schema_model: Type[BaseModel] | None = None,
        raw_payload: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        """Validate payload structure and ontological constraints before committing to ledger.

        Parameters
        ----------
        new_triple : OntologyTriple
            Proposed state mutation triple.
        schema_model : Type[BaseModel] | None
            Optional Pydantic model for door validation.
        raw_payload : dict[str, Any] | None
            Payload dict to validate against schema_model.

        Returns
        -------
        tuple[bool, str]
            (is_valid, message)
        """
        # Step 1: Pydantic at the Door (Structural Validation)
        if schema_model and raw_payload is not None:
            try:
                schema_model.model_validate(raw_payload)
            except ValidationError as err:
                logger.warning("Door Schema Validation failed: %s", err)
                return False, f"Pydantic Door Schema Validation Failed: {err}"

        # Step 2: Ontology at the Ledger (Functional Property Checks)
        for f_constraint in self.functional_constraints:
            violation = f_constraint.check_violation(self.triples, new_triple)
            if violation:
                logger.warning("Ledger Validation Failed: %s", violation)
                return False, violation

        # Step 3: Domain & Range Inferences
        inferred_types: list[tuple[str, str]] = []
        for dr_inf in self.domain_range_inferences:
            inferred_types.extend(dr_inf.infer(new_triple))

        # Step 4: Disjoint Class Checks
        for entity_id, new_class in inferred_types:
            for dj_constraint in self.disjoint_constraints:
                violation = dj_constraint.check_violation(self.entity_classes, entity_id, new_class)
                if violation:
                    logger.warning("Ledger Validation Failed: %s", violation)
                    return False, violation

        # Commit Triple & Inferred Types
        self.triples.append(new_triple)
        for entity_id, new_class in inferred_types:
            if entity_id not in self.entity_classes:
                self.entity_classes[entity_id] = set()
            self.entity_classes[entity_id].add(new_class)

        logger.info("Ledger Validation Passed. Committed triple (%s, %s, %s).", new_triple.subject, new_triple.predicate, new_triple.object)
        return True, "Passed structural and ontological ledger validation."
