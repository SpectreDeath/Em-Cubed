# Skill Summary Card: `skill-anomaly-diagnostic`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-anomaly-diagnostic                  │
│ Category:    MODEL_VALIDATION / Adversarial SMT Testing│
│ Invocation:  /skill-anomaly-diagnostic                 │
│ Trigger:     "skill anomaly diagnostic", "adversarial  │
│              "z3 deadlock test", "constraint resilience│
│              "unsat core diagnostic", "edge case check"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Edge-case diagnostic tester that injects  │
│              adversarial variations into baseline      │
│              constraints to verify Z3 SMT resilience.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest baseline constraints & adversarial variations| Constraint Problem AST | Non-empty input verified |
| **2. Z3 SMT Check**| Formulate SMT assertions & check satisfiability | Z3 SMT Satisfiability | `sat`/`unsat` resolved |
| **3. Visual Brief** | Render resilience gauge & failure case cards | `%TEMP%\anomaly-diagnostic-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate resilience threshold & extract UNSAT cores| Resilience Gate Record | Threshold gate evaluated |
| **5. Model Emission**| Assemble diagnostic report & emit result payload | `AnomalyDiagnosisResult` Payload| Full diagnostic payload emitted|

---

## Invariants & Guardrails

- [ ] **Resilience Scale**: $0.0 \le \text{Resilience} \le 1.0$.
- [ ] **UNSAT Extraction**: Every deadlock includes the causal failing variation.
- [ ] **Threshold Gating**: Alerts emitted if score falls below `resilience_threshold`.
