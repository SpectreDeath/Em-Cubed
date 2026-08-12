"""Ontology tool handlers: validate_triple, elicit_ontology, evaluate_topos,
extract_truthmakers, prove_zkp, check_health, run_monad.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from em_cubed.gateway.tool_registry import ToolRegistry

# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _handle_validate_triple(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.ontology.schema import OntologyTriple
    from em_cubed.ontology.validator import OntologyLedgerValidator

    triple = OntologyTriple(subject=args["subject"], predicate=args["predicate"], object=args["object"])
    validator = OntologyLedgerValidator()
    is_valid, msg = validator.validate_and_commit(triple)
    return {"valid": is_valid, "message": msg}


def _handle_elicit_ontology(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.ontology.elicitation import KnowledgeElicitationPipeline

    pipeline = KnowledgeElicitationPipeline()
    elicitation_report = pipeline.execute_pipeline(
        executive_prompt=args["prompt"],
        dsq_texts=["What is the supply risk?"],
        cq_texts=["Which suppliers provide Folic Acid?"],
    )
    formatted_triples = [
        {"subject": t.subject, "predicate": t.predicate, "object": t.object}
        for t in elicitation_report.triples
    ]
    return {"triples_count": len(elicitation_report.triples), "triples": formatted_triples}


def _handle_evaluate_topos(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.ontology.topos import SubobjectClassifier

    truth_val = SubobjectClassifier.evaluate_confidence(float(args["confidence"]))
    return {
        "confidence": truth_val.confidence,
        "modal_type": truth_val.modal_type.value,
        "satisfied": truth_val.is_satisfied(),
    }


def _handle_extract_truthmakers(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.ontology.schema import OntologyTriple
    from em_cubed.ontology.truthmaker import ExactTruthmakerClassifier

    t = OntologyTriple(subject=args["subject"], predicate="relatesTo", object=args["object"])
    tm = ExactTruthmakerClassifier.classify_exact_truthmaker(
        proposition=args["proposition"],
        state_triples=[t],
        relevant_predicates=["relatesTo"],
    )
    return {
        "proposition": tm.proposition,
        "is_satisfied": tm.is_satisfied,
        "ground_explanation": tm.ground_explanation,
    }


def _handle_prove_zkp(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.ontology.schema import OntologyTriple
    from em_cubed.ontology.zk_attestation import ZeroKnowledgeOntologyAttestor

    t = OntologyTriple(subject=args["subject"], predicate="relatesTo", object=args["object"])
    commitment = ZeroKnowledgeOntologyAttestor.generate_attestation(
        proposition=args["proposition"],
        state_triples=[t],
        relevant_predicates=["relatesTo"],
    )
    return {
        "proof_id": commitment.proof_id,
        "proposition_hash": commitment.proposition_hash,
        "merkle_state_root": commitment.merkle_state_root,
        "signature": commitment.signature,
    }


def _handle_check_health(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.ontology.health_monitor import OntologicalHealthMonitor

    health_report = OntologicalHealthMonitor.audit_health([])
    return {"coherence_index": health_report.coherence_index, "health_status": health_report.health_status}


def _handle_run_monad(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.ontology.schema import OntologyTriple
    from em_cubed.surfaces.functor import OntologyMonad, SurfaceFunctor

    t = OntologyTriple(subject=args["subject"], predicate=args["predicate"], object=args["object"])
    prolog_str = SurfaceFunctor.python_to_prolog([t])
    z3_str = SurfaceFunctor.prolog_to_z3(prolog_str)
    monad = OntologyMonad.unit(z3_str)
    return {"smt_lib": monad.extract(), "trace": monad.trace}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_all(registry: "ToolRegistry") -> None:
    """Register all ontology tool handlers with *registry*."""
    registry.register("em_cubed_validate_triple", _handle_validate_triple)
    registry.register("em_cubed_elicit_ontology", _handle_elicit_ontology)
    registry.register("em_cubed_evaluate_topos", _handle_evaluate_topos)
    registry.register("em_cubed_extract_truthmakers", _handle_extract_truthmakers)
    registry.register("em_cubed_prove_zkp", _handle_prove_zkp)
    registry.register("em_cubed_check_health", _handle_check_health)
    registry.register("em_cubed_run_monad", _handle_run_monad)
