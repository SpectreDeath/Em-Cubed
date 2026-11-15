# Skill Summary Card: `assert_context_gate`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        assert_context_gate                       │
│ Category:    STOCHASTIC_PROCESSES / Context Gating     │
│ Invocation:  /assert_context_gate                      │
│ Trigger:     "assert context gate", "controlled markov │
│              chain", "state transition guard",         │
│              "symbolic loop prevention"                │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Symbolic context gating of Markov state   │
│              transitions with capability, resource,    │
│              recency & safety verification in Prolog.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest state pair & working memory snapshot | Context State AST | Context fields verified |
| **2. Prolog Facts** | Synthesize dynamic Prolog facts from memory | Belief Store Atoms | Facts asserted to belief base |
| **3. Visual Brief** | Render transition decision tree & 4-gate status| `%TEMP%\context-gate-brief-*.html`| Dark theme HTML gate brief |
| **4. Checkpoint** | Validate loop history & budget sufficiency | Gate Decision Record | Resource & loop checks verified |
| **5. Model Emission** | Evaluate all 4 gates & emit permission payload | `GateResult` Record | Full gating decision emitted |

---

## Invariants & Guardrails

- [ ] **Controlled Markov Process**: Transitions gated by $P(s' \mid s, \text{context})$.
- [ ] **Loop Penalty Invariant**: No immediate repeated transitions within 3 steps.
- [ ] **Resource Conservation**: Action cost must not exceed available budget $R$.
