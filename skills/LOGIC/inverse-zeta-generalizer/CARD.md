# Skill Summary Card: `inverse-zeta-generalizer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        inverse-zeta-generalizer                  │
│ Category:    LOGIC / Continuous Jaynesian Probability  │
│ Invocation:  /inverse-zeta-generalizer                 │
│ Trigger:     "generalize inverse zeta",                │
│              "continuous lattice probability",         │
│              "bayesian lattice update", "jaynes proof" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Map distributive lattice structures to    │
│              continuous degrees of belief [0, 1] and   │
│              verify Cox-Jaynes consistency via Z3 SMT. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate lattice distributivity & observation weights| Validated Lattice AST | Non-negative evidence weights ($w_i \ge 0$) |
| **2. Prior Estimation**| Compute uninformative Dirichlet prior from poset | Prior Density Array | Prior distribution sums to 1.0 |
| **3. Visual Brief** | Render prior vs posterior charts & KL divergence | `%TEMP%\inverse-zeta-brief-*.html`| Dark theme HTML probability brief |
| **4. Checkpoint** | Validate numerical stability & non-zero density | Stability Gate Record | No total probability collapse |
| **5. Bayes Update & SMT**| Compute posterior & prove Jaynes consistency in Z3| Posterior Probability Map | Z3 `sat` and KL info gain emitted |

---

## Invariants & Guardrails

- [ ] **Sum-to-One Invariant**: $\sum_{e \in \mathcal{L}} P(e) = 1.0 \pm 10^{-6}$.
- [ ] **Strict Non-Negativity**: $P(e) \ge 0.0$ for all lattice elements.
- [ ] **Dirichlet Smoothing**: $\alpha > 0.0$ on all prior allocations.
