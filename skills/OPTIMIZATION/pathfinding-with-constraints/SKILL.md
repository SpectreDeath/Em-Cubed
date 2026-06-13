---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: High
Type: Process
Category: Graph Skills
Estimated Execution Time: 2-5 minutes
name: pathfinding-with-constraints
Source: community
description: Pathfinding with constraints for graph traversal under resource limits, time windows, and hard constraints.
compatibility: UNIVERSAL
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
origin: manual
triggers:
  - routing
  - navigation
  - graph_search
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T09:53:00Z"
updated_at: "2026-05-02T09:53:00Z"

## Purpose

Multi-surface pathfinding solver that combines Python for graph algorithms, Prolog for logical constraint satisfaction, and Hy for heuristic path evaluation with multiple objectives.

## Description

This skill solves complex pathfinding problems by:
- Python for Dijkstra, A*, and constraint-aware path algorithms
- Prolog for logical rule validation (e.g., traffic restrictions, time-dependent constraints)
- Hy for fuzzy scoring and multi-objective optimization with uncertainty

## Examples

### Urban Navigation

```
Input: Start, goal, and constraints (avoid tolls, traffic-dependent rules)
Output: Optimal path with constraint compliance and time estimates
```

## Implementation

### Python Graph Algorithms

```python
from typing import Dict, List, Tuple, Optional, Set
import heapq
from dataclasses import dataclass, field
from enum import Enum

class EdgeType(Enum):
    NORMAL = "normal"
    TOLL = "toll"
    HIGHWAY = "highway"
    RESTRICTED = "restricted"

@dataclass
class Node:
    id: str
    x: float = 0.0
    y: float = 0.0
    attributes: Dict = field(default_factory=dict)

@dataclass
class Edge:
    source: str
    target: str
    weight: float
    edge_type: EdgeType = EdgeType.NORMAL
    constraints: List[str] = field(default_factory=list)
    time_dependent: bool = False

class ConstraintAwarePathfinder:
    """Pathfinder with constraint support."""
    
    def __init__(self, nodes: Dict[str, Node], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges
        self.adjacency: Dict[str, List[Tuple[str, float, Edge]]] = {}
        self._build_adjacency()
    
    def _build_adjacency(self) -> None:
        """Build adjacency list from edges."""
        for edge in self.edges:
            if edge.source not in self.adjacency:
                self.adjacency[edge.source] = []
            self.adjacency[edge.source].append((edge.target, edge.weight, edge))
    
    def dijkstra(self, start: str, goal: str, 
                 constraints: Set[str] = None) -> Optional[List[str]]:
        """Dijkstra algorithm with constraint filtering."""
        if constraints is None:
            constraints = set()
        
        pq = [(0, start, [start])]
        visited = {start}
        
        while pq:
            cost, node, path = heapq.heappop(pq)
            
            if node == goal:
                return path
            
            for neighbor, weight, edge in self.adjacency.get(node, []):
                # Check constraints
                if any(c in edge.constraints for c in constraints):
                    continue
                if edge.edge_type == EdgeType.TOLL and "avoid_tolls" in constraints:
                    continue
                if edge.edge_type == EdgeType.RESTRICTED and "avoid_restricted" in constraints:
                    continue
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))
        
        return None
    
    def astar(self, start: str, goal: str, 
              constraints: Set[str] = None,
              heuristic: callable = None) -> Optional[List[str]]:
        """A* algorithm with constraint filtering."""
        if constraints is None:
            constraints = set()
        
        if heuristic is None:
            goal_node = self.nodes.get(goal, Node(goal))
            heuristic = lambda n: self._euclidean_distance(self.nodes.get(n, Node(n)), goal_node)
        
        pq = [(0, 0, start, [start])]  # (f_score, g_score, node, path)
        visited = {start}
        
        while pq:
            f_score, g_score, node, path = heapq.heappop(pq)
            
            if node == goal:
                return path
            
            for neighbor, weight, edge in self.adjacency.get(node, []):
                if any(c in edge.constraints for c in constraints):
                    continue
                if edge.edge_type == EdgeType.TOLL and "avoid_tolls" in constraints:
                    continue
                
                new_g = g_score + weight
                new_f = new_g + heuristic(neighbor)
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))
        
        return None
    
    def _euclidean_distance(self, n1: Node, n2: Node) -> float:
        """Calculate Euclidean distance between nodes."""
        return ((n1.x - n2.x) ** 2 + (n1.y - n2.y) ** 2) ** 0.5
    
    def multi_objective_search(self, start: str, goal: str,
                                constraint_sets: List[Set[str]],
                                weights: List[float]) -> Dict[str, Optional[List[str]]]:
        """Run path search with multiple constraint sets."""
        results = {}
        for i, constraints in enumerate(constraint_sets):
            path = self.astar(start, goal, constraints)
            results[f"path_{i}"] = path
        return results

def detect_negative_cycles(nodes: Dict[str, Node], edges: List[Edge]) -> List[List[str]]:
    """Detect negative weight cycles (Bellman-Ford)."""
    # Initialize distances
    dist = {n: float("inf") for n in nodes}
    dist[list(nodes.keys())[0]] = 0
    
    # Relax edges
    for _ in range(len(nodes) - 1):
        for edge in edges:
            if dist[edge.source] + edge.weight < dist[edge.target]:
                dist[edge.target] = dist[edge.source] + edge.weight
    
    # Check for negative cycles
    cycles = []
    for edge in edges:
        if dist[edge.source] + edge.weight < dist[edge.target]:
            # Negative cycle detected
            cycle = [edge.source, edge.target]
            cycles.append(cycle)
    
    return cycles
```

