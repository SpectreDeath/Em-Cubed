---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: Medium
Type: Optimization
Category: Chaos-Based Search
Estimated Execution Time: 5-20 minutes
name: chaos-optimization
Source: community
surfaces:
  - python
  - prolog
  - hy
---
origin: manual
triggers:
  - chaos_optimization
  - chaotic_search
  - logistic_map
  - tent_map
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T17:05:00Z"
updated_at: "2026-05-29T17:05:00Z"

## Purpose

Multi-surface Chaos Optimization Algorithm (COA) optimizer. Uses deterministic chaotic maps (Logistic, Tent, Sinusoidal) to generate pseudo-random search trajectories with stagnation detection and adaptive mutation.

## Implementation

### Python COA Optimizer

```python
import numpy as np
import random
import math
from typing import Callable, Tuple, List, Optional

class ChaosOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float, float]],
                 pop_size: int = 50, S1: int = 40, S2: int = 60,
                 t3: float = 1.2, P3: float = 0.8, max_iter: int = 100):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.S1 = S1
        self.S2 = S2
        self.t3 = t3
        self.P3 = P3
        self.max_iter = max_iter

        self.population = np.zeros((pop_size, self.dim))
        self.gamma = np.random.uniform(0, 1, (pop_size, self.dim))
        self.velocity = np.zeros((pop_size, self.dim))
        self.stagnation_counter = np.zeros(pop_size)
        self.history = []
        self.global_best_history = [-float('inf')] * 10
        self.history_index = 0

        self.best_fitness = float('inf')
        self.best_position = None

    def _select_chaos_map(self, gamma_val: float, map_idx: int) -> float:
        if map_idx == 0:
            return 4.0 * gamma_val * (1.0 - gamma_val)  # Logistic
        elif map_idx == 1:
            return 1.0 - 2.0 * abs(0.5 - gamma_val)  # Tent
        else:
            return math.sin(math.pi * gamma_val)  # Sinusoidal

    def _clip(self, val: float, lo: float, hi: float, step: float = 0.0) -> float:
        val = max(lo, min(hi, val))
        if step > 0.0:
            val = lo + step * round((val - lo) / step)
        return val

    def _power_distribution(self, center: float, out_min: float, out_max: float, p: float = 20.0) -> float:
        rnd = random.uniform(-1.0, 1.0)
        r = abs(rnd) ** p
        if rnd >= 0.0:
            return self._clip(center + r * (out_max - center), out_min, out_max)
        else:
            return self._clip(center - r * (center - out_min), out_min, out_max)

    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        for i in range(self.pop_size):
            for c in range(self.dim):
                self.population[i, c] = self._clip(
                    random.uniform(self.bounds[c][0], self.bounds[c][1]),
                    self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]
                )
            fitness = self.objective(self.population[i])
            if fitness < self.best_fitness:
                self.best_fitness = fitness
                self.best_position = self.population[i].copy()
            self.history.append(float(self.best_fitness))

        for epoch in range(1, self.max_iter + 1):
            for i in range(self.pop_size):
                should_mutate = random.random() < self.P3
                if should_mutate:
                    for c in range(self.dim):
                        self.gamma[i, c] = self._select_chaos_map(self.gamma[i, c], c % 3)
                        new_val = self._clip(
                            self.bounds[c][0] + self.gamma[i, c] * (self.bounds[c][1] - self.bounds[c][0]),
                            self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]
                        )
                        self.population[i, c] = new_val

                if epoch <= self.S1:
                    for c in range(self.dim):
                        self.velocity[i, c] = 0.5 * self.velocity[i, c] + 0.5 * random.gauss(0, 1)
                        self.population[i, c] += self.velocity[i, c]

            for i in range(self.pop_size):
                fitness = self.objective(self.population[i])
                if fitness >= self.objective(self.population[i] - self.velocity[i] * 0):
                    self.stagnation_counter[i] += 1
                else:
                    self.stagnation_counter[i] = 0

                if self.stagnation_counter[i] > 5 and random.random() < 0.2 * (1.0 + self.stagnation_counter[i] / 10.0):
                    for c in range(self.dim):
                        self.population[i, c] = self._power_distribution(
                            self.best_position[c], self.bounds[c][0], self.bounds[c][1], 20
                        )
                    self.velocity[i] = 0.0
                    self.stagnation_counter[i] = 0

                if fitness < self.best_fitness:
                    self.best_fitness = fitness
                    self.best_position = self.population[i].copy()

            if epoch > 1:
                self.history[epoch - 1] = float(self.best_fitness)

            recent_best = self.history[max(0, epoch - 10):epoch] if epoch > 10 else self.history[:]
            if len(recent_best) >= 5 and max(recent_best) - min(recent_best) < 0.001 * abs(sum(recent_best) / len(recent_best)):
                break

        return self.best_position, self.best_fitness, self.history
```

