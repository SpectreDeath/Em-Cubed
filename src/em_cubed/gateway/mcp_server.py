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

from em_cubed.gateway.tool_registry import ToolRegistry
from em_cubed.gateway.tool_handlers import meta_handlers, ontology_handlers, skill_handlers, workflow_handlers

logger = logging.getLogger(__name__)


class EmCubedMCPServer:
    """MCP Gateway Server exposing Em-Cubed neuro-symbolic tools."""

    def __init__(self) -> None:
        self._registry = ToolRegistry()
        ontology_handlers.register_all(self._registry)
        skill_handlers.register_all(self._registry)
        workflow_handlers.register_all(self._registry)
        meta_handlers.register_all(self._registry)
        # Inject total tool count into the server_discover handler.
        meta_handlers.set_tools_count(len(self.TOOLS))

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
        {
            "name": "em_cubed_auto_chain",
            "description": "Synthesizes an optimal multi-surface skill execution DAG pipeline for a given goal.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string"},
                    "inputs": {"type": "object"},
                },
                "required": ["goal"],
            },
        },
        {
            "name": "em_cubed_server_discover",
            "description": "Exposes MCP 2026-07-28 stateless server capabilities, spec version, and routing header requirements.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "em_cubed_run_dag",
            "description": "Parses and executes a declarative YAML/JSON multi-surface workflow DAG pipeline.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dag_spec": {"type": "object"},
                    "workflow_id": {"type": "string"},
                },
                "required": ["dag_spec"],
            },
        },
        {
            "name": "em_cubed_check_dag_status",
            "description": "Polls durable execution status and checkpoint state of a running workflow DAG.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"},
                },
                "required": ["workflow_id"],
            },
        },
        {
            "name": "em_cubed_lock_skills",
            "description": "Generates or verifies cryptographic em3.lock lockfile signatures for registered skills.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "verify": {"type": "boolean"},
                },
            },
        },
    ]


    def call_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Dispatch tool invocation to the registered handler via ToolRegistry."""
        return self._registry.dispatch(name, args)


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
                        "protocolVersion": "2026-07-28",
                        "stateless": True,
                        "serverInfo": {
                            "name": "em-cubed",
                            "version": "0.8.0",
                        },
                        "capabilities": {"tools": {}, "stateless_transport": True},
                    },
                }
            )

        elif method == "serverDiscover":
            discover_res = server.call_tool("em_cubed_server_discover", {})
            _write_response(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": discover_res,
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
