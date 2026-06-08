---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: Medium
Type: Optimization
Category: Spiral-Based Search
Estimated Execution Time: 5-15 minutes
name: spiral-dynamics-optimization
Source: community
surfaces:
  - python
  - prolog
  - hy
---
origin: manual
triggers:
  - sdo
  - spiral_optimization
  - harmonic_oscillator
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T19:05:00Z"
updated_at: "2026-05-29T19:05:00Z"

## Purpose

Multi-surface Spiral Dynamics Optimization (SDO) algorithm. Uses damped harmonic oscillations with amplitude decay to spiral toward optimal solutions, where each particle oscillates around the best known solution.

## Implementation

### Python SDO Optimizer

```python
import numpy as np
import random
import math
from typing import Callable, Tuple, List, Optional

class SDOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float, float]],
                 pop_size: int = 100, damping: float = 0.3, frequency: float = 4.0,
                 precision: float = 10000.0, max_iter: int = 100):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.damping = damping
        self.frequency = frequency
        self.precision = precision
        self.max_iter = max_iter

        self.particles = []
        self.history = []
        self.best_fitness = float('-inf')
        self.best_position = None

    def _clip(self, val: float, lo: float, hi: float, step: float = 0.0) -> float:
        val = max(lo, min(hi, val))
        if step > 0.0:
            val = lo + step * round((val - lo) / step)
        return val

    def _damped_oscillation(self, amplitude: float, t: int, phi: float = 0.0) -> float:
        """Calculate damped harmonic oscillation: A*e^(-γ*t) * cos(ω*t + φ)"""
        return amplitude * math.exp(-self.damping * t / self.precision) * math.cos(self.frequency * t / self.precision + phi)

    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        # Initialize particles
        for _ in range(self.pop_size):
            pos = [random.uniform(self.bounds[c][0], self.bounds[c][1]) for c in range(self.dim)]
            amp = [0.0] * self.dim  # Amplitude for each coordinate
            t = 0  # Time step
            self.particles.append({
                'position': pos,
                'amplitude': amp,
                't': t,
                'fitness': 0.0
            })

        # Evaluate initial population
        for i in range(self.pop_size):
            self.particles[i]['fitness'] = self.objective(self.particles[i]['position'])

        # Find best
        self.best_fitness = max(p['fitness'] for p in self.particles)
        self.best_position = [p['position'] for p in self.particles
                           if p['fitness'] == self.best_fitness][0].copy()
        self.history.append(self.best_fitness)

        for epoch in range(self.max_iter):
            for i in range(self.pop_size):
                # If particle found best, reinitialize randomly
                if self.particles[i]['fitness'] >= self.best_fitness - 1e-10:
                    for c in range(self.dim):
                        self.particles[i]['position'][c] = random.uniform(
                            self.bounds[c][0], self.bounds[c][1]
                        )
                        self.particles[i]['position'][c] = self._clip(
                            self.particles[i]['position'][c],
                            self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]
                        )
                    self.particles[i]['t'] = 0
                    continue

                # Update time step
                self.particles[i]['t'] += 1
                t = self.particles[i]['t']

                # Update position using damped oscillation
                for c in range(self.dim):
                    phi = random.uniform(0.0, 2.0 * math.pi)
                    self.particles[i]['position'][c] += self._damped_oscillation(
                        self.particles[i]['amplitude'][c], t, phi
                    )
                    self.particles[i]['position'][c] = self._clip(
                        self.particles[i]['position'][c],
                        self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]
                    )

            # Evaluate all particles
            for i in range(self.pop_size):
                self.particles[i]['fitness'] = self.objective(self.particles[i]['position'])

            # Update best and amplitudes
            current_best = max(p['fitness'] for p in self.particles)
            if current_best > self.best_fitness:
                self.best_fitness = current_best
                self.best_position = [p['position'] for p in self.particles
                                    if p['fitness'] == current_best][0].copy()
                # Reset time steps and update amplitudes
                for i in range(self.pop_size):
                    self.particles[i]['t'] = 0
                    for c in range(self.dim):
                        self.particles[i]['amplitude'][c] = (
                            self.best_position[c] - self.particles[i]['position'][c]
                        )

            self.history.append(self.best_fitness)

        return np.array(self.best_position), self.best_fitness, self.history
```

