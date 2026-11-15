# Skill Summary Card: `associative-chaining-product`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        associative-chaining-product              │
│ Category:    DECISION_MAKING / Lattice Probability     │
│ Invocation:  /associative-chaining-product             │
│ Trigger:     "associative chaining product",           │
│              "chain conditional probabilities",        │
│              "product rule lattice", "implication path"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Chain conditional probabilities along     │
│              directed lattice implication paths with   │
│              Prolog topological proof & product rules. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest path sequence & target conditional spec | Implication Path AST | $k \ge 2$ path verified |
| **2. Prolog Proof** | Prove transitive implication in Prolog | Implication Proof Atom | $A \implies B \implies C$ proved |
| **3. Visual Brief** | Render implication graph & probability waterfall | `%TEMP%\associative-chaining-brief-*.html`| Dark theme HTML chain brief |
| **4. Checkpoint** | Validate intermediate probability bounds $[0, 1]$ | Boundedness Gate Record | All factors $\in [0, 1]$ |
| **5. Model Emission** | Multiply conditionals & emit chained result | `ChainingResult` Payload | Full chained payload emitted |

---

## Invariants & Guardrails

- [ ] **Implication Path Guard**: $A \implies B \implies C$ strictly verified in Prolog.
- [ ] **Probability Factor Bounds**: $0.0 \le P(X_i \mid X_{i+1}) \le 1.0$ for all links.
- [ ] **Endpoint Alignment**: Start matches target and end matches given.
