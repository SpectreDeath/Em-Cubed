"""SHACL Shape Ontology State Validator for Em-Cubed Neuro-Symbolic OS.

Validates BFO / OntoClean triple graphs against SHACL shape definitions
to ensure ontological consistency before executing logic surface skills.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationReport:
    """SHACL Validation Report outcome."""

    conforms: bool
    violation_count: int
    violations: list[dict[str, Any]]


class SHACLValidator:
    """Validator for checking triple graphs against SHACL constraints."""

    def __init__(self, shape_graph: list[dict[str, Any]] | None = None):
        self.shape_graph = shape_graph or self._default_shapes()

    def _default_shapes(self) -> list[dict[str, Any]]:
        """Return baseline SHACL shapes for BFO / OntoClean entities."""
        return [
            {
                "targetClass": "bfo:IndependentContinuant",
                "property": "bfo:exists_in",
                "minCount": 1,
            },
            {
                "targetClass": "bfo:Process",
                "property": "bfo:has_participant",
                "minCount": 1,
            },
        ]

    def validate(self, data_graph: list[dict[str, Any]]) -> ValidationReport:
        """Validate triple graph data against configured SHACL shapes.

        Args:
            data_graph: List of triple dictionaries, e.g.
                        [{"subject": "A", "predicate": "bfo:exists_in", "object": "TimePoint"}]

        Returns:
            ValidationReport detailing conformance and violations.
        """
        violations: list[dict[str, Any]] = []

        # Map predicates present per subject
        predicates_by_subject: dict[str, set] = {}
        types_by_subject: dict[str, str] = {}

        for triple in data_graph:
            subj = triple.get("subject", "")
            pred = triple.get("predicate", "")
            obj = triple.get("object", "")

            if pred == "rdf:type":
                types_by_subject[subj] = obj
            else:
                if subj not in predicates_by_subject:
                    predicates_by_subject[subj] = set()
                predicates_by_subject[subj].add(pred)

        for shape in self.shape_graph:
            target_cls = shape.get("targetClass")
            required_pred = shape.get("property")
            min_count = shape.get("minCount", 1)

            for subj, entity_type in types_by_subject.items():
                if entity_type == target_cls:
                    subj_preds = predicates_by_subject.get(subj, set())
                    if required_pred not in subj_preds and min_count > 0:
                        violations.append({
                            "focusNode": subj,
                            "resultSeverity": "sh:Violation",
                            "sourceConstraintComponent": "sh:MinCountConstraintComponent",
                            "message": f"Entity '{subj}' of type '{target_cls}' is missing required property '{required_pred}'",
                        })

        conforms = len(violations) == 0
        return ValidationReport(
            conforms=conforms,
            violation_count=len(violations),
            violations=violations,
        )
