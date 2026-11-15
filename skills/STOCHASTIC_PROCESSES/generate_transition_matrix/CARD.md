# Skill Summary Card: `generate_transition_matrix`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        generate_transition_matrix                │
│ Category:    STOCHASTIC_PROCESSES / Markov Transition  │
│ Invocation:  /generate_transition_matrix               │
│ Trigger:     "generate transition matrix",             │
│              "markov transition matrix",               │
│              "row stochastic normalization",           │
│              "laplace smoothing markov"                │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Construct row-stochastic transition       │
│              matrices with Laplace smoothing, absorbing│
│              state flags & Prolog validation rules.    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Validate sequence or count matrix & state labels| State Space AST | $R \ge 2$ states verified |
| **2. Smoothing** | Count transitions and apply Laplace $\alpha$ parameter| Smoothed Frequency Matrix| $\tilde{\mathbf{C}} \ge 0$ evaluated |
| **3. Visual Brief** | Render Markov state graph & transition heatmap | `%TEMP%\transition-matrix-brief-*.html`| Dark theme HTML Markov brief |
| **4. Checkpoint** | Validate row-stochastic normalization ($\sum P_j = 1.0$)| Normalization Gate Record| Row sums equal 1.0 |
| **5. Model Emission** | Classify absorbing states & emit matrix payload | `TransitionMatrixResult` | Complete matrix record emitted |

---

## Invariants & Guardrails

- [ ] **Row-Stochastic Normalization**: $\sum_{j=1}^R P_{ij} = 1.0 \pm 10^{-6}$ for all rows $i$.
- [ ] **Non-Negative Probabilities**: $P_{ij} \ge 0.0$ strictly enforced.
- [ ] **Uniform Fallback**: Unobserved states distributed uniformly ($1/R$).
