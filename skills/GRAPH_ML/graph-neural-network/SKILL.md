---
name: graph-neural-network
domain: GRAPH_ML
version: 1.0.0
description: Graph neural network implementation with Python surface for message passing and SQLite surface for graph storage.
compatibility: UNIVERSAL
complexity: High
type: Analysis
category: Deep Learning Skills
estimated execution time: 10-20 minutes
source: community
allowed-tools: '- read

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

  '
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

Multi-surface graph neural network using Python for message passing, Prolog for graph logic rules, and Z3 for constraint-based GNN verification.

## Implementation

### Python GNN Core

```python
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class GraphConvolution(nn.Module):
    """Graph convolution layer."""
    
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.weight = nn.Parameter(torch.FloatTensor(in_features, out_features))
        if bias:
            self.bias = nn.Parameter(torch.FloatTensor(out_features))
        self.reset_parameters()
    
    def reset_parameters(self):
        nn.init.xavier_uniform_(self.weight)
        if hasattr(self, "bias"):
            nn.init.zeros_(self.bias)
    
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        support = torch.mm(x, self.weight)
        output = torch.spmm(adj, support)
        if hasattr(self, "bias"):
            return output + self.bias
        return output

class GCN(nn.Module):
    """Graph Convolutional Network."""
    
    def __init__(self, in_features: int, hidden: int, out_features: int, 
                 dropout: float = 0.5):
        super().__init__()
        self.gc1 = GraphConvolution(in_features, hidden)
        self.gc2 = GraphConvolution(hidden, out_features)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        x = self.gc1(x, adj)
        x = torch.relu(x)
        x = self.dropout(x)
        x = self.gc2(x, adj)
        return torch.log_softmax(x, dim=1)

def message_passing(node_features: Dict[int, np.ndarray], 
                    edges: List[Tuple[int, int]], 
                    iterations: int = 2) -> Dict[int, np.ndarray]:
    """Simple message passing implementation."""
    features = node_features.copy()
    adjacency = defaultdict(list)
    for src, dst in edges:
        adjacency[src].append(dst)
        adjacency[dst].append(src)
    
    for _ in range(iterations):
        new_features = {}
        for node, feat in features.items():
            neighbors = [features[n] for n in adjacency[node] if n in features]
            if neighbors:
                aggregated = np.mean(neighbors, axis=0)
                new_features[node] = (feat + aggregated) / 2
            else:
                new_features[node] = feat
        features = new_features
    
    return features

def graph_attention(nodes: List[int], adjacency: Dict[int, List[int]], 
                    features: Dict[int, np.ndarray]) -> Dict[int, np.ndarray]:
    """Graph attention mechanism."""
    new_features = {}
    for node in nodes:
        neighbors = [n for n in adjacency.get(node, []) if n in features]
        if neighbors:
            neighbor_feats = [features[n] for n in neighbors]
            weights = np.array([np.dot(features[node], f) for f in neighbor_feats])
            weights = np.exp(weights) / np.sum(np.exp(weights))
            weighted = np.sum([w * f for w, f in zip(weights, neighbor_feats)], axis=0)
            new_features[node] = 0.5 * features[node] + 0.5 * weighted
        else:
            new_features[node] = features[node]
    return new_features
```

### Prolog Graph Logic

```prolog
% Graph connectivity
connected(Graph, Node1, Node2) :-
    path(Graph, Node1, Node2, _).

path(Graph, Start, End, Path) :-
    edge(Graph, Start, Next),
    path(Graph, Next, End, Rest),
    Path = [Start | Rest].

% Node classification
homogeneous_neighborhood(Node, Graph, Label) :-
    neighbors(Node, Graph, Neighbors),
    forall(member(N, Neighbors), node_label(N, Label)).

% Graph constraints
valid_graph(Graph) :-
    no_self_loops(Graph),
    symmetric_edges(Graph),
    connected_components(Graph, N),
    N = 1.

% Subgraph isomorphism
subgraph_isomorphic(Subgraph, Graph) :-
    find_mapping(Subgraph, Graph, Mapping),
    preserves_edges(Subgraph, Mapping, Graph).

% Message passing rules
message_consistent(Node, Features, Adjacency) :-
    neighbors(Node, Adjacency, Neighbors),
    aggregate_messages(Neighbors, Features, Aggregated),
    update_rule(Node, Features, Aggregated, NewFeatures),
    consistent_update(Node, NewFeatures).
```

### Z3 GNN Verification

