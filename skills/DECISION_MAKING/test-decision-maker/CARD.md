# Skill Summary Card: `test-decision-maker`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        test-decision-maker                       │
│ Category:    DECISION_MAKING / Decision Evaluation     │
│ Invocation:  /test-decision-maker                      │
│ Trigger:     "test decision maker", "option selection",│
│              "decision evaluation", "confidence score",│
│              "criterion ranking"                       │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Evaluate & rank candidate options using   │
│              criterion-based scoring and confidence-   │
│              weighted margin-of-victory selection.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest candidate options, criteria scores & weights | Decision Problem AST | Non-empty options verified |
| **2. Scoring** | Compute weighted scores $\text{Score}(o) = \sum w_j s_j(o)$| Unnormalized Score Map | All scores computed |
| **3. Visual Brief** | Render score bar chart & victory margin gauge | `%TEMP%\test-decision-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate tie-breaking & confidence bounds $[0, 1]$| Selection Gate Record | Margin evaluated safely |
| **5. Model Emission**| Select $o^*$, synthesize reasoning & emit payload | `DecisionResult` Payload | Full decision payload emitted |

---

## Invariants & Guardrails

- [ ] **Candidate Minimum Gate**: At least 1 option required.
- [ ] **Confidence Scale**: $0.0 \le C \le 1.0$.
- [ ] **Margin Calculation**: $C = \text{Score}(o^*) - \text{Score}(o_{\text{second}})$.
