# Skill Summary Card: `pagerank-centrality`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        pagerank-centrality                       │
│ Category:    ANALYTICS / Network Graph Centrality      │
│ Invocation:  /pagerank-centrality                      │
│ Trigger:     "compute pagerank", "node centrality",    │
│              "graph ranking", "power iteration rank"   │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Iterative power-iteration PageRank        │
│              centrality with Prolog dead-end detection │
│              and random teleportation damping.         │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate edge pairs & extract node set $\mathcal{V}$ | Indexed Graph AST | $N = |\mathcal{V}| \ge 2$ & $d \in (0, 1)$ |
| **2. Topology Check** | Detect dead-ends & isolated cycles in Prolog | Prolog Diagnostics Map | Sinks & cycles identified |
| **3. Visual Brief** | Render network topology with rank node scaling | `%TEMP%\pagerank-centrality-brief-*.html`| Dark theme HTML centrality brief |
| **4. Checkpoint** | Validate sparse matrix representation & budget | Safety Gate Record | Memory and iteration bounds safe |
| **5. Power Iteration** | Execute matrix iterations until convergence | Ranked Node List | Rank vector sums to $1.0 \pm 10^{-5}$ |

---

## Invariants & Guardrails

- [ ] **Rank Conservation**: $\sum_{u \in \mathcal{V}} \mathbf{R}(u) = 1.0 \pm 10^{-5}$.
- [ ] **Damping Bound**: Damping factor strictly in $(0.0, 1.0)$ (typically $0.85$).
- [ ] **Deterministic Sorting**: Nodes sorted descending by rank score.
