# Skill Summary Card: `skill-unconscious-inference`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-unconscious-inference               │
│ Category:    STATISTICS / Helmholtzian Model Selection │
│ Invocation:  /skill-unconscious-inference              │
│ Trigger:     "unconscious inference", "helmholtz map", │
│              "disambiguate models", "weighted priors", │
│              "candidate model selection"               │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Helmholtzian unconscious inference for    │
│              resolving ambiguity across valid logical  │
│              hypotheses with SQLite history & MAP picks│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate candidate model set $\mathcal{M}_{\text{valid}}$ | Candidate Hypothesis AST| At least 1 model present |
| **2. Prior Fusion** | Fuse prior weights & Laplace historical frequencies| Composite Weight Map | Combined scoring weights computed |
| **3. Visual Brief** | Render candidate tree & posterior score competition| `%TEMP%\unconscious-inference-brief-*.html`| Dark theme HTML inference brief |
| **4. Checkpoint** | Validate top model confidence margin ($\Delta > 0.05$)| Margin Resolution Record| Close call ambiguity evaluated |
| **5. Model & Commit** | Select MAP model, rank alternatives & commit SQLite| `UnconsciousInferenceResult`| Top pick emitted & SQLite updated |

---

## Invariants & Guardrails

- [ ] **Candidate Minimum Gate**: At least 1 valid candidate model required.
- [ ] **Laplace Smoothing**: Empirical success rate calculated as $\frac{S + 1}{N + 2}$.
- [ ] **Posterior Normalization**: Composite scores normalized to $\sum \text{Score}_i = 1.0$.
