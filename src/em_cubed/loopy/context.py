"""SurfaceExecutionContext Protocol for BaseLoopySkill dependency injection.

Defines the ``SurfaceExecutionContext`` runtime-checkable Protocol and the
``DefaultSurfaceExecutionContext`` concrete implementation.

Rationale
---------
``BaseLoopySkill`` previously imported 12+ ontology modules at the method level,
creating a hidden fan-out that made the loop engine impossible to test or reuse
without the full ontology stack. By expressing ontology operations as a Protocol,
the loop engine depends only on this interface. Concrete implementations (the
default, mocks, or alternative backends) are injected at construction time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, runtime_checkable

from typing import Protocol

if TYPE_CHECKING:
    from em_cubed.ontology.schema import OntologyTriple
    from em_cubed.ontology.topos import TruthValue
    from em_cubed.ontology.truthmaker import ExactTruthmaker


@runtime_checkable
class SurfaceExecutionContext(Protocol):
    """Protocol expressing all ontology operations needed by ``BaseLoopySkill``.

    Implementors only need to provide these methods. The loop engine (``run()``,
    ``verify_topos()``, etc.) calls through this interface, never importing
    the concrete ontology modules directly.
    """

    def classify_boolean(self, is_true: bool, message: str = "") -> "TruthValue":
        """Classify a boolean guard result into a Topos TruthValue (Omega)."""
        ...

    def classify_exact_truthmaker(
        self,
        proposition: str,
        state_triples: list[Any],
        relevant_predicates: list[str],
    ) -> "ExactTruthmaker":
        """Kit Fine's exact truthmaker: isolate minimal state fragments that make a proposition true."""
        ...

    def induce_concept(self, subclass_name: str, positive_samples: list[dict[str, Any]]) -> Any:
        """Pascal Hitzler's concept induction: synthesise a DL class expression from examples."""
        ...

    def compute_derived_property(
        self,
        triples: list[Any],
        subject: str,
        predicate: str,
        reducer_type: str,
    ) -> float | int:
        """Palantir reducer: compute a dynamic derived property over linked triples."""
        ...

    def verify_interface(
        self,
        triples: list[Any],
        subject: str,
        required_predicates: list[str],
    ) -> bool:
        """Palantir interface validation: check if a subject satisfies an OntologyInterface contract."""
        ...

    def migrate_triples(self, triples: list[Any], steps: list[Any]) -> list[Any]:
        """Schema evolution: migrate triples losslessly to a target schema version."""
        ...

    def audit_health(self, triples: list[Any]) -> Any:
        """Production health monitor: calculate coherence index and health metrics."""
        ...

    def snapshot_at(self, timeline: Any, timestamp: Any) -> list[Any]:
        """Temporal snapshot reasoner: return triples valid at a given timestamp."""
        ...

    def find_entities_within_radius(
        self, timeline: Any, lat: float, lon: float, radius_km: float
    ) -> list[tuple[str, float]]:
        """Spatial proximity reasoner: find entities within radius_km of (lat, lon)."""
        ...

    def to_turtle(self, triples: list[Any]) -> str:
        """W3C RDF serialiser: convert triples to RDF Turtle (.ttl) syntax."""
        ...

    def generate_shacl_shapes(self, functional_constraints: list[Any]) -> str:
        """W3C SHACL export: serialise functional property constraints to SHACL shapes."""
        ...

    def process_stream_batch(self, events: list[Any]) -> Any:
        """Reactive event stream: ingest and evaluate a batch of streaming events."""
        ...

    def generate_attestation(
        self,
        proposition: str,
        state_triples: list[Any],
        relevant_predicates: list[str],
    ) -> Any:
        """ZKP: generate a zero-knowledge cryptographic commitment over state triples."""
        ...

    def verify_commitment(self, commitment: Any) -> Any:
        """ZKP: verify a zero-knowledge cryptographic proof payload."""
        ...

    def apply_functor(self, triples: list[Any], target_surface: str = "prolog") -> str:
        """Category-theoretic surface functor: map triples to a target surface language."""
        ...

    def bind_monad(self, state: Any, fn: Any) -> Any:
        """Monadic bind (>>=): execute a monadic computation on loopy skill state."""
        ...


