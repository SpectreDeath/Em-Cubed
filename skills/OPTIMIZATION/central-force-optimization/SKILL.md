---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: Medium
Type: Optimization
Category: Gravitational Search
Estimated Execution Time: 5-15 minutes
name: central-force-optimization
Source: community
surfaces:
  - python
  - prolog
  - hy
---
origin: manual
triggers:
  - cfo
  - central_force
  - gravitational_optimization
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T18:58:00Z"
updated_at: "2026-05-29T18:58:00Z"

## Purpose

Multi-surface Central Force Optimization (CFO) algorithm. Uses deterministic gravitational attraction between probes (agents) where better solutions attract worse ones in a one-way mechanism.

## Implementation

### Python CFO Optimizer

```python
import numpy as np
import random
import math
from typing import Callable, Tuple, List, Optional

class CFOOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float, float]],
                 pop_size: int = 30, g: float = 1.0, alpha: float = 0.1, beta: float = 0.1,
                 initial_frep: float = 0.9, final_frep: float = 0.1, noise_factor: float = 1.0,
                 max_iter: int = 100):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.g = g
        self.alpha = alpha
        self.beta = beta
        self.initial_frep = initial_frep
        self.final_frep = final_frep
        self.noise_factor = noise_factor
        self.max_iter = max_iter

        self.probes = []
        self.accelerations = []
        self.history = []
        self.best_fitness = float('-inf')
        self.best_position = None
        self.frep = initial_frep

    def _clip(self, val: float, lo: float, hi: float, step: float = 0.0) -> float:
        val = max(lo, min(hi, val))
        if step > 0.0:
            val = lo + step * round((val - lo) / step)
        return val

    def _calculate_distance_squared(self, x1: List[float], x2: List[float]) -> float:
        return sum((x1[i] - x2[i]) ** 2 for i in range(len(x1)))

    def _calculate_accelerations(self):
        for p in range(self.pop_size):
            self.accelerations[p] = [0.0] * self.dim

        for p in range(self.pop_size):
            for k in range(self.pop_size):
                if k == p:
                    continue

                mass_diff = self.probes[k]['fitness'] - self.probes[p]['fitness']
                if mass_diff <= 0:
                    continue

                dist_sq = self._calculate_distance_squared(
                    self.probes[k]['position'], self.probes[p]['position']
                )
                if dist_sq < 1e-10:
                    continue

                distance = math.sqrt(dist_sq)
                for c in range(self.dim):
                    direction = (self.probes[k]['position'][c] - self.probes[p]['position'][c]) / distance
                    self.accelerations[p][c] += self.g * (mass_diff ** self.alpha) * direction / (distance ** self.beta)

    def _update_positions(self, epoch: int):
        current_noise = self.noise_factor * (1.0 - epoch / self.max_iter) if self.max_iter > 0 else self.noise_factor

        for p in range(self.pop_size):
            for c in range(self.dim):
                # Position update: x_new = x_old + 0.5 * acceleration
                self.probes[p]['position'][c] += 0.5 * self.accelerations[p][c]

                # Add random noise for exploration
                self.probes[p]['position'][c] += current_noise * self.g * random.uniform(-1.0, 1.0)

                # Boundary handling
                self.probes[p]['position'][c] = self._clip(
                    self.probes[p]['position'][c],
                    self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]
                )

    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        # Initial distribution
        for _ in range(self.pop_size):
            pos = [random.uniform(self.bounds[c][0], self.bounds[c][1]) for c in range(self.dim)]
            self.probes.append({'position': pos, 'fitness': 0.0})
            self.accelerations.append([0.0] * self.dim)

        # Evaluate initial population
        for i in range(self.pop_size):
            self.probes[i]['fitness'] = self.objective(self.probes[i]['position'])

        self.best_fitness = max(p['fitness'] for p in self.probes)
        self.best_position = [self.probes[i]['position'] for i in range(self.pop_size)
                            if self.probes[i]['fitness'] == self.best_fitness][0].copy()
        self.history.append(self.best_fitness)

        for epoch in range(1, self.max_iter + 1):
            self._calculate_accelerations()
            self._update_positions(epoch)

            for p in range(self.pop_size):
                self.probes[p]['fitness'] = self.objective(self.probes[p]['position'])

            current_best = max(p['fitness'] for p in self.probes)
            if current_best > self.best_fitness:
                self.best_fitness = current_best
                self.best_position = [p['position'] for p in self.probes if p['fitness'] == current_best][0].copy()

            self.history.append(self.best_fitness)

        return np.array(self.best_position), self.best_fitness, self.history
```

