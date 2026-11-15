---
name: pagerank-centrality
domain: ANALYTICS
version: 1.0.0
surfaces:
  - python
  - prolog
description: Multi-surface PageRank centrality evaluator for relational network graphs. Detects graph structural anomalies (dead-ends and isolated loops) in Prolog, and computes power iteration matrix multiplication with random teleportation damping factors in Python until convergence. Use when evaluating node importance in knowledge graphs, ranking ontology concepts by connectivity centrality, or diagnosing graph structural sinks.
purpose: Compute iterative PageRank node centralities with Prolog structural graph validation and teleportation damping.
dependencies: []
tags:
  - pagerank
  - centrality-score
  - power-iteration
  - dead-end-detection
  - graph-analytics
  - prolog
inputs:
  edges:
    type: array
    required: true
    description: List of directed graph edges `[[source_node, target_node]]`.
  damping_factor:
    type: number
    required: false
    description: 'Random walk continuation probability factor $d \in (0, 1)$ (default: 0.85).'
  max_iterations:
    type: integer
    required: false
    description: 'Maximum power iteration cycles (default: 100).'
  tolerance:
    type: number
    required: false
    description: 'Convergence stopping threshold $\epsilon$ (default: 1e-4).'
outputs:
  ranked_nodes:
    type: array
    description: 'Sorted list of nodes with normalized centrality scores `[{"node": str, "rank": float}]`.'
  iterations_to_converge:
    type: integer
    description: Total power iteration loops executed before convergence.
  graph_diagnostics:
    type: object
    description: Detected dead-ends and isolated loops from Prolog validation.
---

# PageRank Centrality Engine

`pagerank-centrality` evaluates relational network node quality by modeling a stationary random walk Markov chain over directed graph structures. It audits structural anomalies (dead-ends and isolated cycles) in Prolog, applying the PageRank equation via power iteration in Python:

$$\mathbf{R}_{t+1}(u) = \frac{1 - d}{N} + d \sum_{v \in \text{In}(u)} \frac{\mathbf{R}_t(v)}{|\text{Out}(v)|}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage PageRank Progression

```
[1. Edge Invariant Audit] → [2. Prolog Topology Validation] → [3. Visual Brief] → [4. Checkpoint] → [5. Power Iteration & Rank Sorting]
```

### Stage 1: Edge & Node Invariant Audit
1. Ingest `edges` list ($E \ge 1$) and extract unique node set $\mathcal{V} = \{ u \mid (u, v) \in E \lor (v, u) \in E \}$.
2. Validate damping factor ($0.0 < d < 1.0$) and convergence tolerance ($\epsilon > 0$).

> **Completion criterion**: Directed graph indexed with non-empty node set $\mathcal{V}$ ($N = |\mathcal{V}| \ge 2$).

---

### Stage 2: Prolog Topology Validation (Dead-Ends & Isolated Loops)
1. Assert graph edges into Prolog knowledge base: `edge(Src, Dst).`
2. Detect **Dead-End Nodes**: Nodes with $|\text{Out}(u)| = 0$ (absorbing sinks).
3. Detect **Isolated Cycles / Disconnected Components**: Subgraphs unreachable from the main component.

> **Completion criterion**: Structural anomalies classified into diagnostic map.

---

### Stage 3: The Visual Brief
For network topology reviews or rank distribution audits, generate an interactive brief:
- **Location**: Write to `%TEMP%\pagerank-centrality-brief-<timestamp>.html` (Windows) or `/tmp/pagerank-centrality-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render directed network graph with node size scaled by PageRank centrality and dead-end nodes highlighted.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing large-scale power iterations ($N > 10,000$ nodes):
1. Verify sparse matrix adjacency representation to prevent memory bloat.
2. Confirm that damping factor $d$ is set appropriately ($d = 0.85$).

> **Completion criterion**: Iteration plan verified within memory and iteration budget.

---

### Stage 5: Power Iteration Matrix Multiplication
1. Initialize uniform rank vector: $\mathbf{R}_0(u) = 1 / N$.
2. Iterate until $\sum_u |\mathbf{R}_{t+1}(u) - \mathbf{R}_t(u)| < \epsilon$ or `max_iterations` reached:
   - Handle dead-ends by redistributing their mass uniformly across all $N$ nodes.
3. Sort nodes descending by final centrality score.

> **Completion criterion**: Convergence achieved with rank vector summing to $1.0 \pm 10^{-5}$.

---

## Surface References

### Python Power Iteration Surface

```python
from typing import List, Tuple, Dict, Any

def compute_pagerank(
    edges: List[Tuple[str, str]], 
    damping: float = 0.85, 
    max_iter: int = 100, 
    tol: float = 1e-4
) -> Dict[str, Any]:
    nodes = sorted(list({u for edge in edges for u in edge}))
    n = len(nodes)
    if n == 0:
        return {"ranked_nodes": [], "iterations_to_converge": 0}
        
    idx = {node: i for i, node in enumerate(nodes)}
    outbound = [0] * n
    for src, dst in edges:
        outbound[idx[src]] += 1
        
    rank = [1.0 / n] * n
    teleport = (1.0 - damping) / n
    iters = 0
    
    for it in range(1, max_iter + 1):
        iters = it
        new_rank = [teleport] * n
        dead_end_mass = 0.0
        
        for i in range(n):
            if outbound[i] > 0:
                share = (damping * rank[i]) / outbound[i]
                for src, dst in edges:
                    if idx[src] == i:
                        new_rank[idx[dst]] += share
            else:
                dead_end_mass += damping * rank[i]
                
        # Redistribute dead-end mass uniformly
        if dead_end_mass > 0:
            for j in range(n):
                new_rank[j] += dead_end_mass / n
                
        diff = sum(abs(new_rank[i] - rank[i]) for i in range(n))
        rank = new_rank
        if diff < tol:
            break
            
    ranked = [
        {"node": nodes[i], "rank": round(rank[i], 6)}
        for i in sorted(range(n), key=lambda k: rank[k], reverse=True)
    ]
    
    return {
        "ranked_nodes": ranked,
        "iterations_to_converge": iters,
        "graph_diagnostics": {"total_nodes": n, "total_edges": len(edges)}
    }
```

### Prolog Dead-End Detection Surface

```prolog
:- dynamic dead_end/1.

detect_dead_ends([]).
detect_dead_ends([Node|Rest]) :-
    \+ (edge(Node, _)),
    assertz(dead_end(Node)),
    detect_dead_ends(Rest).
detect_dead_ends([Node|Rest]) :-
    edge(Node, _),
    detect_dead_ends(Rest).
```

---

## Anti-Patterns & Guardrails

- **Rank Leakage at Dead Ends** — Failing to redistribute outbound mass from sink nodes ($|\text{Out}(u)| = 0$), causing total network rank mass to decay to zero.
- **Zero-Damping Teleportation Traps** — Setting damping factor to $1.0$, which causes spider traps and infinite cycles to monopolize 100% of rank mass.
- **Unsorted Output Payloads** — Returning raw node indices rather than descending-ranked entity score records.