class DefaultSurfaceExecutionContext:
    """Concrete ``SurfaceExecutionContext`` backed by the real ontology subsystem.

    This is the production default injected by ``BaseLoopySkill`` when no
    custom context is supplied. All 12+ ontology imports that previously lived
    inside individual ``BaseLoopySkill`` method bodies are centralised here.
    """

    # -----------------------------------------------------------------
    # Topos
    # -----------------------------------------------------------------
    def classify_boolean(self, is_true: bool, message: str = "") -> "TruthValue":
        from em_cubed.ontology.topos import SubobjectClassifier
        return SubobjectClassifier.classify_boolean(is_true, message)

    # -----------------------------------------------------------------
    # Truthmaker
    # -----------------------------------------------------------------
    def classify_exact_truthmaker(
        self,
        proposition: str,
        state_triples: list[Any],
        relevant_predicates: list[str],
    ) -> "ExactTruthmaker":
        from em_cubed.ontology.truthmaker import ExactTruthmakerClassifier
        return ExactTruthmakerClassifier.classify_exact_truthmaker(
            proposition=proposition,
            state_triples=state_triples,
            relevant_predicates=relevant_predicates,
        )

    # -----------------------------------------------------------------
    # Concept Induction
    # -----------------------------------------------------------------
    def induce_concept(self, subclass_name: str, positive_samples: list[dict[str, Any]]) -> Any:
        from em_cubed.ontology.concept_induction import ConceptInductionEngine
        return ConceptInductionEngine.induce_concept(
            subclass_name=subclass_name, positive_samples=positive_samples
        )

    # -----------------------------------------------------------------
    # Advanced Ontology (Derived Properties)
    # -----------------------------------------------------------------
    def compute_derived_property(
        self,
        triples: list[Any],
        subject: str,
        predicate: str,
        reducer_type: str,
    ) -> float | int:
        from em_cubed.ontology.advanced_ontology import DerivedPropertyReducer, ReducerType
        return DerivedPropertyReducer.compute_reducer(
            triples=triples,
            subject=subject,
            predicate=predicate,
            reducer_type=ReducerType(reducer_type),
        )

    # -----------------------------------------------------------------
    # Advanced Ontology (Interface Validation)
    # -----------------------------------------------------------------
    def verify_interface(
        self,
        triples: list[Any],
        subject: str,
        required_predicates: list[str],
    ) -> bool:
        from em_cubed.ontology.advanced_ontology import InterfaceImplementation, OntologyInterface
        interface = OntologyInterface(
            name="SkillStateInterface", required_predicates=required_predicates
        )
        return InterfaceImplementation.validates_interface(
            triples=triples, subject=subject, interface=interface
        )

    # -----------------------------------------------------------------
    # Schema Evolution
    # -----------------------------------------------------------------
    def migrate_triples(self, triples: list[Any], steps: list[Any]) -> list[Any]:
        from em_cubed.ontology.schema_evolution import AutomatedTripleMigrationEngine
        return AutomatedTripleMigrationEngine.migrate_triples(triples=triples, steps=steps)

    # -----------------------------------------------------------------
    # Health Monitor
    # -----------------------------------------------------------------
    def audit_health(self, triples: list[Any]) -> Any:
        from em_cubed.ontology.health_monitor import OntologicalHealthMonitor
        return OntologicalHealthMonitor.audit_health(triples=triples)

    # -----------------------------------------------------------------
    # Temporal / Spatial
    # -----------------------------------------------------------------
    def snapshot_at(self, timeline: Any, timestamp: Any) -> list[Any]:
        from em_cubed.ontology.temporal_spatial import TemporalSnapshotQueryEngine
        return TemporalSnapshotQueryEngine.snapshot_at(timeline=timeline, timestamp=timestamp)

    def find_entities_within_radius(
        self, timeline: Any, lat: float, lon: float, radius_km: float
    ) -> list[tuple[str, float]]:
        from em_cubed.ontology.temporal_spatial import GeoLocation, SpatialProximityReasoner
        center = GeoLocation(latitude=lat, longitude=lon)
        return SpatialProximityReasoner.find_entities_within_radius(
            timeline=timeline, center=center, radius_km=radius_km
        )

    # -----------------------------------------------------------------
    # Interoperability
    # -----------------------------------------------------------------
    def to_turtle(self, triples: list[Any]) -> str:
        from em_cubed.ontology.interoperability import RDFSerializer
        return RDFSerializer.to_turtle(triples=triples)

    def generate_shacl_shapes(self, functional_constraints: list[Any]) -> str:
        from em_cubed.ontology.interoperability import SHACLConstraintGenerator
        return SHACLConstraintGenerator.generate_shacl_shapes(functional_constraints)

    # -----------------------------------------------------------------
    # Event Stream
    # -----------------------------------------------------------------
    def process_stream_batch(self, events: list[Any]) -> Any:
        from em_cubed.ontology.event_stream import OntologyEventStreamProcessor
        processor = OntologyEventStreamProcessor()
        return processor.process_stream_batch(events)

    # -----------------------------------------------------------------
    # ZK Attestation
    # -----------------------------------------------------------------
    def generate_attestation(
        self,
        proposition: str,
        state_triples: list[Any],
        relevant_predicates: list[str],
    ) -> Any:
        from em_cubed.ontology.zk_attestation import ZeroKnowledgeOntologyAttestor
        return ZeroKnowledgeOntologyAttestor.generate_attestation(
            proposition=proposition,
            state_triples=state_triples,
            relevant_predicates=relevant_predicates,
        )

    def verify_commitment(self, commitment: Any) -> Any:
        from em_cubed.ontology.zk_attestation import ZKPAuditor
        return ZKPAuditor.verify_commitment(commitment)

    # -----------------------------------------------------------------
    # Surface Functor / Monad
    # -----------------------------------------------------------------
    def apply_functor(self, triples: list[Any], target_surface: str = "prolog") -> str:
        from em_cubed.surfaces.functor import SurfaceFunctor
        if target_surface.lower() == "prolog":
            return SurfaceFunctor.python_to_prolog(triples)
        elif target_surface.lower() == "z3":
            prolog_str = SurfaceFunctor.python_to_prolog(triples)
            return SurfaceFunctor.prolog_to_z3(prolog_str)
        return ""

    def bind_monad(self, state: Any, fn: Any) -> Any:
        from em_cubed.surfaces.functor import OntologyMonad
        monad = OntologyMonad.unit(state)
        return monad.bind(fn).extract()
