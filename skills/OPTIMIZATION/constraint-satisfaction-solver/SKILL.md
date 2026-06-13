---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: High
Type: Process
Category: Mathematical Skills
Estimated Execution Time: 2-10 minutes
name: constraint-satisfaction-solver
Source: community
description: Constraint satisfaction solver for combinatorial problems with propagation, backtracking, and optimization support.
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
  - optimization
  - constraint_solving
  - puzzle_solving
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T09:53:00Z"
updated_at: "2026-05-02T09:53:00Z"

## Purpose

Multi-surface constraint satisfaction solver that uses Python for search algorithms, Prolog for logical constraint definition, and Z3 (when available) for mathematical constraint solving.

## Description

This skill solves constraint satisfaction problems by:
- Python for backtracking search, constraint propagation, and optimization
- Prolog for declarative constraint specification and logical inference
- Z3 surface for mathematical constraint solving with SMT capabilities

## Examples

### Sudoku Solver

```
Input: 9x9 grid with some cells filled
Output: Completed grid satisfying Sudoku constraints
```

## Implementation

### Python Search Algorithm

```python
from typing import Dict, List, Optional, Tuple
import copy

class ConstraintSatisfactionSolver:
    """Generic CSP solver with multi-surface support."""
    
    def __init__(self, variables: List[str], domains: Dict[str, List], constraints: List):
        self.variables = variables
        self.domains = domains
        self.constraints = constraints
        self.solutions = []
    
    def is_consistent(self, variable: str, value: any, assignment: Dict) -> bool:
        """Check if assigning value to variable is consistent with constraints."""
        for constraint in self.constraints:
            if constraint["variables"] == [variable]:
                continue
            if variable in constraint["variables"]:
                test_assignment = assignment.copy()
                test_assignment[variable] = value
                if not constraint["check"](test_assignment):
                    return False
        return True
    
    def backtrack_search(self, assignment: Dict = None) -> Optional[Dict]:
        """Recursive backtracking search for solution."""
        if assignment is None:
            assignment = {}
        
        if len(assignment) == len(self.variables):
            return assignment.copy()
        
        # Select unassigned variable (most constrained first)
        unassigned = [v for v in self.variables if v not in assignment]
        variable = min(unassigned, key=lambda v: len(self.domains[v]))
        
        for value in self.domains[variable]:
            if self.is_consistent(variable, value, assignment):
                assignment[variable] = value
                result = self.backtrack_search(assignment)
                if result is not None:
                    return result
                del assignment[variable]
        
        return None
    
    def forward_check(self, variable: str, value: any, domains: Dict) -> Dict:
        """Forward checking for constraint propagation."""
        new_domains = copy.deepcopy(domains)
        new_domains[variable] = [value]
        
        for other_var in self.variables:
            if other_var == variable:
                continue
            
            # Remove values that would violate constraints
            remaining = []
            for other_value in new_domains[other_var]:
                test_assignment = {variable: value, other_var: other_value}
                if all(c["check"](test_assignment) for c in self.constraints 
                       if other_var in c["variables"]):
                    remaining.append(other_value)
            
            new_domains[other_var] = remaining
            if not remaining:
                return {}  # Domain wipeout
        
        return new_domains

def solve_sudoku(grid: List[List[int]]) -> Optional[List[List[int]]]:
    """Solve Sudoku using CSP approach."""
    # Flatten grid to variables
    variables = []
    domains = {}
    
    for r in range(9):
        for c in range(9):
            var = f"cell_{r}_{c}"
            variables.append(var)
            if grid[r][c] != 0:
                domains[var] = [grid[r][c]]
            else:
                domains[var] = list(range(1, 10))
    
    # Define constraints
    def all_different(values: Dict) -> bool:
        vals = [v for k, v in values.items()]
        return len(vals) == len(set(vals))
    
    constraints = []
    
    # Row constraints
    for r in range(9):
        row_vars = [f"cell_{r}_{c}" for c in range(9)]
        constraints.append({
            "variables": row_vars,
            "check": lambda a, vars=row_vars: all_different({k: a[k] for k in vars if k in a})
        })
    
    # Column constraints
    for c in range(9):
        col_vars = [f"cell_{r}_{c}" for r in range(9)]
        constraints.append({
            "variables": col_vars,
            "check": lambda a, vars=col_vars: all_different({k: a[k] for k in vars if k in a})
        })
    
    # Box constraints
    for br in range(3):
        for bc in range(3):
            box_vars = [f"cell_{br*3+r}_{bc*3+c}" for r in range(3) for c in range(3)]
            constraints.append({
                "variables": box_vars,
                "check": lambda a, vars=box_vars: all_different({k: a[k] for k in vars if k in a})
            })
    
    solver = ConstraintSatisfactionSolver(variables, domains, constraints)
    result = solver.backtrack_search()
    
    if result:
        # Convert back to grid
        solved = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                solved[r][c] = result[f"cell_{r}_{c}"]
        return solved
    return None
```

