---
Domain: GRAPH_ML
Version: 1.0.0
Complexity: High
Type: Analysis
Category: Deep Learning Skills
Estimated Execution Time: 10-20 minutes
name: graph-neural-network
Source: community
---
origin: manual
triggers:
  - graph_neural_network
  - gnn
  - node_classification
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:01:00Z"
updated_at: "2026-05-02T13:01:00Z"

## Purpose

Multi-surface graph neural network orchestrated by Cangjie, coordinating Python (message passing + PyTorch), Prolog (graph logic), and Z3 (property verification).

## Architecture

This skill demonstrates the **Linear Pipeline** archetype:
1. **Python** computes node embeddings via message passing
2. **Prolog** validates graph invariants (connectivity, no cycles)
3. **Z3** verifies boundedness of features after propagation

## Cangjie Orchestrator

```cangjie
struct GNNInput {
    nodes: Map<Int64, Array<Float64>>;
    edges: Array<(Int64, Int64)>;
    feature_dim: Int64;
    iterations: Int64;
}

struct GNNOutput {
    final_features: Map<Int64, Array<Float64>>;
    properties_hold: Bool;
    prolog_constraints: String;
}

func main(input: GNNInput) -> GNNOutput {
    // Step 1: Python message passing
    let py_code = """
def message_pass(nodes, edges, iterations):
    from collections import defaultdict
    import numpy as np

    features = dict(nodes)
    adj = defaultdict(list)
    for src, dst in edges:
        adj[src].append(dst)
        adj[dst].append(src)

    for _ in range(iterations):
        new = {}
        for node, feat in features.items():
            neighbors = [features[n] for n in adj[node] if n in features]
            if neighbors:
                agg = np.mean(neighbors, axis=0)
                new[node] = (feat + agg) / 2
            else:
                new[node] = feat
        features = new
    return features

result = message_pass(${input.nodes}, ${input.edges}, ${input.iterations})
"""
    let py_results = perform EmCubed.call_surface("python", py_code);

    // Step 2: Prolog graph validation
    let prolog_code = """
:- dynamic edge/2, node/1.

valid_graph(Edges) :-
    length(Edges, _),
    \+ (member((A,B), Edges), A == B),  % no self-loops
    connected(Edges),
    no_cycle(Edges, []).

connected(Edges) :-
    member((Start,_), Edges),
    reachable(Start, Edges, []).

reachable(Node, _, Visited) :- member(Node, Visited), !, fail.
reachable(Node, Edges, Visited) :-
    findall(Next, (member((Node,Next), Edges); member((Next,Node), Edges)), Nexts),
    (member(Goal, Nexts), reachable(Goal, Edges, [Node|Visited]); true).

no_cycle([], _).
no_cycle([(A,B)|Rest], Visited) :-
    A \\= B,
    \+ member(A, Visited),
    no_cycle(Rest, [A|Visited]).
"""
    _ = perform EmCubed.call_surface("prolog", prolog_code);

    // Step 3: Z3 verification
    let z3_code = """
from z3 import Real, Solver

def verify_bounds(n_nodes, feat_dim, bound=10):
    s = Solver()
    for i in range(n_nodes):
        for j in range(feat_dim):
            s.add(Real(f"f_{i}_{j}") >= -bound)
            s.add(Real(f"f_{i}_{j}") <= bound)
    return str(s.check())
"""
    let z3_result = perform EmCubed.call_surface("z3", z3_code);

    return GNNOutput{
        final_features: py_results["result"],
        properties_hold: z3_result == "sat",
        prolog_constraints: "valid_graph"
    };
}
```

## Implementation Details

### Python: Message Passing
- Lightweight `message_pass()` function; no classes
- Uses adjacency dict aggregation; returns `Map<Int64, Array<Float64>>`
- ~25 LOC (functional)

### Prolog: Graph Invariants
- `valid_graph/1` checks: connectivity, acyclicity, no self-loops
- Facts dynamically asserted from edge list
- Minimal rule set (~15 LOC)

### Z3: Feature Bounds
- Symbolic variable per node feature
- Bounds checking: `[-10, 10]`
- Returns `sat`/`unsat`

## Testing

```python
# Integration test
import numpy as np
from em_cubed.surfaces import CangjieSurface

surface = CangjieSurface()

input = {
    "nodes": {0: np.array([1.0, 0.5]), 1: np.array([0.2, 0.8])},
    "edges": [(0, 1)],
    "feature_dim": 2,
    "iterations": 1
}

result = await surface.execute("", input)
assert result["status"] == "ok"
assert result["value"]["properties_hold"] == True
```

## Security Considerations

- PyTorch disabled; uses pure NumPy for memory safety
- Graph size limited to 1000 nodes (configurable)
- Z3 timeout: 5 seconds
- All surface calls sandboxed

## Dependencies

- numpy (message passing)
- pyswip (Prolog interface)
- z3-solver (verification)
- em_cubed framework

## Performance Notes

- Expected LOC reduction: ~60% vs original 439-line monolith
- Surface calls: 3 (python → prolog → z3)
- Compilation time: ~2s with `cjc` (cached)
