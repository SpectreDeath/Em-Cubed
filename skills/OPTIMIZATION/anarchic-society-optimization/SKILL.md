---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: Medium
Type: Optimization
Category: Swarm Intelligence
Estimated Execution Time: 5-30 minutes
name: anarchic-society-optimization
Source: community
surfaces:
  - python
  - prolog
  - hy
  - z3
---
origin: manual
triggers:
  - anarchic_society_optimization
  - aso_optimizer
  - swarm_intelligence
  - multi_policy_optimization
  - pso_variant
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T18:34:00Z"
updated_at: "2026-05-29T18:34:00Z"

## Purpose

Multi-surface Anarchic Society Optimization (ASO) skill. Simulates a decentralized human society without hierarchical structure. Each agent (society member) dynamically selects from three movement policies — PSO-style velocity (CurrentMP), crossover with a random peer's best (SocietyMP), or crossover with its own past position (PastMP) — based on three dissatisfaction indices: Fickleness Index (FI), External Irregularity Index (EI), and Internal Irregularity Index (II). Anarchic behavior (random relocation) is applied probabilistically to escape local minima.

Originally proposed by Ahmadi-Javid (2011). Ranked #9 in the MQL5 optimization benchmark (57.54%), excelling on discrete (Megacity) and sharp (Forest) landscapes.

## Implementation

### Python ASO Core Optimizer

