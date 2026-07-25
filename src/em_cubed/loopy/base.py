"""Base Loopy Skill Contract and Trajectory Data Structures.

Defines the universal loopy skill interface, trajectory logging, and execution result containers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from em_cubed.ontology.topos import SubobjectClassifier, TruthValue
from em_cubed.ontology.validator import OntologyLedgerValidator

logger = logging.getLogger(__name__)

T_State = TypeVar("T_State")
T_Result = TypeVar("T_Result")


@dataclass
class LoopTrajectory:
    """Represents a single step iteration within a loopy skill execution."""

    iteration: int
    action_taken: str
    observation: str
    passed_guard: bool
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopySkillResult(Generic[T_Result]):
    """Outcome of a loopy skill execution containing output and full trajectory."""

    success: bool
    final_output: T_Result
    trajectory: list[LoopTrajectory] = field(default_factory=list)
    error_message: str | None = None


class BaseLoopySkill(Generic[T_State, T_Result]):
    """Abstract base class for iterative, self-correcting loopy skills.

    Parameters
    ----------
    max_iterations : int
        Maximum number of retry iterations allowed before hitting safety limit.
    ledger_validator : OntologyLedgerValidator | None
        Optional validator for ontology-backed state transitions.
    """

    def __init__(
        self, max_iterations: int = 5, ledger_validator: OntologyLedgerValidator | None = None
    ) -> None:
        self.max_iterations = max_iterations
        self.ledger_validator = ledger_validator or OntologyLedgerValidator()

    def initialize_state(self, *args: Any, **kwargs: Any) -> T_State:
        """Set up initial skill state variables, code trees, or query environments."""
        raise NotImplementedError

    def mutate(self, state: T_State, iteration: int) -> tuple[T_State, str]:
        """Execute the action step (e.g., call micro-LLM, run code patch, query solver).

        Returns
        -------
        tuple[T_State, str]
            Updated state and description of action taken.
        """
        raise NotImplementedError

    def verify(self, state: T_State) -> tuple[bool, str]:
        """The Sensor: Deterministic check (e.g. pytest exit code, linter pass, regex match, ontology check).

        Returns
        -------
        tuple[bool, str]
            (passed_guard, observation_message)
        """
        raise NotImplementedError

    def verify_topos(self, state: T_State) -> TruthValue:
        """The Topos Subobject Classifier Sensor: Evaluates state against Omega truth object.

        Returns
        -------
        TruthValue
            Topos TruthValue object.
        """
        passed, obs = self.verify(state)
        return SubobjectClassifier.classify_boolean(passed, obs)

    def verify_truthmaker(self, state: T_State, proposition: str, relevant_predicates: list[str]) -> ExactTruthmaker:
        """Kit Fine's Truthmaker Sensor: Isolates exact truthmaker (s ⊩ A) and falsemaker.

        Returns
        -------
        ExactTruthmaker
            Exact truthmaker valuation.
        """
        from em_cubed.ontology.truthmaker import ExactTruthmakerClassifier
        return ExactTruthmakerClassifier.classify_exact_truthmaker(
            proposition=proposition,
            state_triples=getattr(state, "triples", []),
            relevant_predicates=relevant_predicates,
        )

    def induce_concept_from_trajectory(self, subclass_name: str, state: T_State) -> Any:
        """Pascal Hitzler's Concept Induction: Induces DL class expression from skill state.

        Returns
        -------
        DescriptionLogicExpression
            Synthesized DL class expression.
        """
        from em_cubed.ontology.concept_induction import ConceptInductionEngine
        sample = {"type": "LoopyState", "property": "has_state", "target": str(type(state).__name__)}
        return ConceptInductionEngine.induce_concept(subclass_name=subclass_name, positive_samples=[sample])

    def compute_derived_property(
        self,
        state: T_State,
        subject: str,
        predicate: str,
        reducer_type: str = "SUM",
    ) -> float | int:
        """Landon Carter's Palantir Reducer: Computes dynamic derived property value over linked triples.

        Returns
        -------
        float | int
            Calculated dynamic derived property value.
        """
        from em_cubed.ontology.advanced_ontology import DerivedPropertyReducer, ReducerType
        return DerivedPropertyReducer.compute_reducer(
            triples=getattr(state, "triples", []),
            subject=subject,
            predicate=predicate,
            reducer_type=ReducerType(reducer_type),
        )

    def verify_interface(self, state: T_State, subject: str, required_predicates: list[str]) -> bool:
        """Palantir Interface Validation: Verifies if subject satisfies abstract OntologyInterface contract.

        Returns
        -------
        bool
            True if interface contract is valid.
        """
        from em_cubed.ontology.advanced_ontology import InterfaceImplementation, OntologyInterface
        interface = OntologyInterface(name="SkillStateInterface", required_predicates=required_predicates)
        return InterfaceImplementation.validates_interface(
            triples=getattr(state, "triples", []),
            subject=subject,
            interface=interface,
        )

    def migrate_state_schema(self, state: T_State, target_version_str: str, steps: list[Any]) -> list[Any]:
        """Schema Evolution: Migrates skill state triples losslessly to target schema version.

        Returns
        -------
        list[OntologyTriple]
            Migrated triples list.
        """
        from em_cubed.ontology.schema_evolution import AutomatedTripleMigrationEngine
        return AutomatedTripleMigrationEngine.migrate_triples(
            triples=getattr(state, "triples", []),
            steps=steps,
        )

    def audit_ontological_health(self, state: T_State) -> Any:
        """Production Health Monitor: Calculates real-time coherence index and health metrics.

        Returns
        -------
        OntologyHealthReport
            Health metrics report.
        """
        from em_cubed.ontology.health_monitor import OntologicalHealthMonitor
        return OntologicalHealthMonitor.audit_health(triples=getattr(state, "triples", []))

    def query_temporal_snapshot(self, timeline: Any, timestamp: Any) -> list[Any]:
        """Temporal Snapshot Reasoner: Filters state triples valid at timestamp t.

        Returns
        -------
        list[OntologyTriple]
            Valid base triples list at timestamp t.
        """
        from em_cubed.ontology.temporal_spatial import TemporalSnapshotQueryEngine
        return TemporalSnapshotQueryEngine.snapshot_at(timeline=timeline, timestamp=timestamp)

    def evaluate_spatial_proximity(self, timeline: Any, lat: float, lon: float, radius_km: float) -> list[tuple[str, float]]:
        """Spatial Proximity Reasoner: Finds entities within radius_km of (lat, lon).

        Returns
        -------
        list[tuple[str, float]]
            Matching (subject, distance_km) list.
        """
        from em_cubed.ontology.temporal_spatial import GeoLocation, SpatialProximityReasoner
        center = GeoLocation(latitude=lat, longitude=lon)
        return SpatialProximityReasoner.find_entities_within_radius(timeline=timeline, center=center, radius_km=radius_km)

    def export_rdf_turtle(self, state: T_State) -> str:
        """W3C RDF Export: Serializes skill state triples to RDF Turtle (.ttl) syntax.

        Returns
        -------
        str
            Serialized Turtle text.
        """
        from em_cubed.ontology.interoperability import RDFSerializer
        return RDFSerializer.to_turtle(triples=getattr(state, "triples", []))

    def export_shacl_shapes(self) -> str:
        """W3C SHACL Export: Serializes functional property constraints to SHACL shapes.

        Returns
        -------
        str
            Serialized SHACL shapes Turtle text.
        """
        from em_cubed.ontology.interoperability import SHACLConstraintGenerator
        return SHACLConstraintGenerator.generate_shacl_shapes(self.ledger_validator.functional_constraints)

    def extract_result(self, state: T_State) -> T_Result:
        """Extract final output payload from completed state."""
        raise NotImplementedError

    def run(self, *args: Any, **kwargs: Any) -> LoopySkillResult[T_Result]:
        """Execute the core loop engine until guard passes or max_iterations is reached."""
        state = self.initialize_state(*args, **kwargs)
        trajectory: list[LoopTrajectory] = []

        logger.info("Starting Loopy Skill execution (max_iterations=%d)...", self.max_iterations)

        for i in range(1, self.max_iterations + 1):
            state, action_desc = self.mutate(state, i)

            # Evaluate against Topos Subobject Classifier
            truth_val = self.verify_topos(state)
            passed = truth_val.is_satisfied()
            observation = "; ".join(truth_val.evidence) if truth_val.evidence else f"Confidence: {truth_val.confidence:.2f}"

            trajectory.append(
                LoopTrajectory(
                    iteration=i,
                    action_taken=action_desc,
                    observation=observation,
                    passed_guard=passed,
                    metrics={"confidence": truth_val.confidence, "modal_type": truth_val.modal_type.value},
                )
            )

            if passed:
                logger.info("Loopy Skill passed verification guard on iteration %d.", i)
                return LoopySkillResult(
                    success=True,
                    final_output=self.extract_result(state),
                    trajectory=trajectory,
                )

        logger.warning("Loopy Skill reached max iterations (%d) without passing guard.", self.max_iterations)
        return LoopySkillResult(
            success=False,
            final_output=self.extract_result(state),
            trajectory=trajectory,
            error_message=f"Hit max iterations ({self.max_iterations}) without passing guard.",
        )
