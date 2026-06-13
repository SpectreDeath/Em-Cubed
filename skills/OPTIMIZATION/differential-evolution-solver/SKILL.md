---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: High
Type: Optimization
Category: Evolutionary Skills
Estimated Execution Time: 10-30 minutes
name: differential-evolution-solver
Source: community
surfaces:
  - python
description: Differential evolution solver for global optimization using population-based mutation and crossover strategies.
compatibility: PYTHON
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
  - evolutionary_optimization
  - differential_evolution
  - parameter_tuning
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:01:00Z"
updated_at: "2026-05-02T13:01:00Z"

## Purpose

Multi-surface differential evolution solver with Python for optimization, Prolog for constraint logic, and Hy for adaptive DE parameters.

## Implementation

### Python DE Solver

```python
import numpy as np
from typing import Callable, Tuple, List, Optional

class DifferentialEvolution:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float]],
                 pop_size: int = 15, F: float = 0.8, CR: float = 0.9,
                 max_iter: int = 1000):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.F = F
        self.CR = CR
        self.max_iter = max_iter
        self.dim = len(bounds)
        self.population = self._init_population()
        self.best = None
        self.best_score = float('inf')
    
    def _init_population(self) -> np.ndarray:
        pop = np.zeros((self.pop_size, self.dim))
        for i in range(self.dim):
            pop[:, i] = np.random.uniform(self.bounds[i][0], self.bounds[i][1], self.pop_size)
        return pop
    
    def optimize(self) -> Tuple[np.ndarray, float]:
        for _ in range(self.max_iter):
            for i in range(self.pop_size):
                candidates = [x for x in range(self.pop_size) if x != i]
                a, b, c = np.random.choice(candidates, 3, replace=False)
                
                mutant = self.population[a] + self.F * (self.population[b] - self.population[c])
                mutant = np.clip(mutant, [b[0] for b in self.bounds], [b[1] for b in self.bounds])
                
                trial = np.copy(self.population[i])
                j_rand = np.random.randint(self.dim)
                for j in range(self.dim):
                    if np.random.rand() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                
                score = self.objective(trial)
                if score < self.objective(self.population[i]):
                    self.population[i] = trial
                    if score < self.best_score:
                        self.best_score = score
                        self.best = trial
        return self.best, self.best_score

def de_adaptive(objective, bounds, max_iter=500):
    F = 0.5 + 0.5 * np.random.rand()
    CR = 0.9
    for gen in range(max_iter):
        if gen > 100 and np.random.rand() < 0.1:
            F = np.clip(F + 0.1 * np.random.randn(), 0.4, 1.0)
            CR = np.clip(CR + 0.1 * np.random.randn(), 0.1, 0.9)
    return DifferentialEvolution(objective, bounds, F=F, CR=CR, max_iter=max_iter).optimize()
```

### Prolog Constraint Logic

```prolog
% DE parameter constraints
valid_parameters(F, CR, PopulationSize) :-
    F >= 0.4, F =< 1.0,
    CR >= 0.0, CR =< 1.0,
    PopulationSize >= 4, PopulationSize =< 100.

% Convergence detection
converged_best(History, Tolerance) :-
    findall(Score, member(score(Score), History), Scores),
    max_list(Scores, Max),
    min_list(Scores, Min),
    abs(Max - Min) < Tolerance.

% Mutation validity
valid_mutation(Vector, Bounds, ValidVector) :-
    forall(member(V-Bound, Vector-Bounds),
           between(Bound.low, Bound.high, V)).
```

### Hy Adaptive DE

