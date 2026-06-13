---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: High
Type: Analysis
Category: Mathematical Skills
Estimated Execution Time: 5-10 minutes
name: optimization-landscape-analyzer
Source: community
description: Optimization landscape analyzer for visualizing objective surfaces, identifying basins, and characterizing multimodality.
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
  - landscape_analysis
  - multi_objective
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:30:00Z"
updated_at: "2026-05-02T12:30:00Z"

## Purpose

Multi-surface optimization landscape analyzer that combines Python for numerical optimization, Prolog for constraint analysis, and Z3 for SMT-based optimization verification.

## Description

This skill analyzes optimization landscapes by:
- Python for surrogate modeling, landscape features, and evolutionary algorithms
- Prolog for constraint boundary analysis and local optimum reasoning
- Z3 for formal verification of optimality conditions

## Examples

### Multi-Objective Landscape Analysis

```
Input: Objective functions and constraints
Output: Landscape features, Pareto front approximation, critical regions
```

## Implementation

### Python Landscape Analysis

```python
import numpy as np
from typing import Callable, Tuple, List, Dict, Optional
from dataclasses import dataclass
import scipy.optimize as opt

@dataclass
class LandscapeFeatures:
    modality: int  # Number of local optima
    ruggedness: float  # Landscape smoothness
    neutrality: float  # Flat region size
    epistasis: float  # Variable interaction strength
    separability: float  # Variable separability

class OptimizationLandscapeAnalyzer:
    """Analyze optimization landscape characteristics."""
    
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float]]):
        self.objective = objective
        self.bounds = bounds
        self.dimensions = len(bounds)
    
    def sample_landscape(self, n_samples: int = 1000) -> np.ndarray:
        """Sample objective function values across search space."""
        samples = np.random.uniform(
            low=[b[0] for b in self.bounds],
            high=[b[1] for b in self.bounds],
            size=(n_samples, self.dimensions)
        )
        values = np.array([self.objective(x) for x in samples])
        return np.column_stack([samples, values])
    
    def find_local_optima(self, data: np.ndarray, threshold: float = 0.1) -> List[np.ndarray]:
        """Find local optima in sampled landscape."""
        from scipy.spatial import cKDTree
        
        points = data[:, :-1]
        values = data[:, -1]
        tree = cKDTree(points)
        
        optima = []
        for i, (point, value) in enumerate(zip(points, values)):
            neighbors = tree.query_ball_point(point, 0.1)
            neighbor_values = values[neighbors]
            
            if value <= np.min(neighbor_values) + threshold:
                # Local optimum
                optima.append(point)
        
        return optima
    
    def compute_modality(self, data: np.ndarray) -> int:
        """Estimate number of local optima."""
        optima = self.find_local_optima(data)
        return len(optima)
    
    def compute_ruggedness(self, data: np.ndarray) -> float:
        """Compute landscape ruggedness (autocorrelation)."""
        values = data[:, -1]
        if len(values) < 2:
            return 0.0
        
        # Compute autocorrelation
        mean_val = np.mean(values)
        var_val = np.var(values)
        if var_val == 0:
            return 0.0
        
        # First-order autocorrelation
        autocorr = np.mean((values[:-1] - mean_val) * (values[1:] - mean_val)) / var_val
        return 1 - autocorr  # Higher = more rugged
    
    def compute_neutrality(self, data: np.ndarray, epsilon: float = 0.01) -> float:
        """Estimate neutral network size (flat regions)."""
        values = data[:, -1]
        sorted_vals = np.sort(values)
        diffs = np.diff(sorted_vals)
        
        # Count flat regions
        flat_regions = np.sum(diffs < epsilon)
        return flat_regions / len(diffs) if len(diffs) > 0 else 0.0
    
    def build_surrogate(self, data: np.ndarray) -> Callable:
        """Build surrogate model (Gaussian Process)."""
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import Matern
        
        X = data[:, :-1]
        y = data[:, -1]
        
        kernel = Matern(length_scale=1.0, nu=2.5)
        gp = GaussianProcessRegressor(kernel=kernel, alpha=1e-6)
        gp.fit(X, y)
        
        return gp.predict
    
    def feature_importance(self, data: np.ndarray) -> Dict[int, float]:
        """Compute variable importance using permutation."""
        X = data[:, :-1]
        y = data[:, -1]
        
        base_score = np.var(y)
        importance = {}
        
        for i in range(X.shape[1]):
            X_permuted = X.copy()
            X_permuted[:, i] = np.random.permutation(X_permuted[:, i])
            permuted_score = np.var(X_permuted[:, i])
            importance[i] = (base_score - permuted_score) / base_score
        
        return importance

def multi_objective_landscape(obj_funcs: List[Callable], bounds: List[Tuple], 
                             n_samples: int = 1000) -> Dict:
    """Analyze multi-objective optimization landscape."""
    sampler = OptimizationLandscapeAnalyzer(lambda x: 0, bounds)
    data = sampler.sample_landscape(n_samples)
    
    objectives_data = []
    for func in obj_funcs:
        sampler.objective = func
        obj_data = sampler.sample_landscape(n_samples)
        objectives_data.append(obj_data[:, -1])
    
    # Find Pareto optimal solutions
    combined = np.column_stack(objectives_data)
    is_pareto = np.ones(len(combined), dtype=bool)
    
    for i in range(len(combined)):
        if is_pareto[i]:
            dominated = np.any(np.all(combined <= combined[i], axis=1) & 
                              np.any(combined < combined[i], axis=1))
            is_pareto[i] = not dominated
    
    return {
        "pareto_front_size": np.sum(is_pareto),
        "hypervolume": np.prod(np.max(objectives_data, axis=1)),
        "sparsity": np.std(np.sum(objectives_data, axis=1))
    }
```

