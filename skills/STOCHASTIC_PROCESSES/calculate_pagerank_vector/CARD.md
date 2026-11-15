# Skill Summary Card: `calculate_pagerank_vector`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        calculate_pagerank_vector                 │
│ Category:    STOCHASTIC_PROCESSES / PageRank Vector    │
│ Invocation:  /calculate_pagerank_vector                │
│ Trigger:     "calculate pagerank vector", "pagerank",  │
│              "power iteration graph", "damping factor",│
│              "node authority centrality"               │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute PageRank authority vectors via    │
│              power iteration with 85/15 damping,       │
│              dangling redistribution & personalization.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Extract graph adjacency and identify dangling nodes| Directed Graph AST | $N \ge 2$ nodes verified |
| **2. Setup** | Construct link matrix $\mathbf{G}$ and teleportation vector| Damped Transition Model | $d \in (0, 1)$ verified |
| **3. Visual Brief** | Render graph network & PageRank convergence curve | `%TEMP%\pagerank-brief-*.html`| Dark theme HTML PageRank brief |
| **4. Checkpoint** | Validate dangling redistribution & personalization| Conservation Gate Record| Full probability mass preserved |
| **5. Model Emission** | Solve $\boldsymbol{\pi}$ via power iteration & emit | `PageRankResult` Payload | Full rank payload emitted |

---

## Invariants & Guardrails

- [ ] **Damping Invariant**: $d \in (0.0, 1.0)$ (default $0.85$).
- [ ] **Rank Sum Conservation**: $\sum_{i=1}^N \text{PR}_i = 1.0 \pm 10^{-6}$.
- [ ] **Dangling Node Fix**: Out-degree 0 nodes uniformly redistribute mass.
