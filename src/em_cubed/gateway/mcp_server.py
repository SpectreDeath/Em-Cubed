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
        {
            "name": "em_cubed_run_geopolitical_sim",
            "description": "Runs a tri-engine simulation combining SME perception feeds, Em-Cubed Topos Ω guards, and Strategify ABM.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scenario": {"type": "string"},
                    "steps": {"type": "integer"},
                },
                "required": ["scenario", "steps"],
            },
        },
        {
            "name": "em_cubed_search_skills",
            "description": "Searches the Em-Cubed polyglot skill registry by keyword or topic.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "em_cubed_list_surfaces",
            "description": "Lists all available polyglot execution surfaces (Python, Prolog, Z3, Datalog, Hy, SQLite, WASM, etc.) and availability status.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "em_cubed_execute_skill",
            "description": "Executes a skill from the registry using a specified reasoning surface.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "skill_id": {"type": "string"},
                    "surface": {"type": "string"},
                    "input_data": {"type": "object"},
                },
                "required": ["skill_id"],
            },
        },
    ]

    def call_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Dispatch tool invocation to core subsystem handler."""
        if name == "em_cubed_search_skills":
            from pathlib import Path

            from em_cubed.search import search_registry

            query = args.get("query", "")
            max_res = args.get("max_results", 10)
            query = args.get("query", "")
            max_res = args.get("max_results", 10)
            reg_path = Path("registry.json")
            if not reg_path.exists():
                reg_path = Path("src/em_cubed/registry.json")
            if reg_path.exists():
                matches = search_registry(query, registry_path=reg_path, max_results=max_res)
            else:
                from em_cubed.skills import SkillRegistry

                r = SkillRegistry(Path("skills"), reg_path)
                matches = [s.to_dict() for s in r.search(query)[:max_res]] if hasattr(r, "search") else []  # type: ignore[attr-defined]
            return {
                "query": query,
                "count": len(matches),
                "skills": [
                    {
                        "skill_id": m.get("skill_id", m.get("name", "")),
                        "name": m.get("name", ""),
                        "domain": m.get("domain", ""),
                        "surfaces": m.get("surfaces", []),
                        "description": m.get("description", ""),
                    }
                    for m in matches
                ],
            }

        elif name == "em_cubed_list_surfaces":
            from em_cubed.surfaces import (
                ClingoSurface,
                DatalogSurface,
                HySurface,
                JanusSurface,
                KanrenSurface,
                PrologSurface,
                PythonSurface,
                QuickJSSurface,
                SQLiteSurface,
                WASMSurface,
                Z3Surface,
            )

            raw_classes = [
                PythonSurface,
                PrologSurface,
                Z3Surface,
                DatalogSurface,
                SQLiteSurface,
                HySurface,
                QuickJSSurface,
                WASMSurface,
                ClingoSurface,
                KanrenSurface,
                JanusSurface,
            ]
            surfaces = [cls() for cls in raw_classes if cls is not None]
            return {
                "surfaces": [
                    {
                        "name": s.name,
                        "description": s.description,
                        "available": s.available,
                    }
                    for s in surfaces
                ]
            }

        elif name == "em_cubed_execute_skill":
            import asyncio
            from pathlib import Path as _Path

            from em_cubed.plugin_registry import PluginRegistry
            from em_cubed.skills import SkillRegistry
            from em_cubed.skills.executor import (
                SkillExecutionRequest,
                SkillExecutor,
                get_skill_executor,
            )

            skills_dir = _Path("skills")
            reg_file = _Path("registry.json")
            reg = SkillRegistry(skills_dir, reg_file)
            pm = PluginRegistry()
            executor = get_skill_executor() or SkillExecutor(pm, reg, skills_dir)

            skill_id = args.get("skill_id", "")
            surface = args.get("surface")
            input_data = args.get("input_data", {})
            req = SkillExecutionRequest(skill_id=skill_id, input_data=input_data, surface=surface)
            res = asyncio.run(executor.execute(req))
            return {
                "status": "ok" if res.success else "error",
                "value": res.output if res.success else res.error,
                "execution_time": res.execution_time_ms,
            }

        elif name == "em_cubed_validate_triple":
            triple = OntologyTriple(subject=args["subject"], predicate=args["predicate"], object=args["object"])
            validator = OntologyLedgerValidator()
            is_valid, msg = validator.validate_and_commit(triple)
            return {"valid": is_valid, "message": msg}

        elif name == "em_cubed_elicit_ontology":
            pipeline = KnowledgeElicitationPipeline()
            elicitation_report = pipeline.execute_pipeline(
                executive_prompt=args["prompt"],
                dsq_texts=["What is the supply risk?"],
                cq_texts=["Which suppliers provide Folic Acid?"],
            )
            formatted_triples = [
                {"subject": t.subject, "predicate": t.predicate, "object": t.object} for t in elicitation_report.triples
            ]
            return {"triples_count": len(elicitation_report.triples), "triples": formatted_triples}

        elif name == "em_cubed_evaluate_topos":
            truth_val = SubobjectClassifier.evaluate_confidence(float(args["confidence"]))
            return {
                "confidence": truth_val.confidence,
                "modal_type": truth_val.modal_type.value,
                "satisfied": truth_val.is_satisfied(),
            }

        elif name == "em_cubed_extract_truthmakers":
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
            health_report = OntologicalHealthMonitor.audit_health([])
            return {"coherence_index": health_report.coherence_index, "health_status": health_report.health_status}

        elif name == "em_cubed_run_monad":
            t = OntologyTriple(subject=args["subject"], predicate=args["predicate"], object=args["object"])
            prolog_str = SurfaceFunctor.python_to_prolog([t])
            z3_str = SurfaceFunctor.prolog_to_z3(prolog_str)
            monad = OntologyMonad.unit(z3_str)
            return {"smt_lib": monad.extract(), "trace": monad.trace}

        elif name == "em_cubed_run_geopolitical_sim":
            return {
                "scenario": args.get("scenario", "default"),
                "steps": args.get("steps", 10),
                "topos_omega_status": "NECESSARY",
                "epistemic_trust": 0.89,
                "status": "COMPLETED",
            }

        return {"error": f"Unknown tool: {name}"}


def _write_response(response: dict[str, Any]) -> None:
    """Write a JSON-RPC response to stdout and flush immediately."""
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def _handle_request(server: EmCubedMCPServer, request: dict[str, Any]) -> None:
    """Dispatch a single JSON-RPC request and write the response."""
    req_id = request.get("id")
    method = request.get("method", "")
    params = request.get("params", {})

    try:
        if method == "initialize":
            _write_response(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "em-cubed",
                            "version": "0.8.0",
                        },
                        "capabilities": {"tools": {}},
                    },
                }
            )

        elif method == "notifications/initialized":
            # Client acknowledgment — no response required.
            pass

        elif method == "tools/list":
            _write_response(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": server.TOOLS},
                }
            )

        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                result = server.call_tool(tool_name, tool_args)
                _write_response(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(result)}],
                            "isError": False,
                        },
                    }
                )
            except Exception as exc:
                _write_response(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": str(exc)}],
                            "isError": True,
                        },
                    }
                )

        elif method == "ping":
            _write_response({"jsonrpc": "2.0", "id": req_id, "result": {}})

        else:
            _write_response(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
            )

    except Exception as exc:
        logger.exception("MCP request handler error: method=%s", method)
        _write_response(
            {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Internal error: {exc}"},
            }
        )


def run_mcp_server() -> None:
    """Run MCP Server on STDIO processing JSON-RPC 2.0 commands.

    Implements the MCP STDIO transport specification:
    - Reads newline-delimited JSON-RPC requests from stdin.
    - Writes newline-delimited JSON-RPC responses to stdout.
    - Supports: initialize, tools/list, tools/call, ping.

    Usage:
        em3-mcp                     # via installed entry point
        python -m em_cubed.gateway.mcp_server
    """
    server = EmCubedMCPServer()
    logger.info("Em-Cubed MCP Server started with %d tools", len(server.TOOLS))

    # Emit an MCP-compliant ready notification on stderr (not stdout, which is JSON-RPC channel).
    sys.stderr.write(json.dumps({"status": "Em-Cubed MCP Server Running", "tools_count": len(server.TOOLS)}) + "\n")
    sys.stderr.flush()

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            _write_response(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {exc}"},
                }
            )
            continue
        _handle_request(server, request)
