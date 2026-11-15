# Skill Summary Card: `nuisance-parameter-integrator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        nuisance-parameter-integrator             │
│ Category:    STATISTICS / Bayesian Marginalization     │
│ Invocation:  /nuisance-parameter-integrator            │
│ Trigger:     "nuisance parameter integrator",          │
│              "bayesian marginalization",               │
│              "integrate background uncertainty"        │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Bayesian marginalization of nuisance      │
│              parameters with Z3 probability mass       │
│              conservation proofs & exact integration.  │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate joint matrix $P_{K \times M} \ge 0$ | Joint Probability Matrix AST| Valid joint distribution verified |
| **2. Z3 Verification**| Verify total probability conservation axioms | Z3 Sat Certificate | Mass conservation certified |
| **3. Visual Brief** | Render joint density heatmap & 1D marginal curve| `%TEMP%\nuisance-integrator-brief-*.html`| Dark theme HTML marginal brief |
| **4. Checkpoint** | Validate normalization sum ($\sum P(\omega) \approx 1.0$)| Normalization Gate Record | Unit mass verified |
| **5. Model Emission** | Sum nuisance dimensions & emit marginal vector | `NuisanceMarginalResult` | Complete marginal payload emitted |

---

## Invariants & Guardrails

- [ ] **Non-Negative Invariant**: All cell probabilities $P(\omega_i, \theta_j) \ge 0$.
- [ ] **Total Probability Conservation**: $\sum_{i} P(\omega_i) = 1.0 \pm 10^{-6}$.
- [ ] **Z3 Axiom Proof**: Marginalization algebra verified satisfiable.
