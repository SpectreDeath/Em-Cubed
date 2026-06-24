---
name: calculate_pagerank_vector
domain: STOCHASTIC_PROCESSES
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Computes the PageRank stationary distribution for a directed graph
  modeled as a Markov chain.  The damping factor (85 % link-follow,
  15 % random teleportation) prevents dead-end loops and guarantees
  convergence.  Prolog validates the graph before iteration; Python
  performs power iteration.
compatibility: PROLOG, PYTHON
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

# Calculate PageRank Vector

## Purpose
Compute the PageRank authority vector π for a directed graph G = (V, E) treated as a Markov chain with damping. The 85/15 rule (follow an outlink with probability 0.85; jump to any node uniformly with probability 0.15) ensures irreducibility by linking every state back to the teleportation set, guaranteeing Perron-Frobenius convergence.

## Connection to Veritasium and the Literature
- **PageRank (Page, Brin, Motwani, Winograd 1998)**: The web graph is a Markov chain. Dead-end nodes (dangling pages) have no outlinks and would absorb probability mass without a teleportation step.
- **Perron-Frobenius theorem**: A stochastic matrix that is irreducible and aperiodic has exactly one positive eigenvector (the stationary distribution). The damping factor enforces irreducibility.
- **Monte Carlo link-following**: The random surfer model samples pages as a Markov walk, where teleportation provides a 15% probability of reset.

### Damping Factor Mechanics — The 85/15 Rule
```
G(i, j) = transition probability of moving from i to j in the raw adjacency chain
d      = damping factor = 0.85

PageRank equation:
  PR(i) = (1 - d)                -- teleport mass landing on i
         + d * Σ_j [ PR(j) / outdegree(j) ]   -- link-follow mass

Matrix form (power iteration):
  π_new[j] = (1-d)/N + d * Σ_i π[i] * G[i][j]
```

**Why 15% random jump?**
- **Dead-end elimination**: Pages with 0 outlinks would be absorbing. Teleportation injects probability mass out.
- **Trap escape**: Cyclic subgraphs (e.g., two-page loops) would be periodic; random jumps ensure aperiodicity.
- **Irreducibility**: Every state has a nonzero incoming path from every other state through the teleportation step.
- **Empirical finding**: Brin & Page (1998) found 0.85 optimal for web convergence; values < 0.85 increase sensitivity to spam; values > 0.85 require more iterations.

## Prolog Surface (prelude.pl)

```prolog
:- module(pagerank_gen, [
    outdegree/3,
    dangling_node/2,
    teleport_vector/2,
    pagerank_permitted/3
]).

% ============================================================
% 1. Graph structural predicates
% ============================================================
outdegree(Node, Edges, OutDeg) :-
    count(edge(_, Node), Edges, _),    % incoming (for dangling check)
    OutDeg.

dangling_node(Node, Edges) :-
    forall(edge(Node, _), false),
    memberchk(node(Node), Edges2).

% ============================================================
% 2. Transition probability derivation
%    G[i][j] = 1 / outdegree(i)  if edge(i, j) exists, else 0
% ============================================================
transition_prob(From, To, Edges, Prob) :-
    member(edge(From, To), Edges),
    outdegree(From, Edges, Deg),
    Deg > 0,
    Prob is 1 / Deg.

% ============================================================
% 3. Teleportation vector (uniform over all nodes)
% ============================================================
teleport_vector(N, Teleport) :-
    Teleport is 1 / N.

% ============================================================
% 4. Permission gate
% ============================================================
pagerank_permitted(Edges, Nodes, allowed) :-
    length(Nodes, N),
    N >= 2,
    \+ dangling_node(_, Edges),  % will be handled by teleportation
    !.
  
pagerank_permitted(_, _, allowed).  % always allowed with teleportation

% ============================================================
% 5. Convergence check
% ============================================================
converged(OldRanks, NewRanks, Tolerance) :-
    maplist(diff_check, OldRanks, NewRanks, Deltas),
    max_list(Deltas, MaxDelta),
    MaxDelta < Tolerance.

diff_check(A, B, D) :- D is abs(A - B).
```

## Python Surface (executor.py)

