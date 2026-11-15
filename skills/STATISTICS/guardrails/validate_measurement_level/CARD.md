# Skill Summary Card: `validate_measurement_level`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        validate_measurement_level                │
│ Category:    STATISTICS / Symbolic Guardrails          │
│ Invocation:  /validate_measurement_level               │
│ Trigger:     "validate measurement level",             │
│              "stevens hierarchy", "check scale type",  │
│              "nominal ordinal interval ratio"          │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Enforce Stevens' measurement scale        │
│              hierarchy in Prolog to gate parametric vs │
│              non-parametric statistical test execution.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Extract column metadata, domain & semantic hint | Variable Signature AST | Column identifier registered |
| **2. Prolog Resolution**| Resolve scale via Stevens hierarchy logic | Resolved Scale Atom | Unified to nominal/ordinal/interval/ratio |
| **3. Visual Brief** | Render Stevens scale ladder & allowed gates | `%TEMP%\measurement-level-brief-*.html`| Dark theme HTML hierarchy brief |
| **4. Checkpoint** | Validate scale against requested test family | Permission Gating Record | Scale compatibility checked |
| **5. Permission Emit**| Assert known level in belief store & emit status | Structured Permission Payload| `allowed` or `blocked` emitted |

---

## Invariants & Guardrails

- [ ] **Stevens Hierarchy**: $\text{Nominal} \prec \text{Ordinal} \prec \text{Interval} \prec \text{Ratio}$.
- [ ] **Parametric Protection**: Parametric tests strictly require $\text{Interval} \lor \text{Ratio}$.
- [ ] **Nominal Isolation**: Nominal data strictly restricted to categorical tests (e.g. Chi-Square).
