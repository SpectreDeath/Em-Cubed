# Skill Summary Card: `production-rest-governance-agent`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        production-rest-governance-agent          │
│ Category:    ONTOLOGY / REST API Governance & Viz      │
│ Invocation:  /production-rest-governance-agent         │
│ Trigger:     "rest api governance", "validate endpoint",│
│              "visualize graph rag", "render audit api" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Govern, validate, and visually render     │
│              ontological OS operations across          │
│              production HTTP REST endpoints.           │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Request Audit** | Validate route, authentication & body schema | Validated Request AST | Bearer token & Pydantic validation passed |
| **2. OWL Validation** | Check payload against ontology ledger axioms | Ledger Verdict | Disjointness and property bounds verified |
| **3. Visual Brief** | Render interactive Graph-Path & dispatch timeline | `%TEMP%\rest-governance-brief-*.html` | Dark theme HTML API brief generated |
| **4. Checkpoint** | Gate destructive / mutating state updates | Security Gate Record | Mutations approved under API policy |
| **5. Dispatch & Viz** | Dispatch to controller & export graph HTML | HTTP Response & HTML Path | HTTP 200 returned with visual graph link |

---

## Invariants & Guardrails

- [ ] **Dual-Layer Validation**: Every request verified against OpenAPI schema AND OWL ontology ledger.
- [ ] **Bounded Subgraph Queries**: Max graph-rag traversal depth clamped to $\le 3$ hops over HTTP.
- [ ] **Explicit Status Codes**: Return standard RFC HTTP error codes (`400`, `401`, `422`, `500`).