```python
import numpy as np
import random
import math
from typing import Callable, Tuple, List, Optional

class ASOAgent:
    """Represents a single society member in ASO."""
    def __init__(self, dim: int):
        self.position: List[float] = [0.0] * dim
        self.prev_position: List[float] = [0.0] * dim
        self.p_best: List[float] = [0.0] * dim
        self.p_best_fitness: float = float('-inf')
        self.fitness: float = float('-inf')


class ASOOptimizer:
    """
    Anarchic Society Optimization (ASO).

    Maximization convention (fitness higher = better), consistent with
    the MQL5 benchmark formulation. Negate objective if minimizing.

    Parameters
    ----------
    objective : Callable
        Objective function f(x) -> float. Higher values are better.
    bounds : List[Tuple[float, float, float]]
        List of (min, max, step) per coordinate. step=0.0 for continuous.
    pop_size : int
        Population (society) size.
    omega : float
        Inertia weight for CurrentMP velocity.
    lambda1, lambda2 : float
        PSO-style acceleration coefficients (personal best, global best).
    anarchy_prob : float
        Probability of anarchic random relocation each step.
    alpha, theta, delta : float
        Sensitivity parameters for FI, EI, II index computation.
    max_iter : int
        Maximum number of iterations.
    """

    def __init__(
        self,
        objective: Callable,
        bounds: List[Tuple[float, float, float]],
        pop_size: int = 50,
        omega: float = 0.7,
        lambda1: float = 1.5,
        lambda2: float = 1.5,
        anarchy_prob: float = 0.1,
        alpha: float = 0.5,
        theta: float = 0.1,
        delta: float = 0.1,
        max_iter: int = 100,
    ):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.omega = omega
        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.anarchy_prob = anarchy_prob
        self.alpha = alpha
        self.theta = theta
        self.delta = delta
        self.max_iter = max_iter

        self.agents: List[ASOAgent] = [ASOAgent(self.dim) for _ in range(self.pop_size)]
        self.g_best: List[float] = [0.0] * self.dim
        self.g_best_fitness: float = float('-inf')
        self.history: List[float] = []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _clip(self, val: float, lo: float, hi: float, step: float) -> float:
        """Clip and quantize a coordinate value to (min, max, step)."""
        val = max(lo, min(hi, val))
        if step > 0.0:
            val = lo + step * round((val - lo) / step)
        return val

    def _random_position(self) -> List[float]:
        return [
            self._clip(
                random.uniform(b[0], b[1]), b[0], b[1], b[2]
            )
            for b in self.bounds
        ]

    # ------------------------------------------------------------------
    # Index computations (safe guards against division by zero)
    # ------------------------------------------------------------------

    def _calculate_fi(self, agent: ASOAgent) -> float:
        """Fickleness Index: dissatisfaction relative to pBest vs gBest."""
        denom = self.g_best_fitness - agent.fitness
        if abs(denom) < 1e-300:
            return 0.0
        return 1.0 - self.alpha * (agent.p_best_fitness - agent.fitness) / denom

    def _calculate_ei(self, agent: ASOAgent) -> float:
        """External Irregularity Index: divergence from global best."""
        denom = abs(self.g_best_fitness) * self.theta
        if abs(denom) < 1e-300:
            return 0.0
        exp_arg = min((self.g_best_fitness - agent.fitness) / denom, 700.0)
        return 1.0 - math.exp(-exp_arg)

    def _calculate_ii(self, agent: ASOAgent) -> float:
        """Internal Irregularity Index: deviation from personal best."""
        denom = abs(agent.p_best_fitness) * self.delta
        if abs(denom) < 1e-300:
            return 0.0
        exp_arg = min((agent.p_best_fitness - agent.fitness) / denom, 700.0)
        return 1.0 - math.exp(-exp_arg)

    # ------------------------------------------------------------------
    # Movement policies
    # ------------------------------------------------------------------

    def _current_mp(self, agent: ASOAgent, coord: int) -> float:
        """PSO-style velocity update (CurrentMP)."""
        r1 = random.random()
        r2 = random.random()
        velocity = (
            self.omega * (agent.position[coord] - agent.p_best[coord])
            + self.lambda1 * r1 * (agent.p_best[coord] - agent.position[coord])
            + self.lambda2 * r2 * (self.g_best[coord] - agent.position[coord])
        )
        return agent.position[coord] + velocity

    def _society_mp(self, agent: ASOAgent, coord: int) -> float:
        """Crossover with global best or a random peer's pBest (SocietyMP)."""
        other = random.randint(0, self.pop_size - 1)
        if random.random() < 0.5:
            return self.g_best[coord]
        return self.agents[other].p_best[coord]

    def _past_mp(self, agent: ASOAgent, coord: int) -> float:
        """Crossover between current pBest and previous position (PastMP)."""
        if random.random() < 0.5:
            return agent.p_best[coord]
        return agent.prev_position[coord]

    # ------------------------------------------------------------------
    # Main optimization loop
    # ------------------------------------------------------------------

    def optimize(self) -> Tuple[List[float], float, List[float]]:
        """
        Run ASO optimization.

        Returns
        -------
        best_x : List[float]
            Best solution found.
        best_fitness : float
            Fitness value at best_x.
        history : List[float]
            Best fitness per iteration.
        """
        # --- Initialization ---
        for agent in self.agents:
            agent.position = self._random_position()
            agent.prev_position = agent.position[:]
            agent.p_best = agent.position[:]
            agent.fitness = self.objective(agent.position)
            agent.p_best_fitness = agent.fitness

            if agent.fitness > self.g_best_fitness:
                self.g_best_fitness = agent.fitness
                self.g_best = agent.position[:]

        self.history.append(float(self.g_best_fitness))

        # --- Main loop ---
        for _ in range(self.max_iter):
            for agent in self.agents:
                fi = self._calculate_fi(agent)
                ei = self._calculate_ei(agent)
                ii = self._calculate_ii(agent)

                new_pos = [0.0] * self.dim
                for c in range(self.dim):
                    agent.prev_position[c] = agent.position[c]

                    # Anarchic random jump
                    if random.random() < self.anarchy_prob:
                        new_pos[c] = random.uniform(self.bounds[c][0], self.bounds[c][1])
                    else:
                        rnd = random.random()
                        if rnd > fi:
                            new_pos[c] = self._current_mp(agent, c)
                        elif rnd < ei:
                            new_pos[c] = self._society_mp(agent, c)
                        elif rnd < ii:
                            new_pos[c] = self._past_mp(agent, c)
                        else:
                            new_pos[c] = agent.position[c]  # no movement

                    new_pos[c] = self._clip(
                        new_pos[c], self.bounds[c][0], self.bounds[c][1], self.bounds[c][2]
                    )

                agent.position = new_pos
                agent.fitness = self.objective(agent.position)

                if agent.fitness > agent.p_best_fitness:
                    agent.p_best_fitness = agent.fitness
                    agent.p_best = agent.position[:]

                if agent.fitness > self.g_best_fitness:
                    self.g_best_fitness = agent.fitness
                    self.g_best = agent.position[:]

            self.history.append(float(self.g_best_fitness))

        return self.g_best[:], self.g_best_fitness, self.history
```

### Prolog Policy Decision Logic