### Prolog Constraint Logic

```prolog
% Pathfinding constraints
valid_path([], _).
valid_path([_], _).
valid_path([From, To | Rest], Constraints) :-
    valid_edge(From, To, Edge),
    satisfies_constraints(Edge, Constraints),
    valid_path([To | Rest], Constraints).

% Edge validity
valid_edge(Node1, Node2, Edge) :-
    edge(Node1, Node2, Edge).

valid_edge(Node1, Node2, Edge) :-
    edge(Node2, Node1, Edge).  % Bidirectional

% Constraint satisfaction
satisfies_constraints(Edge, RequiredConstraints) :-
    findall(C, edge_constraint(Edge, C), EdgeConstraints),
    \+ (member(Req, RequiredConstraints), \+ member(Req, EdgeConstraints)).

% Time-dependent constraints
time_allowed(Route, DepartureTime) :-
    forall(member(Edge, Route),
           (edge_time_constraint(Edge, StartTime, EndTime),
            DepartureTime >= StartTime,
            DepartureTime =< EndTime)).

% Avoid certain edge types
avoid_tolls(Path) :-
    \+ (member(Edge, Path), edge_type(Edge, toll)).

avoid_highways(Path) :-
    \+ (member(Edge, Path), edge_type(Edge, highway)).

% Vehicle-specific constraints
vehicle_compatible(Vehicle, Path) :-
    vehicle_type(Vehicle, Type),
    findall(Ok, (member(Edge, Path), vehicle_allowed(Edge, Type, Ok)), Results),
    member(all_ok, Results).

% Traffic rule constraints
traffic_rule_violation(Path, Violation) :-
    member(Edge, Path),
    edge_constraint(Edge, high_traffic),
    current_hour(Hour),
    (Hour >= 7, Hour =< 9; Hour >= 16, Hour =< 18),
    Violation = rush_hour_congestion.
```

### Hy Multi-Objective Scoring

