"""Constraint-Aware Prompt Steering Compiler.

Compiles formal OWL/RDFS ontology constraints (Functional Properties, Disjoint Classes, Domain/Range Rules)
into system prompt instructions and Pydantic schema validation hints for LLMs.
"""

from __future__ import annotations

import logging

from em_cubed.ontology.schema import (
    DisjointClassConstraint,
    DomainRangeInference,
    FunctionalPropertyConstraint,
)

logger = logging.getLogger(__name__)


class ConstraintSteeringCompiler:
    """Compiler converting formal ontological constraints into LLM steering directives."""

    def __init__(
        self,
        functional_constraints: list[FunctionalPropertyConstraint] | None = None,
        disjoint_constraints: list[DisjointClassConstraint] | None = None,
        domain_range_inferences: list[DomainRangeInference] | None = None,
    ) -> None:
        self.functional_constraints = functional_constraints or []
        self.disjoint_constraints = disjoint_constraints or []
        self.domain_range_inferences = domain_range_inferences or []

    def compile_system_instructions(self) -> str:
        """Compile constraints into a system prompt instruction section."""
        instructions: list[str] = [
            "CRITICAL ONTOLOGY CONSTRAINT DIRECTIVES:",
            "You MUST strictly adhere to the following domain logic invariants. Any violation will be rejected by the ledger validator:",
        ]

        if self.functional_constraints:
            instructions.append("\n1. FUNCTIONAL PROPERTY UNIQUENESS (SINGLE-VALUE CONSTRAINTS):")
            for fc in self.functional_constraints:
                instructions.append(
                    f"   - Predicate '{fc.predicate}' is single-valued per subject. Never assign duplicate values."
                )

        if self.disjoint_constraints:
            instructions.append("\n2. DISJOINT CLASS BOUNDARIES:")
            for dc in self.disjoint_constraints:
                instructions.append(
                    f"   - Entity cannot simultaneously belong to '{dc.class_a}' and '{dc.class_b}'. Roles are disjoint."
                )

        if self.domain_range_inferences:
            instructions.append("\n3. DOMAIN & RANGE INFERENCES:")
            for dr in self.domain_range_inferences:
                instructions.append(
                    f"   - Predicate '{dr.predicate}' implies Subject MUST be class '{dr.domain_class}' and Object MUST be class '{dr.range_class}'."
                )

        return "\n".join(instructions)