### Prolog Constraint Logic

```prolog
% Sudoku constraints
sudoku(Rows) :-
    length(Rows, 9), maplist(same_length(Rows), Rows),
    maplist(member, Rows, Rows),  % All rows are members
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    Rows = [A,B,C,D,E,F,G,H,I],
    blocks(A,B,C,D,E,F,G,H,I).

blocks([], [], [], [], [], [], [], [], []).
blocks([N1,N2,N3|Ns1], [N4,N5,N6|Ns2], [N7,N8,N9|Ns3],
       D, E, F, G, H, I) :-
    all_distinct([N1,N2,N3,N4,N5,N6,N7,N8,N9]),
    blocks(Ns1, Ns2, Ns3, D, E, F, G, H, I).

all_distinct([]).
all_distinct([X|Xs]) :-
    maplist(dif(X), Xs),
    all_distinct(Xs).

% N-Queens constraint
nqueens(N, Qs) :-
    length(Qs, N),
    Qs ins 1..N,
    all_distinct(Qs),
    all_distinct([Qs[I]-I : I in 1..N]),
    all_distinct([Qs[I]+I : I in 1..N]).

% Map coloring constraint
map_color(Countries, Colorings) :-
    member(Colorings, [
        [france, germany, belgium, netherlands, luxembourg, switzerland, italy]
    ]),
    coloring_constraint(Countries, Colorings).

coloring_constraint([], _).
coloring_constraint([Country|Rest], Colorings) :-
    adjacent(Country, Neighbor),
    memberchk([Country, Color1], Colorings),
    memberchk([Neighbor, Color2], Colorings),
    Color1 \= Color2,
    coloring_constraint(Rest, Colorings).

adjacent(france, germany).
adjacent(france, belgium).
adjacent(france, netherlands).
adjacent(france, luxembourg).
adjacent(france, switzerland).
adjacent(france, italy).
```

### Hy Heuristic Search

```hy
(defn most-constrained-variable [domains assignment]
  "Select variable with smallest domain (MRV heuristic)"
  (let [unassigned (filter (fn [v] (not (in v (keys assignment)))) (keys domains))]
    (apply min unassigned :key (fn [v] (len (get domains v))))))

(defn least-constraining-value [var domains constraints assignment]
  "Order values by least constraining (LCV)"
  (let [value-counts (for [value (get domains var)]
                       [value (count-constraints value var domains constraints assignment)])]
    (sorted value-counts :key (fn [pair] (get pair 1)))))

(defn count-constraints [value var domains constraints assignment]
  "Count how many constraints would be affected"
  (sum (map (fn [constraint]
              (let [other-vars (remove (fn [v] (= v var)) constraint)]
                (len (filter (fn [other-var]
                              (> (len (get domains other-var)) 1))
                            other-vars))))
            constraints)))

(defn ac-3-enforce [constraints domains]
  "Arc consistency AC-3 algorithm"
  (let [queue (list-constraints-as-arcs constraints)]
    (while queue
      (let [[xi xj] (pop queue)
            revised (revise xi xj constraints domains)]
        (when revised
          (setv domains (assoc domains xi revised))
          (for [xk (get-neighbors xi constraints)]
            (when (and (not (= xk xj)) (not (in [xk xi] queue)))
              (append queue [xi xk]))))))
    domains))
```

## Testing

```python
# Test CSP solver
from skills.constraint_satisfaction_solver import ConstraintSatisfactionSolver

# Simple problem: A + B = 5, A - B = 1
variables = ["A", "B"]
domains = {"A": [1, 2, 3, 4], "B": [1, 2, 3, 4]}

def sum_constraint(assignment):
    return assignment.get("A", 0) + assignment.get("B", 0) == 5

def diff_constraint(assignment):
    return assignment.get("A", 0) - assignment.get("B", 0) == 1

constraints = [
    {"variables": ["A", "B"], "check": sum_constraint},
    {"variables": ["A", "B"], "check": diff_constraint}
]

solver = ConstraintSatisfactionSolver(variables, domains, constraints)
result = solver.backtrack_search()
assert result in [{"A": 3, "B": 2}, {"A": 2, "B": 3}]
```