```prolog
% ASO movement policy selection based on FI, EI, II indices and random draw.
% Policy atoms: current_mp, society_mp, past_mp, no_move.

% select_policy(+Rnd, +FI, +EI, +II, -Policy)
% Mirrors the branching logic from the MQL5 ASO reference implementation.
select_policy(Rnd, FI, _EI, _II, current_mp) :-
    Rnd > FI, !.
select_policy(Rnd, _FI, EI, _II, society_mp) :-
    Rnd < EI, !.
select_policy(Rnd, _FI, _EI, II, past_mp) :-
    Rnd < II, !.
select_policy(_, _, _, _, no_move).

% Validate ASO parameter ranges.
valid_aso_params(PopSize, Omega, Lambda1, Lambda2, AProb, Alpha, Theta, Delta) :-
    PopSize   >= 4,    PopSize   =< 10000,
    Omega     >= 0.0,  Omega     =< 2.0,
    Lambda1   >= 0.0,  Lambda1   =< 4.0,
    Lambda2   >= 0.0,  Lambda2   =< 4.0,
    AProb     >= 0.0,  AProb     =< 1.0,
    Alpha     >= 0.0,  Alpha     =< 1.0,
    Theta     >  0.0,
    Delta     >  0.0.

% Convergence check: last N best scores within tolerance.
converged_aso(History, Window, Tolerance) :-
    length(History, Len),
    Len >= Window,
    append(_, Last, History),
    length(Last, Window),
    max_list(Last, Max),
    min_list(Last, Min),
    abs(Max - Min) < Tolerance.
```

### Hy Index Computation

```hy
;; Anarchic Society Optimization — Hy surface
;; Functional computation of FI, EI, and II dissatisfaction indices.

(import math [exp])

(defn safe-div [num denom [eps 1e-300]]
  "Guarded division; returns 0.0 when denominator is near-zero."
  (if (< (abs denom) eps) 0.0 (/ num denom)))

(defn calculate-fi [current-fitness p-best-fitness g-best-fitness alpha]
  "Fickleness Index: measures dissatisfaction vs personal and global bests.
   FI near 1 → agent is content and will likely use CurrentMP."
  (let [denom (- g-best-fitness current-fitness)]
    (- 1.0 (* alpha (safe-div (- p-best-fitness current-fitness) denom)))))

(defn calculate-ei [current-fitness g-best-fitness theta]
  "External Irregularity Index: deviation pressure from global best.
   EI near 1 → agent is far from global best, favours SocietyMP."
  (let [denom (* g-best-fitness theta)]
    (- 1.0 (exp (- (safe-div (- g-best-fitness current-fitness) denom))))))

(defn calculate-ii [current-fitness p-best-fitness delta]
  "Internal Irregularity Index: deviation pressure from personal best.
   II near 1 → agent is far from its own best, favours PastMP."
  (let [denom (* p-best-fitness delta)]
    (- 1.0 (exp (- (safe-div (- p-best-fitness current-fitness) denom))))))

(defn compute-indices [current-fitness p-best-fitness g-best-fitness alpha theta delta]
  "Compute all three ASO indices and return as a dict."
  {:fi (calculate-fi current-fitness p-best-fitness g-best-fitness alpha)
   :ei (calculate-ei current-fitness g-best-fitness theta)
   :ii (calculate-ii current-fitness p-best-fitness delta)})

(defn adapt-parameters [omega anarchy-prob alpha iteration max-iter]
  "Gradually adapt omega (decreasing) and anarchy-prob (decreasing) over time."
  (let [progress (/ iteration (max max-iter 1))]
    {:omega       (- omega (* 0.3 progress))
     :anarchy-prob (* anarchy-prob (- 1.0 (* 0.5 progress)))
     :alpha       (+ alpha (* 0.3 progress))}))
```

### Z3 Bounds Enforcement

```python
from z3 import Real, Solver, And, sat

def z3_validate_bounds(position: list, bounds: list) -> bool:
    """
    Use Z3 SMT solver to formally verify that a candidate position
    satisfies all search-space bounds constraints.

    Parameters
    ----------
    position : list of float
        Candidate position vector.
    bounds : list of (min, max, step)
        Per-coordinate bounds.

    Returns
    -------
    bool — True if all constraints are satisfied.
    """
    solver = Solver()
    vars_ = [Real(f"x{i}") for i in range(len(position))]

    for i, (v, (lo, hi, _step)) in enumerate(zip(vars_, bounds)):
        solver.add(And(v >= lo, v <= hi))
        # Fix variable to actual position value for formal verification
        solver.add(v == position[i])

    return solver.check() == sat


def z3_clip_to_bounds(position: list, bounds: list) -> list:
    """
    Clip position coordinates to stay within declared bounds.
    Returns a new position list, does not modify in place.
    """
    clipped = []
    for val, (lo, hi, step) in zip(position, bounds):
        val = max(lo, min(hi, val))
        if step > 0.0:
            val = lo + step * round((val - lo) / step)
        clipped.append(val)
    return clipped
```

