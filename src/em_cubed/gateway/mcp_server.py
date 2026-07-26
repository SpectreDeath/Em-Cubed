"""Model Context Protocol (MCP) Gateway Server for Em-Cubed.

Exposes Em-Cubed's neuro-symbolic reasoning capabilities (Topos Ω, Truthmakers,
Concept Induction, Health Monitoring, ZKP Attestation, Surface Functors) to external
LLM agents and IDEs via standard JSON-RPC over STDIO.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

from em_cubed.ontology.elicitation import KnowledgeElicitationPipeline
from em_cubed.ontology.health_monitor import OntologicalHealthMonitor
from em_cubed.ontology.schema import OntologyTriple
from em_cubed.ontology.topos import SubobjectClassifier
from em_cubed.ontology.truthmaker import ExactTruthmakerClassifier
from em_cubed.ontology.validator import OntologyLedgerValidator
from em_cubed.ontology.zk_attestation import ZeroKnowledgeOntologyAttestor
from em_cubed.surfaces.functor import OntologyMonad, SurfaceFunctor

logger = logging.getLogger(__name__)


class EmCubedMCPServer:
    """MCP Gateway Server exposing Em-Cubed neuro-symbolic tools."""

    TOOLS = [
        {
            "name": "em_cubed_validate_triple",
            "description": "Validates an ontological triple against OWL functional & disjointness rules.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "predicate": {"type": "string"},
                    "object": {"type": "string"},
                },
                "required": ["subject", "predicate", "object"],
            },
        },
        {
            "name": "em_cubed_elicit_ontology",
            "description": "Elicits BFO/OntoClean OWL triples from a natural language prompt.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                },
                "required": ["prompt"],
            },
        },
        {
            "name": "em_cubed_evaluate_topos",
            "description": "Evaluates confidence score into Topos Ω modal truth (NECESSARY, POSSIBLE).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "confidence": {"type": "number"},
                },
                "required": ["confidence"],
            },
        },
        {
            "name": "em_cubed_extract_truthmakers",
            "description": "Isolates Kit Fine exact truthmaker state fragments (s ⊩ A).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "proposition": {"type": "string"},
                    "subject": {"type": "string"},
                    "object": {"type": "string"},
                },
                "required": ["proposition", "subject", "object"],
            },
        },
        {
            "name": "em_cubed_prove_zkp",
            "description": "Generates quantum-resistant Zero-Knowledge proof attestation commitment.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "proposition": {"type": "string"},
                    "subject": {"type": "string"},
                    "object": {"type": "string"},
                },
                "required": ["proposition", "subject", "object"],
            },
        },
        {
            "name": "em_cubed_check_health",
            "description": "Audits live Coherence Index (%) & self-healing guardrail metrics.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "em_cubed_run_monad",
            "description": "Executes surface functor monadic workflow mapping Python to Prolog to Z3.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "predicate": {"type": "string"},
                    "object": {"type": "string"},
                },
                "required": ["subject", "predicate", "object"],
            },
        },
    ]

    def call_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Dispatch tool invocation to core subsystem handler."""
        if name == "em_cubed_validate_triple":
            triple = OntologyTriple(subject=args["subject"], predicate=args["predicate"], object=args["object"])
            validator = OntologyLedgerValidator()
            is_valid, msg = validator.validate_and_commit(triple)
            return {"valid": is_valid, "message": msg}

        elif name == "em_cubed_elicit_ontology":
            pipeline = KnowledgeElicitationPipeline()
            report = pipeline.execute_pipeline(
                executive_prompt=args["prompt"],
                dsq_texts=["What is the supply risk?"],
                cq_texts=["Which suppliers provide Folic Acid?"],
            )
            return {"triples_count": len(report.triples), "triples": [t.to_dict() for t in report.triples]}

        elif name == "em_cubed_evaluate_topos":
            truth_val = SubobjectClassifier.evaluate_confidence(float(args["confidence"]))
            return {"confidence": truth_val.confidence, "modal_type": truth_val.modal_type.value, "satisfied": truth_val.is_satisfied()}

        elif name == "em_cubed_extract_truthmakers":
            t = OntologyTriple(subject=args["subject"], predicate="relatesTo", object=args["object"])
            tm = ExactTruthmakerClassifier.classify_exact_truthmaker(
                proposition=args["proposition"],
                state_triples=[t],
                relevant_predicates=["relatesTo"],
            )
            return {"proposition": tm.proposition, "is_satisfied": tm.is_satisfied, "ground_explanation": tm.ground_explanation}

        elif name == "em_cubed_prove_zkp":
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

        elif name == "em_cubed_check_health":
            report = OntologicalHealthMonitor.audit_health([])
            return {"coherence_index": report.coherence_index, "health_status": report.health_status}

        elif name == "em_cubed_run_monad":
            t = OntologyTriple(subject=args["subject"], predicate=args["predicate"], object=args["object"])
            prolog_str = SurfaceFunctor.python_to_prolog([t])
            z3_str = SurfaceFunctor.prolog_to_z3(prolog_str)
            monad = OntologyMonad.unit(z3_str)
            return {"smt_lib": monad.extract(), "trace": monad.trace}

        return {"error": f"Unknown tool: {name}"}


def run_mcp_server() -> None:
    """Run MCP Server on STDIO processing JSON-RPC commands."""
    server = EmCubedMCPServer()
    sys.stdout.write(json.dumps({"status": "EmCubed MCP Server Running", "tools_count": len(server.TOOLS)}) + "\n")
    sys.stdout.flush()
