# Skill Summary Card: `strategic-planner`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        strategic-planner                         │
│ Category:    DECISION_MAKING / Strategic Planning      │
│ Invocation:  /strategic-planner                        │
│ Trigger:     "strategic planner", "portfolio plan",    │
│              "smt resource allocation", "feasibility"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Synthesize optimal strategic initiative   │
│              portfolios with Z3 SMT constraint bounds  │
│              and multi-criteria utility optimization.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest strategic options & global resource bounds | Strategic Portfolio AST | Non-negative bounds verified |
| **2. Z3 SMT** | Encode linear resource constraints & solve in Z3 | SMT Feasibility Atom | SMT satisfiability proved |
| **3. Visual Brief** | Render roadmap Gantt & budget allocation charts | `%TEMP%\strategic-planner-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate budget ceiling ($\sum x_i C_i \le B_{\text{max}}$)| Budget Gate Record | Resource constraints met |
| **5. Model Emission**| Select optimal portfolio & emit ranking payload | `StrategicPlanResult` Payload | Full strategic payload emitted |

---

## Invariants & Guardrails

- [ ] **Budget Conservation**: Total cost $\le B_{\text{max}}$.
- [ ] **SMT Soundness**: Z3 solver certifies binary portfolio feasibility.
- [ ] **Benefit-Cost Monotonicity**: Options ranked by valid $\text{Value} / \text{Cost}$ ratios.