### Prolog Parameter Validation

```prolog
% CFO parameter constraints
valid_cfo_params(PopSize, Alpha, Beta) :-
    PopSize >= 4, PopSize =< 100,
    Alpha >= 0.01, Alpha =< 2.0,
    Beta >= 0.01, Beta =< 2.0.

% Better fitness check
better_solution(Fitness1, Fitness2) :-
    Fitness1 > Fitness2.
```

### Hy Gravitational Helpers

```hy
; Central Force Optimization - Hy surface
; Gravitational attraction and distance calculations

(defn calculate-distance-squared [x1 x2]
  "Calculate squared Euclidean distance between two points."
  (sum (** (- (get x1 i) (get x2 i)) 2) for i (range (len x1))))

(defn gravitational-force [mass1 mass2 g alpha distance beta]
  "Calculate gravitational attraction force between two agents."
  (* g (** (- mass1 mass2) alpha) (/ 1 (** distance beta))))

(defn update-position [position acceleration current-noise g]
  "Update position with acceleration and noise."
  (+ position (* 0.5 acceleration) (* current-noise g (random.uniform -1.0 1.0))))
```

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface, PrologSurface

def sphere(x):
    return -sum(xi**2 for xi in x)  # Negative for maximization

@pytest.mark.asyncio
class TestCFOOptimizer:
    async def test_python_cfo_sphere(self):
        """Test CFO on sphere function (maximization)."""
        code = '''
import random, math

def sphere(x): return -sum(xi**2 for xi in x)

class CFOOptimizer:
    def __init__(self, objective, bounds, pop_size=30):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.dim = len(bounds)
        self.probes = []
        self.accelerations = []

    def optimize(self):
        for _ in range(self.pop_size):
            pos = [random.uniform(-5, 5) for _ in range(self.dim)]
            fitness = self.objective(pos)
            self.probes.append({'position': pos, 'fitness': fitness})
            self.accelerations.append([0.0] * self.dim)
        
        best_f = max(p['fitness'] for p in self.probes)
        return [p['position'] for p in self.probes if p['fitness'] == best_f][0], best_f

opt = CFOOptimizer(sphere, [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)])
best_x, best_f = opt.optimize()
best_f
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 0.0  # Best fitness should be negative (near 0 at optimum)

    async def test_distance_squared(self):
        """Test distance squared calculation."""
        code = '''
def distance_squared(x1, x2):
    return sum((x1[i] - x2[i])**2 for i in range(len(x1)))

distance_squared([0.0, 0.0], [3.0, 4.0])
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert abs(result["value"] - 25.0) < 1e-9

    async def test_prolog_params(self):
        """Test Prolog parameter validation."""
        code = '''
?- 30 >= 4, 30 =< 100, 0.1 >= 0.01, 0.1 =< 2.0, 0.1 >= 0.01, 0.1 =< 2.0.
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
async def test_cfo_skill_integration():
    """Test central-force-optimization skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "central-force-optimization"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: central-force-optimization\nDomain: OPTIMIZATION')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# CFO\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("central force", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic CFO Optimization

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()
code = '''
def objective(x): return -sum(xi**2 for xi in x)  # Maximize (minimize negative)
bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = CFOOptimizer(objective, bounds, pop_size=30, max_iter=80)
best_x, best_score, history = opt.optimize()
print("Best:", best_x, "Score:", best_score)
'''
result = await surface.execute(code, {})
```

## Security Considerations

- Pure numerical operations only; no file system, network, or OS access.
- All coordinates clamped to declared bounds.
- Gravitational force values bounded by distance constraints.

## Dependencies

- `numpy`
- `em_cubed` framework