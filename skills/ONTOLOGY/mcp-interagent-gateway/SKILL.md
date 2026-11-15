---
name: mcp-interagent-gateway
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
description: Model Context Protocol (MCP) JSON-RPC gateway server and inter-agent communication bus. Exposes core ontological OS tools (validate_triple, elicit_ontology, evaluate_topos, extract_truthmakers, prove_zkp, check_health, run_monad) over standard MCP STDIO/SSE transports to external LLM clients, IDEs, and subagents. Use when exposing ontology capabilities via Model Context Protocol, connecting external AI agents to Em-Cubed symbolic reasoners, or executing MCP tool dispatches.
purpose: Provide a standard Model Context Protocol (MCP) JSON-RPC gateway server exposing core ontological OS capabilities.
dependencies: []
tags:
  - mcp-server
  - model-context-protocol
  - json-rpc
  - inter-agent-bus
  - tool-dispatch
inputs:
  tool_name:
    type: string
    required: true
    description: Target MCP tool identifier (e.g. 'em_cubed_evaluate_topos', 'em_cubed_check_health').
  arguments:
    type: object
    required: true
    description: JSON argument payload adhering to the target tool's input schema.
outputs:
  content:
    type: array
    description: MCP standard content blocks containing tool execution results or error text.
  is_error:
    type: boolean
    description: True if tool execution encountered an unhandled exception or schema violation.
---

# MCP Inter-Agent Gateway Engine

`mcp-interagent-gateway` implements **Phase 23 Autonomous Multi-Agent Swarm MCP Gateway Server & Inter-Agent Bus** in `Em-Cubed`. It provides an enterprise Model Context Protocol (MCP) JSON-RPC server interface over standard STDIO/SSE transports, exposing 8 formal neurosymbolic reasoning tools directly to external IDEs, Claude Code, and autonomous subagent swarms.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage MCP Tool Dispatch Progression

```
[1. Request & Schema Audit] → [2. Tool Route Dispatch] → [3. Visual Brief] → [4. Checkpoint] → [5. Execution & MCP Response]
```

### Stage 1: Request & Schema Invariant Audit
1. Ingest JSON-RPC message and validate standard MCP protocol envelope:
   `{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": str, "arguments": dict}}`
2. Validate arguments against registered JSON Schema for requested tool.

> **Completion criterion**: JSON-RPC envelope and tool arguments validated.

---

### Stage 2: Tool Route & Surface Dispatch
1. Map tool request to target internal engine:
   - `em_cubed_validate_triple`: OWL ledger disjointness validator.
   - `em_cubed_elicit_ontology`: 6-stage PMEST knowledge elicitation.
   - `em_cubed_evaluate_topos`: Subobject Classifier $\Omega$ modal verifier.
   - `em_cubed_extract_truthmakers`: Kit Fine exact truthmaker classifier ($s \Vdash A$).
   - `em_cubed_prove_zkp`: Zero-Knowledge Merkle state root attestor.
   - `em_cubed_check_health`: Coherence Index and self-healing monitor.
   - `em_cubed_run_monad`: Surface functor monadic bind pipeline.

> **Completion criterion**: Request mapped to target engine with typed parameters.

---

### Stage 3: The Visual Brief
For multi-agent MCP tool choreography, generate an interactive brief:
- **Location**: Write to `%TEMP%\mcp-gateway-brief-<timestamp>.html` (Windows) or `/tmp/mcp-gateway-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render client-gateway-engine JSON-RPC sequence diagram and tool execution metrics.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing state-mutating MCP tools (e.g. `em_cubed_mutate_ontology`):
1. Verify client authorization token and execution sandbox boundaries.
2. Halt if destructive operations exceed client permission scopes.

> **Completion criterion**: Dispatch verified within client capability bounds.

---

### Stage 5: Execution & MCP Standard Response Emit
1. Execute engine logic and capture stdout/result telemetry.
2. Format output into standard MCP content block:
   ```json
   {
     "content": [{"type": "text", "text": "{\"status\": \"success\", \"result\": ...}"}],
     "isError": false
   }
   ```

> **Completion criterion**: Standard MCP JSON-RPC response returned to caller.

---

## Surface References

### Python MCP Server Surface

```python
from typing import Dict, Any

def dispatch_mcp_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "em_cubed_evaluate_topos":
        conf = args.get("confidence", 0.95)
        modal = "NECESSARY" if conf >= 0.90 else "POSSIBLE"
        return {
            "content": [{"type": "text", "text": f"Topos Omega evaluated: {modal} (Conf={conf})"}],
            "is_error": False
        }
    elif name == "em_cubed_check_health":
        return {
            "content": [{"type": "text", "text": "Coherence Index: 0.98 | Status: HEALTHY"}],
            "is_error": False
        }
    return {
        "content": [{"type": "text", "text": f"Tool '{name}' not found."}],
        "is_error": True
    }
```

---

## Anti-Patterns & Guardrails

- **Non-Standard MCP Envelopes** — Returning raw unstructured text or non-compliant JSON-RPC responses that crash MCP client runtimes.
- **Unbounded Tool Execution** — Allowing MCP tools to run long loops without timeout limits ($\le 30$ seconds).
- **Silent Exception Swallowing** — Catching exceptions and returning empty strings rather than setting `"isError": true` with diagnostic messages.
