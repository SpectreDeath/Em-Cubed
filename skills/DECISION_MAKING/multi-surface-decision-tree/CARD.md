# Skill Summary Card: `multi-surface-decision-tree`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        multi-surface-decision-tree               │
│ Category:    DECISION_MAKING / Decision Tree Analysis  │
│ Invocation:  /multi-surface-decision-tree              │
│ Trigger:     "multi surface decision tree",            │
│              "pareto optimal decision", "fuzzy decision│
│              "multi criteria tree", "option scoring"   │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Evaluate multi-criteria options with      │
│              Prolog Pareto dominance & constraints,    │
│              Python scaling & Hy fuzzy score synthesis.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest options, criteria keys & threshold constraints| Decision Candidate AST | Options & criteria parsed |
| **2. Prolog Pareto**| Prove Pareto optimality & check hard constraints | Pareto Frontier Atom | Dominated options pruned |
| **3. Visual Brief** | Render decision tree & 2D Pareto scatter plot | `%TEMP%\decision-tree-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate weight sum ($\sum w_c = 1$) & compliance| Compliance Gate Record | Compliant subset isolated |
| **5. Model Emission**| Aggregate fuzzy scores, rank options & emit $a^*$ | `DecisionTreeResult` Payload | Full decision payload emitted |

---

## Invariants & Guardrails

- [ ] **Pareto Optimality Invariant**: Non-dominated set satisfies $\neg \exists b \succ a$.
- [ ] **Hard Constraint Gating**: Non-compliant options flagged with violation codes.
- [ ] **Normalized Score Scale**: All normalized scores strictly within $[0.0, 1.0]$.