```hy
(defn path-score [path weights factors]
  "Calculate composite path score"
  (let [length-score (/ 1 (+ 1 (len path)))
        time-score (get factors "time" 1.0)
        cost-score (- 1 (get factors "cost" 0.5))
        safety-score (get factors "safety" 0.8)]
    (+ (* (get weights "length" 0.3) length-score)
       (* (get weights "time" 0.4) time-score)
       (* (get weights "cost" 0.2) cost-score)
       (* (get weights "safety" 0.1) safety-score))))

(defn pareto-front [paths scores]
  "Find Pareto optimal paths"
  (filter (fn [path]
            (let [path-score (get scores path)]
              (not (some (fn [other-path]
                           (and (not (= path other-path))
                                (dominates (get scores other-path) path-score)))
                         paths))))
          paths))

(defn dominates [score1 score2]
  "Check if score1 dominates score2"
  (and (<= (get score1 "time") (get score2 "time"))
       (<= (get score1 "cost") (get score2 "cost"))
       (<= (get score1 "risk") (get score2 "risk"))
       (or (< (get score1 "time") (get score2 "time"))
           (< (get score1 "cost") (get score2 "cost"))
           (< (get score1 "risk") (get score2 "risk")))))

(defn fuzzy-time-estimate [base-time uncertainty]
  "Apply fuzzy adjustment to time estimates"
  (let [delta (* uncertainty (- (random) 0.5))
        fuzzy-time (+ base-time delta)]
    {:best-time (- fuzzy-time (* 2 uncertainty))
     :expected fuzzy-time
     :worst-case (+ fuzzy-time (* 2 uncertainty))}))

(defn multi-objective-normalize [values objective-types]
  "Normalize objectives (min/max) for scoring"
  (for [i (range (len values))]
    (let [vals (map (fn [v] (get v i)) values)
          obj-type (get objective-types i)]
      (cond
        (= obj-type "min") (/ (- (max vals) (get vals i)) (- (max vals) (min vals) 0.001))
        (= obj-type "max") (/ (- (get vals i) (min vals)) (- (max vals) (min vals) 0.001))
        True 0.5))))

(defn dynamic-weight-adjustment [current-weights performance-history learning-rate]
  "Adjust weights based on outcome feedback"
  (let [errors (map (fn [perf] (- 1 (get perf "achieved") (get perf "expected"))) performance-history)
        adjustments (map (fn [err w] (+ w (* learning-rate err))) errors current-weights)
        normalized (let [total (sum adjustments)]
                     (map (fn [w] (/ w total)) adjustments))]
    {:old-weights current-weights :new-weights normalized}))
```

## Testing

> **Note:** These tests use direct imports for standalone illustration. In production, use the `SkillExecutor` which injects surface plugins via `context["surfaces"]`. See [Multi-Surface Guide](../../docs/MULTI_SURFACE_GUIDE.md) for the recommended pattern.

### Python Surface Test

```python
# Test pathfinder (standalone - uses direct imports)
from skills.pathfinding_with_constraints import ConstraintAwarePathfinder, Node, Edge, EdgeType

nodes = {
    "A": Node("A", 0, 0),
    "B": Node("B", 1, 1),
    "C": Node("C", 2, 0),
    "D": Node("D", 1, -1)
}

edges = [
    Edge("A", "B", 1.5),
    Edge("B", "C", 2.0),
    Edge("A", "D", 1.0),
    Edge("D", "C", 1.5, EdgeType.TOLL)
]

pf = ConstraintAwarePathfinder(nodes, edges)
path = pf.dijkstra("A", "C")
assert path is not None
assert path[0] == "A"
assert path[-1] == "C"

# Test with constraints
path_no_tolls = pf.dijkstra("A", "C", {"avoid_tolls"})
assert path_no_tolls == ["A", "D", "C"]
```

### Multi-Surface Integration Test (Recommended Pattern)

```python
# Production pattern: use SkillExecutor with context injection
from em_cubed.skills.executor import SkillExecutor, SkillExecutionRequest

executor = SkillExecutor(plugin_manager, registry, skills_dir)
request = SkillExecutionRequest(
    skill_id="OPTIMIZATION/pathfinding-with-constraints",
    input_data={
        "nodes": {"A": {"x": 0, "y": 0}, "B": {"x": 1, "y": 1}},
        "edges": [{"source": "A", "target": "B", "weight": 1.5}],
        "start": "A",
        "goal": "B",
        "constraints": []
    }
)
result = await executor.execute(request)
assert result.success
```