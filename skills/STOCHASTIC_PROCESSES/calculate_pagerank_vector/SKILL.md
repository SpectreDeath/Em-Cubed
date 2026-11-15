---
name: calculate_pagerank_vector
domain: STOCHASTIC_PROCESSES
version: 1.0.0
surfaces:
  - prolog
  - python
description: Directed graph PageRank authority vector computation engine modeling web links as a damped Markov chain. Evaluates the 85/15 damping factor ($d = 0.85$ link-following, $1 - d = 0.15$ random teleportation) to guarantee Perron-Frobenius irreducibility, redistributes dangling node mass (zero out-degree fix), supports personalized teleportation distributions, verifies graph properties in Prolog, and calculates steady-state PageRank vectors via power iteration in Python. Use when computing network node centrality, ranking state importances, or solving stationary distributions on directed graphs.
purpose: Compute PageRank stationary authority vectors via power iteration with 85/15 damping and dangling-node redistribution.
dependencies:
  - STOCHASTIC_PROCESSES/generate_transition_matrix
  - STOCHASTIC_PROCESSES/evaluate_stationarity
tags:
  - pagerank
  - power-iteration
  - damping-factor
  - perron-frobenius
  - network-centrality
  - dangling-nodes
inputs:
  edges:
    type: array
    required: true
    description: Directed edge list `[('node_a', 'node_b'), ...]`.
  damping:
    type: number
    required: false
    description: Link-following probability $d \in (0, 1)$ (default 0.85).
  max_iter:
    type: integer
    required: false
    description: Power iteration maximum ceiling (default 1000).
  tol:
    type: number
    required: false
    description: $L_\infty$ convergence residual threshold (default 1e-10).
  personalization:
    type: object
    required: false
    description: 'Optional non-uniform teleportation probability map `{node_id: weight}`.'
outputs:
  ranks:
    type: object
    description: Dictionary mapping each node to its normalized PageRank score.
  sorted_ranks:
    type: array
    description: Ranked list of `(node, score)` tuples in descending order of authority.
  iterations:
    type: integer
    description: Steps required for power iteration convergence.
  linf_norm_delta:
    type: number
    description: Final $L_\infty$ residual norm between successive iterations.
  damping:
    type: number
    description: Damping factor $d$ utilized during computation.
  n_nodes:
    type: integer
    description: Total distinct node count in the graph.
---

# Calculate PageRank Vector Engine

`calculate_pagerank_vector` computes the stationary authority distribution $\boldsymbol{\pi}$ on a directed graph $G = (V, E)$ treated as a damped Markov chain. It enforces the **85/15 damping rule** ($d = 0.85$) to guarantee **Perron-Frobenius irreducibility**, redistributes dangling node mass, and solves $\boldsymbol{\pi}$ via **power iteration** in **Python**:

$$\boldsymbol{\pi}^{(k+1)} = (1 - d)\mathbf{v}_{\text{teleport}} + d (\boldsymbol{\pi}^{(k)}\mathbf{G}) + d \frac{\sum_{i \in \text{Dangling}} \pi_i^{(k)}}{N} \mathbf{1}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage PageRank Progression

```
[1. Graph Adjacency & Dangling Audit] → [2. Transition Matrix & Teleportation Setup] → [3. Visual Brief] → [4. Checkpoint] → [5. Power Iteration & Rank Emit]
```

### Stage 1: Graph Adjacency & Dangling Node Audit
1. Ingest directed `edges` list; extract distinct node set $V$ ($N = |V| \ge 2$).
2. Compute out-degree $\text{deg}^+(u)$ for every node.
3. Flag dangling nodes ($\text{deg}^+(u) = 0$).

> **Completion criterion**: Clean directed adjacency graph established with $N \ge 2$.

---

### Stage 2: Transition Matrix & Teleportation Vector Setup
1. Construct row-stochastic link transition matrix $\mathbf{G}$:
   $$G_{uv} = \frac{1}{\text{deg}^+(u)} \quad \text{if } (u, v) \in E$$
2. Construct teleportation vector $\mathbf{v}_{\text{teleport}}$ (uniform $1/N$ or personalized).

> **Completion criterion**: Transition matrix and teleportation vector initialized.

---

