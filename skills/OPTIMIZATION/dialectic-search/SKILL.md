---
name: dialectic-search
domain: OPTIMIZATION
version: 1.0.0
surfaces:
- python
- prolog
- hy
description: Dialectic search optimizer using thesis-antithesis-synthesis framework for multi-objective optimization.
compatibility: PYTHON
complexity: Medium
type: Optimization
category: Philosophy-Based Search
estimated execution time: 5-20 minutes
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
  - dialectic_search
  - philosophical_optimization
  - thesis_antithesis_synthesis
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T17:00:00Z"
updated_at: "2026-05-29T17:00:00Z"

## Purpose

Multi-surface Dialectic Search (DA) optimizer. An optimization algorithm rooted in Hegelian dialectics that guides search trajectories by constructing a Thesis (current best solution), proposing an Antithesis (exploring opposite coordinates), and reconciling them into Synthesis.

## Implementation

### Python DA Optimizer

```python
import numpy as np
import random
from typing import Callable, Tuple, List, Optional

class DialecticOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float]],
                 pop_size: int = 50, k1: int = 3, k2: int = 10, max_iter: int = 100):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.dim = len(bounds)
        self.k1 = k1
        self.k2 = k2
        self.max_iter = max_iter

        self.population = np.zeros((pop_size, self.dim))
        self.fitness = np.full(pop_size, float('inf'))
        self.best_fitness = float('inf')
        self.best_position = None
        self.history = []

    def _clip(self, val: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, val))

    def _euclidean_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        return np.sqrt(np.sum((a - b) ** 2))

    def _initialize_population(self):
        for i in range(self.pop_size):
            for c in range(self.dim):
                self.population[i, c] = random.uniform(self.bounds[c][0], self.bounds[c][1])

    def _sort_population(self):
        indices = np.argsort(self.fitness)[::-1]
        self.population = self.population[indices]
        self.fitness = self.fitness[indices]

    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        self._initialize_population()

        for i in range(self.pop_size):
            self.fitness[i] = self.objective(self.population[i])
            if self.fitness[i] < self.best_fitness:
                self.best_fitness = self.fitness[i]
                self.best_position = self.population[i].copy()

        self.history.append(float(self.best_fitness))

        for gen in range(self.max_iter):
            self._sort_population()

            for c in range(self.dim):
                self.population[0, c] = self.population[0, c] + random.random() * (self.population[1, c] - self.population[0, c])
                self.population[0, c] = self._clip(self.population[0, c], self.bounds[c][0], self.bounds[c][1])

            for i in range(self.k2, self.k1):
                dist_prev = -float('inf')
                dist_next = -float('inf')
                anti_prev = -1
                anti_next = -1

                for j in range(1, self.k2 + 1):
                    dist = self._euclidean_distance(self.population[i], self.population[i - j])
                    if dist > dist_prev:
                        dist_prev = dist
                        anti_prev = i - j

                for j in range(1, self.k2 + 1):
                    dist = self._euclidean_distance(self.population[i], self.population[i + j])
                    if dist > dist_next:
                        dist_next = dist
                        anti_next = i + j

                anti_idx = anti_prev if dist_prev > dist_next else anti_next

                for c in range(self.dim):
                    self.population[i, c] = self.population[i, c] + random.random() * (self.population[anti_idx, c] - self.population[i, c])
                    self.population[i, c] = self._clip(self.population[i, c], self.bounds[c][0], self.bounds[c][1])

            for i in range(self.k1, self.pop_size):
                anti1 = random.randint(0, self.k1 - 1)
                anti2 = random.randint(0, self.k1 - 1)
                while anti1 == anti2:
                    anti2 = random.randint(0, self.k1 - 1)

                dist1 = self._euclidean_distance(self.population[i], self.population[anti1])
                dist2 = self._euclidean_distance(self.population[i], self.population[anti2])
                anti_idx = anti1 if dist1 < dist2 else anti2

                for c in range(self.dim):
                    self.population[i, c] = self.population[i, c] + random.random() * (self.population[anti_idx, c] - self.population[i, c])
                    self.population[i, c] = self._clip(self.population[i, c], self.bounds[c][0], self.bounds[c][1])

            for i in range(self.pop_size):
                score = self.objective(self.population[i])
                if score < self.fitness[i]:
                    self.fitness[i] = score
                if score < self.best_fitness:
                    self.best_fitness = score
                    self.best_position = self.population[i].copy()

            self.history.append(float(self.best_fitness))

        return self.best_position, self.best_fitness, self.history
```

### Prolog Dialectic Logic

```prolog
% Parameter validation for DA
valid_da_params(PopSize, K1, K2) :-
    PopSize >= 4, PopSize =< 200,
    K1 >= 1, K1 =< 10,
    K2 >= 5, K2 =< 50.

% Thesis-Antithesis-Synthesis logic
% For speculative thinkers: max distance from quality peer
select_speculative_antithesis(CurrentDist, NextDist, CurrentIdx, NextIdx, SelectedIdx) :-
    CurrentDist > NextDist -> SelectedIdx = CurrentIdx ; SelectedIdx = NextIdx.

% For practical thinkers: min distance from quality peer
select_practical_antithesis(Dist1, Dist2, Idx1, Idx2, SelectedIdx) :-
    Dist1 < Dist2 -> SelectedIdx = Idx1 ; SelectedIdx = Idx2.

% Convergence check
converged(History, Tolerance) :-
    length(History, Len),
    Len >= 10,
    append(_, Last10, History),
    length(Last10, 10),
    max_list(Last10, Max),
    min_list(Last10, Min),
    abs(Max - Min) < Tolerance.
```

