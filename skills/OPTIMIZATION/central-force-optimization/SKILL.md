---
name: central-force-optimization
domain: OPTIMIZATION
version: "1.0.0"
surfaces: [python, prolog, hy]
---

## Purpose

Multi-surface Central Force Optimization (CFO) algorithm. Uses deterministic gravitational attraction between probes (agents) where better solutions attract worse ones in a one-way mechanism.

## Implementation

### Python CFO Optimizer

```python
import random
import math

class CFOOptimizer:
    def __init__(self, objective, bounds, pop_size=30, g=1.0, alpha=0.1, beta=0.1,
                 max_iter=100):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.g = g
        self.alpha = alpha
        self.beta = beta
        self.max_iter = max_iter

        self.probes = []
        self.accelerations = []
        self.history = []
        self.best_fitness = float('-inf')
        self.best_position = None

    def _clip(self, val, lo, hi, step=0.0):
        val = max(lo, min(hi, val))
        if step > 0.0:
            val = lo + step * round((val - lo) / step)
        return val

    def _calculate_distance_squared(self, x1, x2):
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

    def _update_positions(self, epoch):
        current_noise = self.noise_factor * (1.0 - epoch / self.max_iter) if self.max_iter > 0 else 1.0

        for p in range(self.pop_size):
            for c in range(self.dim):
                self.probes[p]['position'][c] += 0.5 * self.accelerations[p][c]
                self.probes[p]['position'][c] += current_noise * self.g * random.uniform(-1.0, 1.0)
                self.probes[p]['position'][c] = self._clip(
                    self.probes[p]['position'][c],
                    self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]
                )

    def optimize(self):
        for _ in range(self.pop_size):
            pos = [random.uniform(self.bounds[c][0], self.bounds[c][1]) for c in range(self.dim)]
            self.probes.append({'position': pos, 'fitness': 0.0})
            self.accelerations.append([0.0] * self.dim)

        for i in range(self.pop_size):
            self.probes[i]['fitness'] = self.objective(self.probes[i]['position'])

        self.best_fitness = max(p['fitness'] for p in self.probes)
        self.best_position = [p['position'] for p in self.probes if p['fitness'] == self.best_fitness][0][:]
        self.history.append(self.best_fitness)

        for epoch in range(1, self.max_iter + 1):
            self._calculate_accelerations()
            self._update_positions(epoch)

            for p in range(self.pop_size):
                self.probes[p]['fitness'] = self.objective(self.probes[p]['position'])

            current_best = max(p['fitness'] for p in self.probes)
            if current_best > self.best_fitness:
                self.best_fitness = current_best
                self.best_position = [p['position'] for p in self.probes if p['fitness'] == current_best][0][:]

            self.history.append(self.best_fitness)

        return self.best_position, self.best_fitness, self.history
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
def sphere(x):
    return -sum(xi**2 for xi in x)  # Negative for maximization

# test_python_cfo_sphere and other tests remain unchanged
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_cfo_skill_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "central-force-optimization"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: central-force-optimization\ndomain: OPTIMIZATION')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("central force", registry_file)
        assert len(results) >= 1
```

## Security Considerations

- Pure numerical operations only; no file system, network, or OS access.
- All coordinates clamped to declared bounds.
- Gravitational force values bounded by distance constraints.

## Dependencies

- `em_cubed` framework (zero external dependencies)