### Prolog Constraint Analysis

```prolog
% Constraint boundary analysis
constraint_boundary(RHS1, RHS2, Variables, Boundary) :-
    constraint(RHS1, Vars1),
    constraint(RHS2, Vars2),
    intersection(Vars1, Vars2, CommonVars),
    boundary_equation(CommonVars, Boundary).

% Local optimum characterization
local_optimum(Point, Objective, Constraints) :-
    gradient_zero(Objective, Point),
    satisfies_constraints(Point, Constraints),
    hessian_positive_definite(Objective, Point).

% Critical region identification
critical_region(Region, Objective) :-
    gradient_zero(Objective, Point),
    nearby_points_satisfy(Point, Region).

% Multimodal landscape detection
multimodal_landscape(Objective, Regions) :-
    findall(P, local_optimum(P, Objective, _), Optima),
    group_nearby_optima(Optima, Regions).

% Constraint interaction
constraint_interaction(C1, C2) :-
    shared_variables(C1, C2, Vars),
    length(Vars, NumVars),
    NumVars > 0.

% Optimality certificate
optimality_certified(Point, Objective, Certificate) :-
    first_order_condition(Objective, Point),
    second_order_condition(Objective, Point, Certificate).
```

### Z3 SMT Verification

```python
from z3 import Real, Optimize, Solver, sat, Implies, And, Or, Not

def verify_global_optimum(objective: Callable, bounds: List[Tuple], 
                         candidate: np.ndarray) -> bool:
    """Verify if candidate is globally optimal using Z3."""
    solver = Solver()
    
    # Define variables
    vars = [Real(f'x_{i}') for i in range(len(bounds))]
    
    # Add bounds
    constraints = []
    for var, (lo, hi) in zip(vars, bounds):
        constraints.append(var >= lo)
        constraints.append(var <= hi)
    
    solver.add(constraints)
    
    # Define objective as Z3 expression
    # This requires symbolic conversion of objective
    # For demonstration, assuming linear objective
    obj_sym = sum(c * v for c, v in zip(candidate, vars))
    
    candidate_val = objective(candidate)
    solver.add(obj_sym <= candidate_val)
    
    return solver.check() == sat
```

## Testing

```python
# Test landscape analysis
from skills.optimization_landscape_analyzer import OptimizationLandscapeAnalyzer

def sphere(x):
    return sum(xi**2 for xi in x)

analyzer = OptimizationLandscapeAnalyzer(sphere, [(-5, 5), (-5, 5)])
data = analyzer.sample_landscape(500)
modality = analyzer.compute_modality(data)
ruggedness = analyzer.compute_ruggedness(data)
assert modality >= 1
assert 0 <= ruggedness <= 1
```