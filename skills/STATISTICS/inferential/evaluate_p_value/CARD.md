# Skill Summary Card: `evaluate_p_value`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        evaluate_p_value                          │
│ Category:    STATISTICS / Inferential Decisions        │
│ Invocation:  /evaluate_p_value                         │
│ Trigger:     "evaluate p-value", "hypothesis decision",│
│              "reject null", "fail to reject null"      │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Translate numerical p-values into formal  │
│              hypothesis decisions via first-order      │
│              Prolog logic rules and narrative evidence.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate $p \in [0, 1]$ and $\alpha \in (0, 1)$ | Validated Input Spec | Inputs within theoretical bounds |
| **2. Prolog Routing** | Route through `hypothesis_state/3` logic | Decision & State Atoms | Formal state unified |
| **3. Visual Brief** | Render null distribution curve with $\alpha$ cut | `%TEMP%\p-value-brief-*.html`| Dark theme HTML p-value brief |
| **4. Checkpoint** | Validate boundary condition ($p = \alpha$) | Boundary Gate Record | Boundary logic confirmed |
| **5. Result Emit** | Construct narrative summary & emit payload | `PValueResult` | Structured result record emitted |

---

## Invariants & Guardrails

- [ ] **Strict Inequality Rejection**: $p < \alpha \implies \text{reject\_null}$; $p \ge \alpha \implies \text{fail\_to\_reject\_null}$.
- [ ] **No Acceptance Claim**: Use "fail to reject", never "accept null".
- [ ] **Alpha Bounds**: Significance level strictly in $(0.0, 1.0)$.