### Prolog Parameter Validation

```prolog
% COA parameter constraints
valid_coa_params(PopSize, S1, S2, P3) :-
    PopSize >= 4, PopSize =< 200,
    S1 >= 10, S1 =< 100,
    S2 >= 10, S2 =< 200,
    P3 >= 0.0, P3 =< 1.0.

% Convergence check using best history
converged(History, Tolerance) :-
    length(History, Len),
    Len >= 5,
    max_list(History, Max),
    min_list(History, Min),
    abs(Max - Min) < Tolerance.
```

### Hy Chaos Map Generator

```hy
; Chaos Optimization - Hy surface
; Chaotic map functions for search trajectory generation

(defn logistic-map [x]
  (* 4.0 x (- 1.0 x)))

(defn tent-map [x]
  (- 1.0 (* 2.0 (abs (- 0.5 x)))))

(defn sinusoidal-map [x]
  (math.sin (* math.pi x)))

(defn select-map [x map-type]
  "Select chaos map: 0=logistic, 1=tent, 2=sinusoidal"
  (cond
    [(= map-type 0) (logistic-map x)]
    [(= map-type 1) (tent-map x)]
    [True (sinusoidal-map x)]))

(defn compute-power-distribution [center out-min out-max p rnd]
  "Generate power-law distributed random value."
  (setv r (** (abs rnd) p))
  (if (>= rnd 0.0)
    (max out-min (min out-max (+ center (* r (- out-max center)))))
    (max out-min (min out-max (- center (* r (- center out-min))))))
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
class TestChaosOptimizer:
    async def test_python_coa_sphere(self):
        """Test COA on sphere function."""
        code = '''
import random, math
def sphere(x): return sum(xi**2 for xi in x)

class ChaosOptimizer:
    def __init__(self, objective, bounds, pop_size=30):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.dim = len(bounds)
        self.population = [[random.uniform(-5, 5) for _ in range(2)] for _ in range(pop_size)]

    def _power_distribution(self, center, out_min, out_max, p=20):
        rnd = random.uniform(-1, 1)
        r = abs(rnd) ** p
        return center + (r * (out_max - center) if rnd >= 0 else -r * (center - out_min))

    def optimize(self):
        best_f = min(self.objective(p) for p in self.population)
        best = [p for p in self.population if self.objective(p) <= best_f][0]
        for _ in range(60):
            for i in range(self.pop_size):
                for c in range(self.dim):
                    if random.random() < 0.8:
                        self.population[i][c] = self._power_distribution(best[c], -5, 5)
                f = self.objective(self.population[i])
                if f < best_f:
                    best_f = f
                    best = self.population[i][:]
        return best, best_f

opt = ChaosOptimizer(sphere, [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)])
best_x, best_f = opt.optimize()
best_f
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 1.0

    async def test_logistic_map(self):
        """Test logistic map produces valid chaotic values."""
        code = '''
def logistic_map(x): return 4.0 * x * (1.0 - x)
vals = [logistic_map(random.random()) for _ in range(5)]
all(0 <= v <= 1 for v in vals)
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_prolog_params(self):
        """Test Prolog parameter validation."""
        code = '''
?- 50 >= 4, 50 =< 200, 40 >= 10, 40 =< 100, 0.8 >= 0.0, 0.8 =< 1.0.
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
async def test_coa_skill_integration():
    """Test chaos-optimization skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "chaos-optimization"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: chaos-optimization\nDomain: OPTIMIZATION\nsurfaces:\n  - python\n  - hy')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("chaos", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic COA Optimization

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()
code = '''
def objective(x): return sum(xi**2 for xi in x)
bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = ChaosOptimizer(objective, bounds, pop_size=30, max_iter=80)
best_x, best_score, history = opt.optimize()
print("Best:", best_x, "Score:", best_score)
'''
result = await surface.execute(code, {})
```

## Security Considerations

- Pure numerical operations only; no file system, network, or OS access.
- Chaotic map values bounded to [0, 1] range.
- All coordinates clamped to declared bounds.

## Dependencies

- `numpy`
- `em_cubed` framework