### Stage 3: The Visual Brief
For graph centrality and PageRank authority flows, generate an interactive brief:
- **Location**: Write to `%TEMP%\pagerank-brief-<timestamp>.html` (Windows) or `/tmp/pagerank-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render directed network graph with node size scaled to PageRank authority score, top-k rank table, and power iteration convergence chart.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before power iteration:
1. Verify damping parameter: $0 < d < 1.0$ (typically $0.85$).
2. Verify personalization vector normalization: $\sum v_i = 1.0$.

> **Completion criterion**: Damping factor and teleportation mass verified.

---

### Stage 5: Power Iteration & Authority Ranking Emission
1. Initialize uniform distribution $\boldsymbol{\pi}^{(0)} = (1/N, \dots, 1/N)$.
2. Iterate damped transition equation until $\|\boldsymbol{\pi}^{(k+1)} - \boldsymbol{\pi}^{(k)}\|_\infty < \text{tol}$.
3. Sort nodes descending by PageRank score.
4. Emit complete `PageRankResult` record.

> **Completion criterion**: Full PageRank authority payload emitted.

---

## Surface References

### Python Calculation Surface

```python
from typing import List, Dict, Any, Optional, Tuple

def calculate_pagerank_vector(
    edges: List[Tuple[Any, Any]],
    damping: float = 0.85,
    max_iter: int = 1000,
    tol: float = 1e-10,
    personalization: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    if not (0.0 < damping < 1.0):
        raise ValueError(f"invalid_damping: Damping must be in (0, 1), got {damping}.")
        
    nodes = set()
    adj = {}
    for src, dst in edges:
        s, d = str(src), str(dst)
        nodes.add(s)
        nodes.add(d)
        adj.setdefault(s, {})
        adj[s][d] = adj[s].get(d, 0.0) + 1.0
        
    node_list = sorted(nodes)
    n = len(node_list)
    if n == 0:
        raise ValueError("empty_graph: Edge list produced no nodes.")
        
    outdeg = {s: sum(adj.get(s, {}).values()) for s in node_list}
    is_dangling = {s: (outdeg[s] == 0.0) for s in node_list}
    
    G = []
    for src in node_list:
        row = [0.0] * n
        deg = outdeg[src]
        if deg > 0:
            for dst, cnt in adj.get(src, {}).items():
                j = node_list.index(dst)
                row[j] = cnt / deg
        G.append(row)
        
    if personalization is None:
        teleport = [(1.0 - damping) / n] * n
    else:
        raw = [personalization.get(s, 0.0) for s in node_list]
        tot = sum(raw)
        teleport = [v / tot if tot > 0 else 1.0 / n for v in raw]
        
    pi = [1.0 / n] * n
    iters = 0
    delta = float("inf")
    
    for it in range(max_iter):
        new_pi = [teleport[j] for j in range(n)]
        
        # Link-following mass
        for i in range(n):
            if pi[i] > 0:
                contrib = pi[i] * damping
                for j in range(n):
                    if G[i][j] > 0:
                        new_pi[j] += contrib * G[i][j]
                        
        # Dangling node redistribution
        dangling_mass = sum(pi[i] for i in range(n) if is_dangling[node_list[i]])
        dangling_add = dangling_mass * damping / n
        for j in range(n):
            new_pi[j] += dangling_add
            
        delta = max(abs(new_pi[j] - pi[j]) for j in range(n))
        pi = new_pi
        iters = it + 1
        if delta < tol:
            break
            
    tot_pi = sum(pi)
    pi = [p / tot_pi for p in pi] if tot_pi > 0 else [1.0 / n] * n
    
    ranks = {s: round(p, 6) for s, p in zip(node_list, pi)}
    sorted_ranks = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "ranks": ranks,
        "sorted_ranks": sorted_ranks,
        "iterations": iters,
        "linf_norm_delta": delta,
        "damping": damping,
        "n_nodes": n
    }
```

---

## Anti-Patterns & Guardrails

- **Dangling Node Probability Loss** — Failing to redistribute probability mass from nodes with zero out-links, causing probability leakage ($\sum \pi_i < 1$).
- **Zero Damping ($d = 1.0$) Deadlock** — Setting damping to 1.0 on graphs with absorbing or periodic components, preventing convergence.
- **Unnormalized Personalization Vector** — Passing personalization weights that do not sum to 1.0.