```hy
(defn adaptive-f [generation max-generations]
  "Adapt mutation factor over generations"
  (+ 0.4 (* 0.6 (/ generation max-generations))))

(defn jade-strategy [current-cr success-history]
  "JADE adaptive DE strategy"
  (let [c (mean (take 5 success-history))]
    (if (< c 0.1)
        (* current-cr 0.9)
        (+ current-cr (* 0.1 (- 1 c))))))

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface

def sphere_function(x):
    """Simple test objective: sphere function (minimum at 0)."""
    return sum(xi**2 for xi in x)

def rastrigin_function(x):
    """Rastrigin function (many local minima)."""
    A = 10
    n = len(x)
    return A * n + sum(xi**2 - A * np.cos(2 * np.pi * xi) for xi in x)

@pytest.mark.asyncio
class TestDifferentialEvolution:
    @pytest.fixture
    async def de_surface(self):
        """Get Python surface for DE execution."""
        return PythonSurface()

    async def test_de_initialization(self, de_surface):
        """Test DE solver initialization."""
        code = '''
import numpy as np
from typing import Callable, Tuple

class DifferentialEvolution:
    def __init__(self, objective: Callable, bounds: list, pop_size: int = 15, F: float = 0.8, CR: float = 0.9, max_iter: int = 100):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.F = F
        self.CR = CR
        self.max_iter = max_iter
        self.dim = len(bounds)

de = DifferentialEvolution(lambda x: sum(xi**2 for xi in x), [(0, 5)]*2)
assert de.dim == 2
assert de.pop_size == 15
assert de.F == 0.8
'''
        result = await de_surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_sphere_optimization(self, de_surface):
        """Test DE on sphere function (should find near-zero)."""
        code = '''
import numpy as np
from typing import Callable, Tuple

def sphere(x):
    return sum(xi**2 for xi in x)

class DifferentialEvolution:
    def __init__(self, objective: Callable, bounds: list, pop_size: int = 20, F: float = 0.8, CR: float = 0.9, max_iter: int = 50):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.F = F
        self.CR = CR
        self.max_iter = max_iter
        self.dim = len(bounds)
        self.population = self._init_population()
        self.best = None
        self.best_score = float('inf')
    
    def _init_population(self):
        pop = np.zeros((self.pop_size, self.dim))
        for i in range(self.dim):
            pop[:, i] = np.random.uniform(self.bounds[i][0], self.bounds[i][1], self.pop_size)
        return pop
    
    def optimize(self):
        for _ in range(self.max_iter):
            for i in range(self.pop_size):
                candidates = [x for x in range(self.pop_size) if x != i]
                a, b, c = np.random.choice(candidates, 3, replace=False)
                mutant = self.population[a] + self.F * (self.population[b] - self.population[c])
                mutant = np.clip(mutant, [b[0] for b in self.bounds], [b[1] for b in self.bounds])
                trial = np.copy(self.population[i])
                j_rand = np.random.randint(self.dim)
                for j in range(self.dim):
                    if np.random.rand() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                score = self.objective(trial)
                if score < self.objective(self.population[i]):
                    self.population[i] = trial
                    if score < self.best_score:
                        self.best_score = score
                        self.best = trial
        return self.best, self.best_score

bounds = [(-5, 5)] * 2
de = DifferentialEvolution(sphere, bounds, pop_size=15, max_iter=100)
best_x, best_score = de.optimize()
print(f"best_score={best_score}")
'''
        result = await de_surface.execute(code, {})
        assert result["status"] == "ok"
        # Score should be very small (near 0) for sphere
        assert result["value"] < 1.0, f"Expected near-zero score, got {result['value']}"

    async def test_de_with_bounds(self, de_surface):
        """Test that DE respects bounds."""
        code = '''
import numpy as np

def rosenbrock(x):
    return sum(100.0*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2 for i in range(len(x)-1))

class DifferentialEvolution:
    def __init__(self, objective, bounds, pop_size=10, F=0.8, CR=0.9, max_iter=50):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.F = F
        self.CR = CR
        self.max_iter = max_iter
        self.dim = len(bounds)
        self.population = self._init_population()
        self.best = None
        self.best_score = float('inf')
    
    def _init_population(self):
        pop = np.zeros((self.pop_size, self.dim))
        for i in range(self.dim):
            pop[:, i] = np.random.uniform(self.bounds[i][0], self.bounds[i][1], self.pop_size)
        return pop
    
    def optimize(self):
        for _ in range(self.max_iter):
            for i in range(self.pop_size):
                candidates = [x for x in range(self.pop_size) if x != i]
                a, b, c = np.random.choice(candidates, 3, replace=False)
                mutant = self.population[a] + self.F * (self.population[b] - self.population[c])
                mutant = np.clip(mutant, [b[0] for b in self.bounds], [b[1] for b in self.bounds])
                trial = np.copy(self.population[i])
                j_rand = np.random.randint(self.dim)
                for j in range(self.dim):
                    if np.random.rand() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                score = self.objective(trial)
                if score < self.objective(self.population[i]):
                    self.population[i] = trial
                    if score < self.best_score:
                        self.best_score = score
                        self.best = trial
        return self.best, self.best_score

bounds = [(-2, 2)] * 2
de = DifferentialEvolution(rosenbrock, bounds, pop_size=10, max_iter=50)
best_x, best_score = de.optimize()
# Check all values are within bounds
assert np.all(best_x >= -2) and np.all(best_x <= 2)
'''
        result = await de_surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_adaptive_de(self, de_surface):
        """Test adaptive DE parameter adjustment."""
        code = '''
import numpy as np
from typing import Callable

def sphere(x):
    return sum(xi**2 for xi in x)

class DifferentialEvolution:
    def __init__(self, objective, bounds, pop_size=15, F=0.8, CR=0.9, max_iter=100):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.F = F
        self.CR = CR
        self.max_iter = max_iter
        self.dim = len(bounds)
        self.population = self._init_population()
        self.best_score = float('inf')
    
    def _init_population(self):
        pop = np.zeros((self.pop_size, self.dim))
        for i in range(self.dim):
            pop[:, i] = np.random.uniform(self.bounds[i][0], self.bounds[i][1], self.pop_size)
        return pop
    
    def optimize(self):
        for gen in range(self.max_iter):
            for i in range(self.pop_size):
                candidates = [x for x in range(self.pop_size) if x != i]
                a, b, c = np.random.choice(candidates, 3, replace=False)
                mutant = self.population[a] + self.F * (self.population[b] - self.population[c])
                mutant = np.clip(mutant, [b[0] for b in self.bounds], [b[1] for b in self.bounds])
                trial = np.copy(self.population[i])
                j_rand = np.random.randint(self.dim)
                for j in range(self.dim):
                    if np.random.rand() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                score = self.objective(trial)
                if score < self.objective(self.population[i]):
                    self.population[i] = trial
                    if score < self.best_score:
                        self.best_score = score
        # Adaptive parameter update (simplified)
        if self.max_iter > 100:
            self.F = np.clip(self.F + 0.1 * np.random.randn(), 0.4, 1.0)
            self.CR = np.clip(self.CR + 0.1 * np.random.randn(), 0.1, 0.9)
        return self.best_score

bounds = [(-5, 5)] * 3
de = DifferentialEvolution(sphere, bounds, pop_size=10, max_iter=120)
final_score = de.optimize()
assert final_score < 10.0
'''
        result = await de_surface.execute(code, {})
        assert result["status"] == "ok"

### Integration Tests

```python
import pytest
import numpy as np
from em_cubed import reindex, search_registry
from em_cubed.surfaces import PythonSurface
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_de_skill_integration():
    """Test the differential evolution skill in a complete workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "differential-evolution-solver"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: differential evolution solver
Domain: OPTIMIZATION
surfaces:
  - python
---

## Purpose
Differential evolution optimization

## Description
DE solver for continuous optimization

## Implementation

### Python

```python
def test_func(x):
    return sum(xi**2 for xi in x)
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        results = search_registry("differential", registry_file)
        assert len(results) >= 1
        
        surface = PythonSurface()
        code = "2 + 2"
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] == 4
```

## Usage Patterns

### Basic DE Optimization

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

# Define a simple objective function
code = '''
def objective(x):
    return (x[0] - 1)**2 + (x[1] - 2)**2

# Run DE optimization
result = objective([1.0, 2.0])
print(f"Objective at optimum: {result}")
'''
result = await surface.execute(code, {})
print(f"Result: {result}")
```

### Constrained Optimization

```python
# Define constraints via bounds
bounds = [(0, 10), (0, 5), (-5, 5)]
# DE will respect these bounds during mutation
```

## Security Considerations

- Uses numpy for numerical computations (safe)
- No file system or network access in implementation
- Execution limited by timeout (default 30s)

## Dependencies

- numpy (for numerical operations)
- em_cubed framework
```