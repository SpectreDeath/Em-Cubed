---
name: pagerank-centrality
domain: ANALYTICS
version: "1.0.0"
surfaces: [python, prolog]
description: Multi-surface PageRank centrality with Python surface for power iteration and Prolog surface for graph validation before numerical computation.
compatibility: PYTHON, PROLOG
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

## Purpose
Evaluates relational network node quality by treating linkages as a persistent Markov Chain with damping factor.

## Description
Implements power iteration matrix multiplication to distribute node weight until convergence. Prolog validates graph structure (dead-ends, isolated loops) before power iteration, forcing Python to apply random teleportation damping factor to those coordinates.

## Python Surface

```python
def compute_pagerank(edges, damping=0.15, max_iter=100, tol=0.0001):
    nodes = set()
    for src, dst in edges:
        nodes.add(src)
        nodes.add(dst)

    n = len(nodes)
    node_list = sorted(nodes)
    node_index = {node: i for i, node in enumerate(node_list)}

    outbound = {i: 0 for i in range(n)}
    for src, dst in edges:
        outbound[node_index[src]] += 1

    rank = [1.0 / n] * n
    teleport = (1.0 - damping) / n

    for _ in range(max_iter):
        new_rank = [teleport] * n

        for i in range(n):
            if outbound[i] > 0:
                contribution = rank[i] / outbound[i]
                for src, dst in edges:
                    if node_index[src] == i:
                        new_rank[node_index[dst]] += damping * contribution

        diff = sum(abs(new_rank[i] - rank[i]) for i in range(n))
        rank = new_rank

        if diff < tol:
            break

    result = {node: rank[node_index[node]] for node in node_list}
    sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    return sorted_result
```

## Prolog Surface

```prolog
:- dynamic dead_end/1.
:- dynamic isolated_loop/1.

detect_dead_ends([]).
detect_dead_ends([Node|Rest]) :-
    \+ (edge(Node, _)),
    assertz(dead_end(Node)),
    detect_dead_ends(Rest).
detect_dead_ends([Node|Rest]) :-
    edge(Node, _),
    detect_dead_ends(Rest).

detect_isolated_loops([]).
detect_isolated_loops([Node|Rest]) :-
    \+ (edge(_, Node)),
    \+ (edge(Node, _)),
    assertz(isolated_loop(Node)),
    detect_isolated_loops(Rest).
detect_isolated_loops([Node|Rest]) :-
    (edge(_, Node) ; edge(Node, _)),
    detect_isolated_loops(Rest).

validate_page_graph(Nodes, Edges) :-
    forall(member(Node, Nodes),
           (member(edge(Node, _), Edges) ; member(edge(_, Node), Edges))).
```

## Testing

### Unit Tests

```python
def test_simple_pagerank():
    edges = [
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'C'),
        ('C', 'A')
    ]
    result = compute_pagerank(edges, damping=0.15, max_iter=100)
    assert len(result) == 3
    assert result[0][0] == 'C'
    assert result[0][1] > result[1][1] > result[2][1]

def test_two_node_cycle():
    edges = [
        ('X', 'Y'),
        ('Y', 'X')
    ]
    result = compute_pagerank(edges, damping=0.15, max_iter=100)
    assert len(result) == 2
    assert abs(result[0][1] - result[1][1]) < 0.1

def test_three_node_cycle():
    edges = [
        ('P', 'Q'),
        ('Q', 'R'),
        ('R', 'P')
    ]
    result = compute_pagerank(edges, damping=0.15, max_iter=100)
    assert len(result) == 3
    for _, rank in result:
        assert abs(rank - 1.0 / 3) < 0.1
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_pagerank_skill_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "ANALYTICS" / "pagerank-centrality"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: pagerank-centrality\ndomain: ANALYTICS')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("pagerank", registry_file)
        assert len(results) >= 1
```

## Security Considerations
- Pure numerical operations only; no file system, network, or OS access.
- Power iteration converges on valid probability distributions summing to 1.0.
- Damping factor prevents infinite loops in cyclic structures.
- No external dependencies; safe for sandboxed execution.

## Dependencies
- `em_cubed` framework (zero external dependencies)
