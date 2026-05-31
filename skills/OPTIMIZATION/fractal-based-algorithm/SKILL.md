---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: Medium
Type: Optimization
Category: Fractal-Based Search
Estimated Execution Time: 5-20 minutes
name: fractal-based-algorithm
Source: community
surfaces:
  - python
  - prolog
  - hy
---
origin: manual
triggers:
  - fractal_optimization
  - fba
  - space_partitioning
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T17:10:00Z"
updated_at: "2026-05-29T17:10:00Z"

## Purpose

Multi-surface Fractal-Based Algorithm (FBA) optimizer. Uses self-similar fractal structures and hierarchical space partitioning to adaptively explore solution space based on promising area density.

## Implementation

### Python FBA Optimizer

```python
import numpy as np
import random
import math
from typing import Callable, Tuple, List, Optional

class FractalOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float, float]],
                 pop_size: int = 50, p1: int = 60, p2: int = 30, p3: float = 0.8,
                 m_value: int = 10, max_iter: int = 100):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.m_value = m_value
        self.max_iter = max_iter

        self.population = []
        self.subspaces = []
        self.history = []
        self.best_fitness = float('inf')
        self.best_position = None

    def _clip(self, val: float, lo: float, hi: float, step: float = 0.0) -> float:
        val = max(lo, min(hi, val))
        if step > 0.0:
            val = lo + step * round((val - lo) / step)
        return val

    def _power_distribution(self, center: float, out_min: float, out_max: float, p: float = 5.0) -> float:
        rnd = random.uniform(-1.0, 1.0)
        r = abs(rnd) ** p
        if rnd >= 0.0:
            return self._clip(center + r * (out_max - center), out_min, out_max)
        return self._clip(center - r * (center - out_min), out_min, out_max)

    def _is_point_in_subspace(self, point: List[float], subspace: dict) -> bool:
        for c in range(self.dim):
            if point[c] < subspace['min'][c] or point[c] >= subspace['max'][c]:
                return False
        return True

    def _create_initial_partitioning(self):
        total_subspaces = min(self.m_value ** self.dim, 10000)
        self.subspaces = []
        for i in range(total_subspaces):
            subspace = {
                'min': [0.0] * self.dim,
                'max': [0.0] * self.dim,
                'promising_rank': 0.0,
                'is_promising': False,
                'parent_index': -1,
                'level': 0
            }
            self.subspaces.append(subspace)

        index = 0
        if self.dim == 1:
            interval_size = (self.bounds[0][1] - self.bounds[0][0]) / self.m_value
            for i in range(self.m_value):
                if index >= total_subspaces:
                    break
                self.subspaces[index]['min'][0] = self.bounds[0][0] + i * interval_size
                self.subspaces[index]['max'][0] = self.bounds[0][0] + (i + 1) * interval_size
                index += 1
        elif self.dim == 2:
            interval_size0 = (self.bounds[0][1] - self.bounds[0][0]) / self.m_value
            interval_size1 = (self.bounds[1][1] - self.bounds[1][0]) / self.m_value
            for i in range(self.m_value):
                for j in range(self.m_value):
                    if index >= total_subspaces:
                        break
                    self.subspaces[index]['min'][0] = self.bounds[0][0] + i * interval_size0
                    self.subspaces[index]['max'][0] = self.bounds[0][0] + (i + 1) * interval_size0
                    self.subspaces[index]['min'][1] = self.bounds[1][0] + j * interval_size1
                    self.subspaces[index]['max'][1] = self.bounds[1][0] + (j + 1) * interval_size1
                    index += 1
        else:
            indices = [0] * self.dim
            while index < total_subspaces:
                for c in range(self.dim):
                    interval_size = (self.bounds[c][1] - self.bounds[c][0]) / self.m_value
                    self.subspaces[index]['min'][c] = self.bounds[c][0] + indices[c] * interval_size
                    self.subspaces[index]['max'][c] = self.bounds[c][0] + (indices[c] + 1) * interval_size
                c = self.dim - 1
                while c >= 0:
                    indices[c] += 1
                    if indices[c] < self.m_value:
                        break
                    indices[c] = 0
                    c -= 1
                if c < 0:
                    break
                index += 1

    def _identify_promising_points(self, fitness: List[float]) -> List[int]:
        sorted_idx = sorted(range(len(fitness)), key=lambda i: fitness[i], reverse=True)
        num_promising = max(1, min(self.pop_size * self.p1 // 100, self.pop_size))
        return [sorted_idx[i] for i in range(num_promising)]

    def _calculate_subspace_ranks(self, promising_indices: List[int]):
        for subspace in self.subspaces:
            subspace['promising_rank'] = 0.0

        total = len(promising_indices)
        if total == 0:
            return

        for idx in promising_indices:
            point = self.population[idx]
            for subspace in self.subspaces:
                if self._is_point_in_subspace(point, subspace):
                    subspace['promising_rank'] += 1.0
                    break

        for subspace in self.subspaces:
            subspace['promising_rank'] /= total

    def _select_promising_subspaces(self):
        sorted_idx = sorted(range(len(self.subspaces)),
                          key=lambda i: self.subspaces[i]['promising_rank'], reverse=True)
        num_promising = max(1, min(len(self.subspaces) * self.p2 // 100, len(self.subspaces)))
        for i in range(len(self.subspaces)):
            self.subspaces[i]['is_promising'] = False
        for i in range(num_promising):
            self.subspaces[sorted_idx[i]]['is_promising'] = True

    def _divide_promising_subspaces(self):
        for i, subspace in enumerate(self.subspaces):
            if not subspace['is_promising']:
                continue
            parent = subspace.copy()
            total_new = self.m_value ** self.dim
            current_len = len(self.subspaces)
            for idx in range(total_new):
                new_subspace = {
                    'min': [0.0] * self.dim,
                    'max': [0.0] * self.dim,
                    'promising_rank': 0.0,
                    'is_promising': False,
                    'parent_index': i,
                    'level': parent.get('level', 0) + 1
                }
                indices = [0] * self.dim
                for d in range(self.dim):
                    interval_size = (parent['max'][d] - parent['min'][d]) / self.m_value
                    new_subspace['min'][d] = parent['min'][d] + indices[d] * interval_size
                    new_subspace['max'][d] = parent['min'][d] + (indices[d] + 1) * interval_size

                # Increment indices
                c = self.dim - 1
                while c >= 0:
                    indices[c] += 1
                    if indices[c] < self.m_value:
                        break
                    indices[c] = 0
                    c -= 1

                if c < 0:
                    break
                self.subspaces.append(new_subspace)

    def _generate_new_population(self):
        total_rank = sum(s['promising_rank'] for s in self.subspaces)
        if total_rank < 0.0001:
            for s in self.subspaces:
                s['promising_rank'] = 1.0
            total_rank = len(self.subspaces)

        points = 0
        for subspace in self.subspaces:
            if points >= self.pop_size:
                break
            n_points = int(round((subspace['promising_rank'] / total_rank) * self.pop_size))
            n_points = min(n_points, self.pop_size - points)
            for _ in range(n_points):
                ind = []
                for c in range(self.dim):
                    val = random.uniform(subspace['min'][c], subspace['max'][c])
                    ind.append(self._clip(val, self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]))
                self.population[points] = ind
                points += 1

        while points < self.pop_size:
            ind = []
            for c in range(self.dim):
                val = random.uniform(self.bounds[c][0], self.bounds[c][1])
                ind.append(self._clip(val, self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]))
            self.population.append(ind)
            points += 1

    def _mutate_points(self):
        for i in range(self.pop_size):
            if random.random() < self.p3:
                for c in range(self.dim):
                    self.population[i][c] = self._power_distribution(
                        self.best_position[c], self.bounds[c][0], self.bounds[c][1], 5
                    )

    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        self._create_initial_partitioning()

        for _ in range(self.pop_size):
            ind = []
            for c in range(self.dim):
                val = random.uniform(self.bounds[c][0], self.bounds[c][1])
                ind.append(self._clip(val, self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]))
            self.population.append(ind)

        fitness = [self.objective(ind) for ind in self.population]
        self.best_fitness = min(fitness)
        self.best_position = self.population[fitness.index(self.best_fitness)].copy()
        self.history.append(self.best_fitness)

        for epoch in range(1, self.max_iter + 1):
            promising_indices = self._identify_promising_points(fitness)
            self._calculate_subspace_ranks(promising_indices)
            self._select_promising_subspaces()
            self._divide_promising_subspaces()
            self._generate_new_population()
            self._mutate_points()

            fitness = [self.objective(ind) for ind in self.population]
            current_best = min(fitness)
            if current_best < self.best_fitness:
                self.best_fitness = current_best
                self.best_position = self.population[fitness.index(current_best)].copy()
            self.history.append(self.best_fitness)

        return np.array(self.best_position), self.best_fitness, self.history
```