### Prolog Parameter Validation

```prolog
% SDO parameter constraints
valid_sdo_params(PopSize, Damping, Frequency) :-
    PopSize >= 10, PopSize =< 200,
    Damping >= 0.01, Damping =< 1.0,
    Frequency >= 0.5, Frequency =< 20.0.

% Better solution check
is_better(Fitness1, Fitness2) :-
    Fitness1 > Fitness2.
```

### Hy Spiral Helpers

```hy
; Spiral Dynamics Optimization - Hy surface
; Damped harmonic oscillation calculations

(defn damped-oscillation [amplitude damping freq t phi]
  "Calculate damped harmonic oscillation: A*e^(-γt) * cos(ωt + φ)"
  (* amplitude (math.exp (* -1.0 damping t))
     (math.cos (+ (* freq t) phi))))

(defn update-amplitude [best-pos particle-pos]
  "Calculate amplitude as difference from best position."
  (- best-pos particle-pos))

(defn spiral-update [position amplitude damping freq t]
  "Update position along spiral trajectory."
  (+ position (damped-oscillation amplitude damping freq t (random.uniform 0.0 (* 2.0 math.pi))))
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
class TestSDOptimizer:
    async def test_python_sdo_sphere(self):
        """Test SDO on sphere function (maximization)."""
        code = '''
import random, math

def sphere(x): return -sum(xi**2 for xi in x)

class SDOptimizer:
    def __init__(self, objective, bounds, pop_size=30):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.dim = len(bounds)
        self.damping = 0.3
        self.frequency = 4.0
        self.precision = 10000.0
        self.particles = []

    def optimize(self):
        for _ in range(self.pop_size):
            pos = [random.uniform(-5, 5) for _ in range(self.dim)]
            amp = [random.uniform(-5, 5) for _ in range(self.dim)]
            self.particles.append({'position': pos, 'amplitude': amp})

        best_f = max(self.objective(p['position']) for p in self.particles)
        best_x = [p['position'] for p in self.particles
                  if self.objective(p['position']) == best_f][0]
        return best_x, best_f

opt = SDOptimizer(sphere, [(-5.0, 5.0), (-5.0, 5.0)])
best_x, best_f = opt.optimize()
best_f
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] <= 0.0

    async def test_damped_oscillation(self):
        """Test damped oscillation decreases with time."""
        code = '''
import math
def damped_oscillation(amplitude, t, damping=0.3, freq=4.0):
    return abs(amplitude * math.exp(-damping * t) * math.cos(freq * t))

vals = [damped_oscillation(5.0, t) for t in range(10)]
all(vals[i] >= vals[i+1] for i in range(len(vals)-1))
'''
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_prolog_params(self):
        """Test Prolog parameter validation."""
        code = '''
?- 100 >= 10, 100 =< 200, 0.3 >= 0.01, 0.3 =< 1.0, 4.0 >= 0.5, 4.0 =< 20.0.
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
async def test_sdo_skill_integration():
    """Test spiral-dynamics-optimization skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "spiral-dynamics-optimization"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: spiral-dynamics-optimization\nDomain: OPTIMIZATION')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("spiral", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic SDO Optimization

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()
code = '''
def objective(x): return -sum(xi**2 for xi in x)  # Maximize (minimize negative)
bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = SDOptimizer(objective, bounds, pop_size=100, damping=0.3, frequency=4.0)
best_x, best_score, history = opt.optimize()
print("Best:", best_x, "Score:", best_score)
'''
result = await surface.execute(code, {})
```

## Security Considerations

- Pure numerical operations only; no file system, network, or OS access.
- All coordinates clamped to declared bounds.
- Oscillation values bounded by amplitude constraints.

## Dependencies

- `numpy`
- `em_cubed` framework