### Hy Synthesis Helper

```hy
; Dialectic Search - Hy surface
; Synthesis parameter computation

(defn generate-mu [size]
  "Generate random mutation vector for synthesis step."
  (list-comp (random.random) [i (range size)]))

(defn apply-synthesis [current antithesis mu bounds]
  "Apply synthesis: x_new = x + mu * (x_anti - x)"
  (+ current (* mu (- antithesis current))))

(defn clip-value [val lo hi]
  "Clip value to bounds."
  (max lo (min hi val)))

(defn adapt-alpha [current-alpha success-rate]
  "Adapt search scope based on success rate."
  (cond
    [(< success-rate 0.1) (* current-alpha 1.2)]
    [(> success-rate 0.7) (* current-alpha 0.9)]
    [True current-alpha]))
```

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface, PrologSurface

def sphere(x):
    return sum(xi**2 for xi in x)

@pytest.mark.asyncio
class TestDialecticOptimizer:
    async def test_python_da_sphere(self):
        """Test DA finds near-zero on sphere function."""
        code = '''
import numpy as np
import random

def sphere(x):
    return sum(xi**2 for xi in x)

class DialecticOptimizer:
    def __init__(self, objective, bounds, pop_size=30, k1=3, k2=10, max_iter=50):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.dim = len(bounds)
        self.k1 = k1
        self.k2 = k2
        self.max_iter = max_iter
        self.population = np.zeros((pop_size, self.dim))
        self.fitness = np.full(pop_size, float("inf"))
        self.best_fitness = float("inf")
        self.best_position = None

    def _clip(self, val, lo, hi):
        return max(lo, min(hi, val))

    def _euclidean_distance(self, a, b):
        return np.sqrt(np.sum((a - b) ** 2))

    def optimize(self):
        for i in range(self.pop_size):
            for c in range(self.dim):
                self.population[i, c] = random.uniform(self.bounds[c][0], self.bounds[c][1])
            self.fitness[i] = self.objective(self.population[i])
            if self.fitness[i] < self.best_fitness:
                self.best_fitness = self.fitness[i]
                self.best_position = self.population[i].copy()

        for gen in range(self.max_iter):
            indices = np.argsort(self.fitness)[::-1]
            self.population = self.population[indices]
            self.fitness = self.fitness[indices]

            for i in range(self.k1, self.pop_size):
                anti1 = random.randint(0, self.k1 - 1)
                anti2 = random.randint(0, self.k1 - 1)
                while anti1 == anti2:
                    anti2 = random.randint(0, self.k1 - 1)
                dist1 = self._euclidean_distance(self.population[i], self.population[anti1])
                dist2 = self._euclidean_distance(self.population[i], self.population[anti2])
                anti_idx = anti1 if dist1 < dist2 else anti2
                for c in range(self.dim):
                    self.population[i, c] = self._clip(
                        self.population[i, c] + random.random() * (self.population[anti_idx, c] - self.population[i, c]),
                        self.bounds[c][0], self.bounds[c][1]
                    )
                self.fitness[i] = self.objective(self.population[i])
                if self.fitness[i] < self.best_fitness:
                    self.best_fitness = self.fitness[i]
                    self.best_position = self.population[i].copy()

        return self.best_position, self.best_fitness

opt = DialecticOptimizer(sphere, [(-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0)], pop_size=30, max_iter=60)
best_x, best_score = opt.optimize()
best_score
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 1.0

    async def test_prolog_params(self):
        """Test Prolog parameter validation."""
        code = '''
valid_da_params(PopSize, K1, K2) :-
    PopSize >= 4, PopSize =< 200,
    K1 >= 1, K1 =< 10,
    K2 >= 5, K2 =< 50.

?- valid_da_params(50, 3, 10).
'''
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_da_skill_integration():
    """Test dialectic-search skill in registry pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "dialectic-search"
        skills_dir.mkdir(parents=True)
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('name: dialectic-search\nDomain: OPTIMIZATION\nsurfaces:\n  - python\n  - prolog')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("dialectic", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic DA Optimization (Sphere Function)

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()
code = '''
import numpy as np, random

def objective(x):
    return sum(xi**2 for xi in x)

bounds = [(-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0)]
opt = DialecticOptimizer(objective, bounds, pop_size=30, k1=3, k2=10, max_iter=80)
best_x, best_score, history = opt.optimize()
print("Best X:", best_x)
print("Best Score:", best_score)
'''
result = await surface.execute(code, {})
```

## Security Considerations

- Pure numerical operations only; no file system, network, or OS access.
- Euclidean distance computation is bounded and safe.
- Agent positions clamped to declared bounds.

## Dependencies

- `numpy`
- `em_cubed` framework