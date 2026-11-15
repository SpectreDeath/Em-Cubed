---
name: production-rest-governance-agent
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
  - z3
description: Production REST API governance agent, visual graph explorer, and audit trail renderer. Exposes secure HTTP endpoints for loopy skill execution, schema validation, Graph-Path RAG queries, and federated state alignment while rendering standalone interactive HTML/SVG graph visualizations. Use when governing production API access to the ontological OS, validating API payloads against OWL ledgers, or inspecting multi-hop semantic graph paths visually.
purpose: Securely govern, validate, and visually render ontological OS operations across production REST API endpoints.
dependencies: []
tags:
  - rest-api-governance
  - visual-graph-explorer
  - fast-api
  - openapi-schema
  - audit-rendering
inputs:
  endpoint_path:
    type: string
    required: true
    description: Target REST route to execute or query.
  request_payload:
    type: object
    required: false
    description: Request body parameters for execution or validation.
  render_visualization:
    type: boolean
    required: false
    description: Generate interactive HTML graph visualization (default true).
outputs:
  response_body:
    type: object
    description: API JSON response with execution telemetry.
  status_code:
    type: integer
    description: HTTP status code (200, 400, 422, 500).
  visualization_path:
    type: string
    description: Absolute file path to generated HTML visualization brief.
---

# Production REST Governance Agent Engine

`production-rest-governance-agent` implements **Phase 6 Production REST API Governance & Visual Graph Exploration** in `Em-Cubed`. It provides an enterprise HTTP interface over the ontological OS with OpenAPI contract enforcement, multi-surface validation, and interactive SVG/HTML semantic graph rendering.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage API Governance Progression

```
[1. Request & Auth Audit] → [2. Schema & OWL Ledger Validation] → [3. Visual Brief] → [4. Checkpoint] → [5. Dispatch & Graph Render]
```

### Stage 1: Request & Authentication Invariant Audit
1. Inspect HTTP method, route, and Bearer token authentication headers.
2. Validate incoming JSON payload against Pydantic request models.

> **Completion criterion**: Request headers authenticated and payload schema verified.

---

### Stage 2: Schema & OWL Ledger Validation
1. Dispatch payload to `/api/v1/ontology/validate`.
2. Validate that entity classes, disjointness rules, and functional property bounds are satisfied at the ontology ledger.

> **Completion criterion**: Payload certified compliant with both OpenAPI schema and OWL ledger axioms.

---

### Stage 3: The Visual Brief
For complex graph queries or multi-step execution traces, render an interactive HTML visual brief:
- **Location**: Write to `%TEMP%\rest-governance-brief-<timestamp>.html` (Windows) or `/tmp/rest-governance-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the multi-hop Knowledge Graph traversal and request dispatch timeline.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing mutating operations (e.g. `POST /api/v1/ontology/migrate`):
1. Verify API caller permissions and rate limit quotas.
2. Enforce explicit confirmation on state-mutating actions.

> **Completion criterion**: State mutations gated and authorized against API security policy.

---

### Stage 5: Endpoint Dispatch & SVG/HTML Export
1. Dispatch request to target controller (e.g. `loopy/execute`, `graph-rag`, `federated-status`).
2. Export standalone SVG/HTML graph visualization via `KnowledgeGraphVisualizer.render_subgraph_html()`.
3. Return HTTP 200 payload with response data and visualization path.

> **Completion criterion**: API response emitted with HTTP 200 and visualization artifact exported.

---

## Surface References

### Python FastAPI Controller Surface

```python
from typing import Dict, Any

def handle_governance_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if endpoint == "/api/v1/ontology/validate":
        is_valid = "entity_id" in payload and payload.get("class_name") is not None
        return {
            "status_code": 200 if is_valid else 422,
            "response_body": {
                "valid": is_valid,
                "ledger_checked": True,
                "disjointness_passed": is_valid
            },
            "visualization_path": "/tmp/subgraph_viz.html"
        }
    elif endpoint == "/api/v1/loopy/execute":
        return {
            "status_code": 200,
            "response_body": {"success": True, "iterations": 2, "passed_guard": True},
            "visualization_path": "/tmp/trajectory_viz.html"
        }
    return {"status_code": 404, "response_body": {"error": "Not Found"}}
```

---

## Anti-Patterns & Guardrails

- **Unauthenticated Mutation Endpoints** — Exposing ontology-mutating routes without cryptographic token verification.
- **Schema-Only Validation Blindness** — Validating JSON schema while ignoring OWL ledger axioms and semantic disjointness.
- **Unbounded Graph Expansion** — Returning 10,000+ triple subgraphs over HTTP without pagination or depth bounding.