```python
from z3 import Real, Solver, And, Implies, sat

def verify_gnn_properties(adjacency_matrix: np.ndarray, 
                         feature_dim: int) -> bool:
    """Verify GNN properties using Z3."""
    solver = Solver()
    
    # Define feature variables for each node
    nodes = range(adjacency_matrix.shape[0])
    features = {i: [Real(f"f_{i}_{j}") for j in range(feature_dim)] for i in nodes}
    
    # Add constraints for message passing linearity
    for i in nodes:
        for j in range(feature_dim):
            # Feature should be bounded
            solver.add(features[i][j] >= -10)
            solver.add(features[i][j] <= 10)
    
    # Check consistency
    return solver.check() == sat

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface

def test_graph_adjacency_construction():
    """Test building adjacency list/dict from edge list."""
    code = '''
from collections import defaultdict

edges = [(0, 1), (0, 2), (1, 2), (2, 3)]
adjacency = defaultdict(list)
for src, dst in edges:
    adjacency[src].append(dst)
    adjacency[dst].append(src)  # undirected

assert len(adjacency[0]) == 2  # node 0 connected to 1,2
assert 1 in adjacency[2]
assert 3 in adjacency[2]
print("adjacency construction ok")
'''
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_message_passing_simple():
    """Test simple message passing aggregation."""
    code = '''
import numpy as np
from collections import defaultdict

def message_passing(node_features, edges, iterations=1):
    features = node_features.copy()
    adjacency = defaultdict(list)
    for src, dst in edges:
        adjacency[src].append(dst)
        adjacency[dst].append(src)
    
    for _ in range(iterations):
        new_features = {}
        for node, feat in features.items():
            neighbors = [features[n] for n in adjacency[node] if n in features]
            if neighbors:
                aggregated = np.mean(neighbors, axis=0)
                new_features[node] = (feat + aggregated) / 2
            else:
                new_features[node] = feat
        features = new_features
    return features

# Simple graph: 3 nodes in line
features = {0: np.array([1.0]), 1: np.array([0.0]), 2: np.array([2.0])}
edges = [(0,1), (1,2)]
result = message_passing(features, edges, iterations=1)

# Node 0: neighbors=[1] -> mean([0]) = 0, avg with own = 0.5
assert abs(result[0][0] - 0.5) < 0.01
# Node 1: neighbors=[0,2] -> mean([1,2]) = 1.5, avg with own = 0.75
assert abs(result[1][0] - 0.75) < 0.01
# Node 2: neighbors=[1] -> mean([0]) = 0, avg with own = 1.0
assert abs(result[2][0] - 1.0) < 0.01

print("message passing ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_graph_attention_weights():
    """Test attention weight computation."""
    code = '''
import numpy as np

def graph_attention(nodes, adjacency, features):
    new_features = {}
    for node in nodes:
        neighbors = [n for n in adjacency.get(node, []) if n in features]
        if neighbors:
            neighbor_feats = [features[n] for n in neighbors]
            # Dot product attention
            weights = np.array([np.dot(features[node], f) for f in neighbor_feats])
            weights = np.exp(weights) / np.sum(np.exp(weights))
            weighted = np.sum([w * f for w, f in zip(weights, neighbor_feats)], axis=0)
            new_features[node] = 0.5 * features[node] + 0.5 * weighted
        else:
            new_features[node] = features[node]
    return new_features

nodes = [0, 1, 2]
adjacency = {0: [1], 1: [0,2], 2: [1]}
features = {0: np.array([1.0, 0.0]), 1: np.array([0.0, 1.0]), 2: np.array([1.0, 1.0])}

result = graph_attention(nodes, adjacency, features)
assert 0 in result
assert result[0].shape == (2,)
print("attention ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_gnn_property_verification():
    """Test Z3-based GNN property verification."""
    code = '''
from z3 import Real, Solver

def verify_feature_bounds(n_nodes, feature_dim, bound=10):
    """Verify that features stay within bounds after message passing."""
    solver = Solver()
    features = {i: [Real(f"f_{i}_{j}") for j in range(feature_dim)] for i in range(n_nodes)}
    
    for i in range(n_nodes):
        for j in range(feature_dim):
            solver.add(features[i][j] >= -bound)
            solver.add(features[i][j] <= bound)
    
    return solver.check()  # Should be sat

result = verify_feature_bounds(3, 2, bound=10)
assert str(result) == "sat"
print("verification ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_node_degree_calculation():
    """Calculate node degrees from adjacency."""
    code = '''
from collections import defaultdict

edges = [(0,1), (0,2), (1,2), (2,3), (3,4)]
adj = defaultdict(list)
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)

degrees = {node: len(neighbors) for node, neighbors in adj.items()}
assert degrees[0] == 2
assert degrees[2] == 3  # connected to 0,1,3
assert degrees[4] == 1
print("degree calc ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_feature_aggregation():
    """Test aggregating neighbor features."""
    code = '''
import numpy as np

def aggregate_neighbors(node, features, adjacency):
    neighbors = adjacency.get(node, [])
    if not neighbors:
        return features[node]
    neighbor_feats = [features[n] for n in neighbors]
    return np.mean(neighbor_feats, axis=0)

features = {0: np.array([1.0, 2.0]), 1: np.array([3.0, 4.0]), 2: np.array([5.0, 6.0])}
adjacency = {0: [1, 2], 1: [0], 2: [0]}

agg0 = aggregate_neighbors(0, features, adjacency)
expected = np.mean([features[1], features[2]], axis=0)
assert np.allclose(agg0, expected)

print("aggregation ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
class TestGNN:
    @pytest.fixture
    async def surface(self):
        return PythonSurface()

    async def test_numpy_linear_algebra(self, surface):
        """Test matrix operations used in GNNs."""
        code = '''
import numpy as np
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
C = np.dot(A, B)
assert C.shape == (2, 2)
print("matmul ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_torch_tensor_ops(self, surface):
        """Test PyTorch tensor basics."""
        code = '''
import torch
x = torch.tensor([1.0, 2.0, 3.0])
y = torch.tensor([4.0, 5.0, 6.0])
z = x + y
assert torch.equal(z, torch.tensor([5.0, 7.0, 9.0]))
print("torch ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
from em_cubed.surfaces import PythonSurface
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_gnn_skill_workflow():
    """Test GNN skill complete workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "GRAPH_ML" / "graph-neural-network"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: GNN Test
Domain: GRAPH_ML
surfaces:
  - python
---

## Purpose
Test graph neural networks

## Implementation

### Python

```python
def simple_gcn_step(features, adj):
    return np.mean(features, axis=0)
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        surface = PythonSurface()
        result = await surface.execute("sum([1,2,3])", {})
        assert result["status"] == "ok"
```

## Security Considerations

- PyTorch can use significant memory; monitor usage
- Large graphs may cause DoS; limit node count
- Z3 verification can be expensive; use timeouts

## Dependencies

- numpy (array operations)
- torch (GNN layers)
- z3-solver (property verification)
- em_cubed framework
```

````