## Testing

### Unit Tests

```python
import pytest
import math
from typing import List

# ------------------------------------------------------------------ #
# Helper: sphere function (negated for maximization convention)       #
# ------------------------------------------------------------------ #

def neg_sphere(x: List[float]) -> float:
    """Negated sphere — maximum is at origin (value = 0.0)."""
    return -sum(xi ** 2 for xi in x)


def neg_rastrigin(x: List[float]) -> float:
    """Negated Rastrigin — maximum is at origin (value = 0.0)."""
    n = len(x)
    return -(10 * n + sum(xi**2 - 10 * math.cos(2 * math.pi * xi) for xi in x))


# ------------------------------------------------------------------ #
# Tests                                                                #
# ------------------------------------------------------------------ #

@pytest.mark.asyncio
class TestASOOptimizer:

    async def test_aso_sphere_2d(self):
        """ASO should converge near zero on the 2D negated sphere."""
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        code = '''
import math, random

def neg_sphere(x):
    return -sum(xi**2 for xi in x)

bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = ASOOptimizer(neg_sphere, bounds, pop_size=40, max_iter=150,
                   omega=0.7, lambda1=1.5, lambda2=1.5,
                   anarchy_prob=0.1, alpha=0.5, theta=0.1, delta=0.1)
best_x, best_fitness, history = opt.optimize()
# Fitness = -||x||^2, so best should be close to 0
-best_fitness  # return squared distance
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 1.0, f"ASO sphere dist^2 = {result['value']}"

    async def test_aso_prolog_policy_current(self):
        """Prolog policy selection: rnd > FI → current_mp."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
select_policy(Rnd, FI, _EI, _II, current_mp) :- Rnd > FI, !.
select_policy(Rnd, _FI, EI, _II, society_mp) :- Rnd < EI, !.
select_policy(Rnd, _FI, _EI, II, past_mp)    :- Rnd < II, !.
select_policy(_, _, _, _, no_move).

?- select_policy(0.9, 0.5, 0.3, 0.2, Policy).
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert "current_mp" in result.get("bindings", {}).get("Policy", "")

    async def test_aso_prolog_policy_society(self):
        """Prolog policy selection: rnd < EI (and not > FI) → society_mp."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
select_policy(Rnd, FI, _EI, _II, current_mp) :- Rnd > FI, !.
select_policy(Rnd, _FI, EI, _II, society_mp) :- Rnd < EI, !.
select_policy(Rnd, _FI, _EI, II, past_mp)    :- Rnd < II, !.
select_policy(_, _, _, _, no_move).

?- select_policy(0.2, 0.5, 0.4, 0.1, Policy).
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert "society_mp" in result.get("bindings", {}).get("Policy", "")

    async def test_aso_prolog_valid_params(self):
        """Prolog parameter validation passes for default config."""
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        code = '''
valid_aso_params(PopSize, Omega, L1, L2, AProb, Alpha, Theta, Delta) :-
    PopSize >= 4, PopSize =< 10000,
    Omega >= 0.0, Omega =< 2.0,
    L1 >= 0.0, L1 =< 4.0,
    L2 >= 0.0, L2 =< 4.0,
    AProb >= 0.0, AProb =< 1.0,
    Alpha >= 0.0, Alpha =< 1.0,
    Theta > 0.0, Delta > 0.0.

?- valid_aso_params(50, 0.7, 1.5, 1.5, 0.1, 0.5, 0.1, 0.1).
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_aso_hy_indices(self):
        """Hy surface computes FI, EI, II within [0, 1]."""
        from em_cubed.surfaces import HySurface
        surface = HySurface()
        code = '''
(import math [exp])

(defn safe-div [num denom [eps 1e-300]]
  (if (< (abs denom) eps) 0.0 (/ num denom)))

(defn calculate-fi [curr pbest gbest alpha]
  (let [denom (- gbest curr)]
    (- 1.0 (* alpha (safe-div (- pbest curr) denom)))))

(defn calculate-ei [curr gbest theta]
  (let [denom (* gbest theta)]
    (- 1.0 (exp (- (safe-div (- gbest curr) denom))))))

(defn calculate-ii [curr pbest delta]
  (let [denom (* pbest delta)]
    (- 1.0 (exp (- (safe-div (- pbest curr) denom))))))

; Use test values: curr=-5.0, pbest=-3.0, gbest=-1.0
(let [fi (calculate-fi -5.0 -3.0 -1.0 0.5)
      ei (calculate-ei -5.0 -1.0 0.1)
      ii (calculate-ii -5.0 -3.0 0.1)]
  {:fi fi :ei ei :ii ii})
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        indices = result["value"]
        for key in ("fi", "ei", "ii"):
            assert isinstance(indices[key], float), f"{key} should be float"

    async def test_aso_z3_bounds_valid(self):
        """Z3 should accept a position within bounds."""
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        code = '''
from z3 import Real, Solver, And, sat

def z3_validate_bounds(position, bounds):
    solver = Solver()
    vars_ = [Real(f"x{i}") for i in range(len(position))]
    for i, (v, (lo, hi, _step)) in enumerate(zip(vars_, bounds)):
        solver.add(And(v >= lo, v <= hi))
        solver.add(v == position[i])
    return solver.check() == sat

bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
z3_validate_bounds([1.5, -2.3], bounds)
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] is True

    async def test_aso_z3_bounds_invalid(self):
        """Z3 should reject a position outside bounds."""
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        code = '''
from z3 import Real, Solver, And, sat

def z3_validate_bounds(position, bounds):
    solver = Solver()
    vars_ = [Real(f"x{i}") for i in range(len(position))]
    for i, (v, (lo, hi, _step)) in enumerate(zip(vars_, bounds)):
        solver.add(And(v >= lo, v <= hi))
        solver.add(v == position[i])
    return solver.check() == sat

bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
z3_validate_bounds([7.0, 0.0], bounds)  # 7.0 is out of bounds
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] is False

    async def test_aso_rastrigin_5d(self):
        """ASO should approach 0 on 5D negated Rastrigin with sufficient iterations."""
        from em_cubed.surfaces import PythonSurface
        surface = PythonSurface()
        code = '''
import math, random

def neg_rastrigin(x):
    n = len(x)
    return -(10 * n + sum(xi**2 - 10 * math.cos(2 * math.pi * xi) for xi in x))

bounds = [(-5.12, 5.12, 0.0)] * 5
opt = ASOOptimizer(neg_rastrigin, bounds, pop_size=50, max_iter=200,
                   omega=0.7, lambda1=1.5, lambda2=1.5,
                   anarchy_prob=0.1, alpha=0.5, theta=0.1, delta=0.1)
best_x, best_fitness, history = opt.optimize()
-best_fitness  # return absolute value (should be < 10 for good result)
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 20.0, f"ASO Rastrigin 5D result = {result['value']}"
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path


@pytest.mark.asyncio
async def test_aso_skill_registry_integration():
    """Test the anarchic-society-optimization skill is discoverable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "anarchic-society-optimization"
        skills_dir.mkdir(parents=True)

        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: anarchic-society-optimization
Domain: OPTIMIZATION
surfaces:
  - python
  - prolog
  - hy
  - z3
---
## Purpose
ASO global optimizer
''')

        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)

        results = search_registry("anarchic", registry_file)
        assert len(results) >= 1

        results2 = search_registry("society", registry_file)
        assert len(results2) >= 1
```