```python
"""
calculate_pagerank_vector
===========================
Power-iteration PageRank solver with 85/15 damping factor.
Derives the transition matrix from edge list, applies teleportation,
and iterates until rank vector converges.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class PageRankResult:
    ranks: Dict[str, float]
    sorted_ranks: Tuple[Tuple[str, float], ...]
    iterations: int
    linf_norm_delta: float
    damping: float
    n_nodes: int

    def to_dict(self) -> dict:
        return {
            "ranks":          dict(self.ranks),
            "sorted_ranks":   [list(r) for r in self.sorted_ranks],
            "iterations":     self.iterations,
            "linf_norm_delta": self.linf_norm_delta,
            "damping":        self.damping,
            "n_nodes":        self.n_nodes,
        }


def calculate_pagerank_vector(
    edges: List[Tuple[Union[str, int], Union[str, int]]],
    damping: float = 0.85,
    max_iter: int = 1_000,
    tol: float = 1e-10,
    personalization: Optional[Dict[Union[str, int], float]] = None,
) -> PageRankResult:
    """Compute PageRank via power iteration with teleportation damping.

    Parameters
    ----------
    edges : list of (src, dst) tuples
        Directed edge list.  Duplicate edges are collapsed and their
        weights summed.
    damping : float
        Probability of following an outlink (0.85 = 85% teleportation
        free-browsing probability = 1 - damping = 0.15).
    max_iter : int
        Power-iteration ceiling.
    tol : float
        L∞ convergence tolerance.
    personalization : dict or None
        Optional non-uniform teleportation distribution.  If provided,
        keys are node labels and values are target probabilities
        (automatically normalized to sum to 1).  None → uniform.

    Returns
    -------
    PageRankResult

    Raises
    ------
    ValueError
        Empty edges with no solo nodes, or damping not in (0, 1).
    """
    if not (0.0 < damping < 1.0):
        raise ValueError(f"damping must be in (0, 1), got {damping}")

    # ---- Build adjacency ----
    adj: Dict[str, Dict[str, float]] = {}
    nodes: set = set()
    for src, dst in edges:
        src_s = str(src)
        dst_s = str(dst)
        nodes.add(src_s)
        nodes.add(dst_s)
        adj.setdefault(src_s, {})
        adj[src_s][dst_s] = adj[src_s].get(dst_s, 0.0) + 1.0

    node_list = sorted(nodes)
    n = len(node_list)
    if n == 0:
        raise ValueError("edges list produces no nodes")

    # ---- Degrees and dangling flags ----
    outdegree: Dict[str, float] = {s: sum(adj.get(s, {}).values()) for s in node_list}
    is_dangling: Dict[str, bool] = {s: (outdegree[s] == 0.0) for s in node_list}

    # ---- Transition matrix G (row-stochastic from adjacency) ----
    G: List[List[float]] = []
    for i, src in enumerate(node_list):
        row = [0.0] * n
        destinations = adj.get(src, {})
        deg = outdegree[src]
        if deg > 0:
            for dst, cnt in destinations.items():
                j = node_list.index(dst)
                row[j] = cnt / deg
        G.append(row)

    # ---- Teleportation vector ----
    if personalization is None:
        teleport = [(1.0 - damping) / n] * n
    else:
        raw = [personalization.get(s, 0.0) for s in node_list]
        total = sum(raw)
        teleport = [v / total if total > 0 else 1.0 / n for v in raw]

    # ---- Power iteration: π_new = e * (1-d) + (π_old · G) * d ----
    pi = [1.0 / n] * n
    iters = 0
    delta = float("inf")

    for it in range(max_iter):
        new_pi = [0.0] * n

        # (a) Teleportation mass
        for j in range(n):
            new_pi[j] = teleport[j]

        # (b) Link-follow mass: (π_old · G) * d
        for i in range(n):
            if pi[i] == 0.0:
                continue
            contrib = pi[i] * damping
            for j in range(n):
                if G[i][j] > 0:
                    new_pi[j] += contrib * G[i][j]

        # (c) Dangling redistribution (dead-end fix)
        dangling_mass = sum(pi[i] for i in range(n) if is_dangling[node_list[i]])
        dangling_distributed = dangling_mass * damping / n
        for j in range(n):
            new_pi[j] += dangling_distributed

        # (d) Convergence test
        delta = max(abs(new_pi[j] - pi[j]) for j in range(n))
        pi = new_pi
        iters = it + 1

        if delta < tol:
            break

    # -- Normalize (numerical drift compensation) --
    total = sum(pi)
    pi = [p / total for p in pi] if total > 0 else [1.0 / n] * n

    ranks = {s: p for s, p in zip(node_list, pi)}
    sorted_ranks = tuple(sorted(ranks.items(), key=lambda x: x[1], reverse=True))

    return PageRankResult(
        ranks           = ranks,
        sorted_ranks    = sorted_ranks,
        iterations      = iters,
        linf_norm_delta = delta,
        damping         = damping,
        n_nodes         = n,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| edges | list[tuple[str\|int, str\|int]] | Directed edge pairs |
| damping | float | Link-follow probability (default 0.85; teleport = 0.15) |
| max_iter | int | Power-iteration ceiling (default 1,000) |
| tol | float | L∞ convergence tolerance (default 1e-10) |
| personalization | dict or None | Non-uniform teleportation target |

## Outputs

| name | type | description |
|---|---|---|
| ranks | dict[str → float] | Node → PageRank value |
| sorted_ranks | tuple[tuple] | Nodes ranked descending by PageRank |
| iterations | int | Steps to convergence |
| linf_norm_delta | float | Final per-iteration residual |
| damping | float | Echo of input |
| n_nodes | int | Node count |

## Invariants
1. `sum(ranks.values()) == 1.0` (enforced by post-iteration normalization)
2. All ranks `>= 0.0`, finite (no NaN, Inf)
3. Damping factor must be in (0, 1); typical value 0.85
4. If `personalization` supplied, it is normalized to a valid distribution before use
5. Dangling-node mass is redistributed uniformly (not lost)
6. Iterations ≤ max_iter; convergence guaranteed by Perron-Frobenius

## Edge Cases
| Scenario | Behavior |
|---|---|
| Single node with self-loop | Rank = 1.0 (absorbed through teleportation loop) |
| Two-node cycle | Equal ranks ≈ 0.5 each |
| Isolated node (no in/out edges) | Rank ≈ (1-d)/n + d/N → near-zero for large d |
| Dangling node (outdegree=0) | Mass redistributed uniformly via dangling redistribution |
| Personalization dict sums to 0 | Fallback to uniform teleportation |
| Very large graph (>10^5 edges) | O(k·E) per iteration; use sparse adjacency for speed |

## State Updates
```
state_add_observation("graph/pagerank/ranks", result.ranks)
state_add_observation("graph/pagerank/top_node", top_node)
state_add_observation("graph/pagerank/iterations", result.iterations)
belief_add(pagerank_computed(GraphId, Ranks, Damping, Convergence))
```

## Security
- No I/O. Pure computation on user-supplied edge list.
- No external dependencies.