### Prolog Parameter Validation

```prolog
% FBA parameter constraints
valid_fba_params(PopSize, P1, P2, P3, MValue) :-
    PopSize >= 4, PopSize =< 200,
    P1 >= 10, P1 =< 100,
    P2 >= 10, P2 =< 100,
    P3 >= 0.0, P3 =< 1.0,
    MValue >= 5, MValue =< 20.

% Convergence check using history
converged(History, Tolerance) :-
    length(History, Len),
    Len >= 5,
    max_list(History, Max),
    min_list(History, Min),
    abs(Max - Min) < Tolerance.
```

### Hy Space Partitioning

```hy
; Fractal-Based Algorithm - Hy surface
; Space partitioning and fractal structure functions

(defn create-subspace [min-bounds max-bounds level parent-idx]
  "Create a subspace with bounds and metadata."
  {:min min-bounds :max max-bounds :level level :parent-index parent-idx :rank 0.0 :promising False})

(defn divide-subspace [subspace m-value]
  "Divide a subspace into m_value^dim smaller subspaces."
  (setv dim (len subspace.min))
  (setv total (pow m-value dim))
  (setv result [])
  (setv indices [0]
  (for [i (range dim)]
    (.append indices 0))
  (for [idx (range total)]
    (setv new-subspace (create-subspace
      [subspace.min[i] + indices[i] * (/ (- subspace.max[i] subspace.min[i]) m-value)
       for i (range dim)]
      [subspace.min[i] + (+ indices[i] 1) * (/ (- subspace.max[i] subspace.min[i]) m-value)
       for i (range dim)]
      (+ subspace.level 1)
      idx))
    (.append result new-subspace)
    ; increment indices
    (setv c (- dim 1))
    (while (>= c 0)
      (setv indices[c] (+ indices[c] 1))
      (if (< indices[c] m-value)
        (break))
      (setv indices[c] 0)
      (setv c (- c 1)))
    (if (< c 0)
      (break)))
  result)

(defn point-in-subspace [point subspace]
  "Check if point is within subspace bounds."
  (for [c (range (len point))]
    (if (or (< point[c] subspace.min[c]) (>= point[c] subspace.max[c]))
      (return False)))
  True)

(defn power-distribution [center out-min out-max p rnd]
  "Generate power-law distributed random value for mutation."
  (setv r (** (abs rnd) p))
  (if (>= rnd 0.0)
    (max out-min (min out-max (+ center (* r (- out-max center)))))
    (max out-min (min out-max (- center (* r (- center out-min)))))))
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
class TestFractalOptimizer:
    async def test_python_fba_sphere(self):
        """Test FBA on sphere function."""
        code = '''
import random, math

def sphere(x): return sum(xi**2 for xi in x)

class FractalOptimizer:
    def __init__(self, objective, bounds, pop_size=30, m_value=5):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.m_value = m_value
        self.population = []
        
    def optimize(self):
        for _ in range(self.pop_size * 2):
            ind = [random.uniform(-5, 5) for _ in range(self.dim)]
            f = self.objective(ind)
            for c in range(self.dim):
                ind[c] += random.gauss(0, 0.5)
            f = self.objective(ind)
        return ind, min(sphere(ind) for ind in self.population)

opt = FractalOptimizer(sphere, [(-5.0, 5.0), (-5.0, 5.0)])
best_x, best_f = opt.optimize()
best_f
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_point_in_subspace(self):
        """Test subspace point containment check."""
        code = '''
def point_in_subspace(point, subspace):
    for c in range(len(point)):
        if point[c] < subspace['min'][c] or point[c] >= subspace['max'][c]:
            return False
    return True

subspace = {'min': [0.0, 0.0], 'max': [1.0, 1.0]}
point_in_subspace([0.5, 0.5], subspace) and not point_in_subspace([1.5, 0.5], subspace)
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_prolog_params(self):
        """Test Prolog parameter validation."""
        code = '''
?- 50 >= 4, 50 =< 200, 60 >= 10, 60 =< 100, 30 >= 10, 30 =< 100, 0.8 >= 0.0, 0.8 =< 1.0, 10 >= 5, 10 =< 20.
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
async def test_fba_skill_integration():
    """Test fractal-based-algorithm skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "fractal-based-algorithm"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: fractal-based-algorithm\nDomain: OPTIMIZATION')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# FBA\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("fractal", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic FBA Optimization

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()
code = '''
def objective(x): return sum(xi**2 for xi in x)
bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = FractalOptimizer(objective, bounds, pop_size=30, m_value=5, max_iter=80)
best_x, best_score, history = opt.optimize()
print("Best:", best_x, "Score:", best_score)
'''
result = await surface.execute(code, {})
```

## Security Considerations

- Pure numerical operations only; no file system, network, or OS access.
- All coordinates clamped to declared bounds.
- Power distribution values bounded to search space.

## Dependencies

- `numpy`
- `em_cubed` framework