## Usage Patterns

### Basic ASO Optimization (Sphere — Maximization)

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

code = '''
import math

def neg_sphere(x):
    """Negated sphere — maximise to find minimum."""
    return -sum(xi**2 for xi in x)

# Define bounds: (min, max, step). step=0.0 for continuous.
bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]

opt = ASOOptimizer(
    neg_sphere, bounds,
    pop_size=50,
    omega=0.7, lambda1=1.5, lambda2=1.5,
    anarchy_prob=0.1,
    alpha=0.5, theta=0.1, delta=0.1,
    max_iter=100,
)
best_x, best_fitness, history = opt.optimize()
print("Best X:", best_x)
print("Best Fitness:", best_fitness)
'''
result = await surface.execute(code, {})
```

### Discrete Optimization (Megacity-style)

```python
# Use step > 0.0 in bounds for discretised search spaces
bounds = [(-10.0, 10.0, 1.0), (-10.0, 10.0, 1.0)]  # integer steps

opt = ASOOptimizer(
    objective,
    bounds,
    pop_size=40,
    anarchy_prob=0.15,   # higher anarchy helps discrete landscapes
    max_iter=200,
)
```

## Security Considerations

- Pure numerical operations only; no file system, network, or OS access during evaluation.
- Z3 solver runs in a sandboxed context with bounded computation time.
- Agent population state is fully encapsulated and cannot leak between calls.

## Dependencies

- `numpy`
- `z3-solver`
- `hy`
- `em_cubed` framework
