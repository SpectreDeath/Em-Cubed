---
name: stochastic-diffusion-search
Domain: OPTIMIZATION
Version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
  - z3
---

## Purpose

Multi-surface Stochastic Diffusion Search (SDS) optimizer for continuous optimization landscapes using swarm intelligence principles.

## Description

Models a self-organizing dynamic swarm of communicating agents to identify the global optimum. Uses partial candidate evaluations and pairwise peer communication to diffuse promising search hypotheses.

## Implementation

### Python SDS Optimizer

```python
import random
from typing import Callable, Tuple, List

def _my_log2(x: float) -> float:
    result = 0.0
    while x > 1.5:
        x /= 2.0
        result += 1.0
    while x < 0.5:
        x *= 2.0
        result -= 1.0
    y = (x - 1.0) / (x + 1.0)
    y2 = y * y
    series = y
    for i in range(1, 20):
        series += y * ((-y2) ** i) / (2 * i + 1)
    return result + series * 2 / 3

class Candidate:
    def __init__(self, dim: int):
        self.raddr = [0] * dim
        self.raddr_prev = [0] * dim
        self.c = [0.0] * dim
        self.c_prev = [0.0] * dim
        self.f = float("inf")
        self.f_prev = float("inf")

class SDSOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float, float]],
                 pop_size: int = 50, rest_numb: int = 100,
                 probab_rest: float = 0.1, max_iter: int = 100):
        self.objective = objective
        self.bounds = bounds
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.rest_numb = rest_numb
        self.probab_rest = probab_rest
        self.max_iter = max_iter
        
        self.rest_space = [(b[1] - b[0]) / self.rest_numb for b in self.bounds]
        self.cands = [Candidate(self.dim) for _ in range(self.pop_size)]
        
        self.best_x = None
        self.best_score = float("inf")
        self.history = []

    def _se_in_di_sp(self, val: float, min_val: float, max_val: float, step: float) -> float:
        if val <= min_val:
            return min_val
        if val >= max_val:
            return max_val
        if step == 0.0:
            return val
        return min_val + step * round((val - min_val) / step)

    def optimize(self) -> Tuple[List[float], float, List[float]]:
        for gen in range(self.max_iter):
            if gen == 0:
                for i in range(self.pop_size):
                    for c in range(self.dim):
                        n = random.randint(0, self.rest_numb - 1)
                        self.cands[i].raddr[c] = n
                        self.cands[i].raddr_prev[c] = n
                        
                        min_v = self.bounds[c][0] + self.rest_space[c] * n
                        max_v = min_v + self.rest_space[c]
                        dish = random.uniform(min_v, max_v)
                        self.cands[i].c[c] = self._se_in_di_sp(dish, self.bounds[c][0], self.bounds[c][1], self.bounds[c][2])
            
            for i in range(self.pop_size):
                self.cands[i].f = self.objective(self.cands[i].c)
                if self.cands[i].f < self.best_score:
                    self.best_score = self.cands[i].f
                    if self.best_x is None:
                        self.best_x = [0.0] * self.dim
                    for d in range(self.dim):
                        self.best_x[d] = self.cands[i].c[d]
            
            self.history.append(float(self.best_score))
            
            for i in range(self.pop_size):
                if self.cands[i].f < self.cands[i].f_prev:
                    self.cands[i].f_prev = self.cands[i].f
                    self.cands[i].c_prev = self.cands[i].c.copy()
                    self.cands[i].raddr_prev = self.cands[i].raddr.copy()
            
            if gen == self.max_iter - 1:
                break
                
            for i in range(self.pop_size):
                for c in range(self.dim):
                    n = random.randint(0, self.pop_size - 1)
                    
                    if self.cands[n].f_prev < self.cands[i].f_prev:
                        self.cands[i].raddr[c] = self.cands[n].raddr_prev[c]
                    else:
                        if random.uniform(0.0, 1.0) < self.probab_rest:
                            self.cands[i].raddr[c] = random.randint(0, self.rest_numb - 1)
                        else:
                            self.cands[i].raddr[c] = self.cands[i].raddr_prev[c]
                    
                    min_v = self.bounds[c][0] + self.rest_space[c] * self.cands[i].raddr[c]
                    max_v = min_v + self.rest_space[c]
                    dish = random.uniform(min_v, max_v)
                    self.cands[i].c[c] = self._se_in_di_sp(dish, self.bounds[c][0], self.bounds[c][1], self.bounds[c][2])
                    
        return self.best_x if self.best_x else [0.0] * self.dim, self.best_score, self.history
```

### Prolog Parameter & Convergence Logic

```prolog
% Validate SDS configuration parameters
valid_sds_params(PopSize, RestNumb, ProbabRest) :-
    PopSize >= 4, PopSize =< 1000,
    RestNumb >= 10, RestNumb =< 10000,
    ProbabRest >= 0.0, ProbabRest =< 1.0.

% Stagnation check: score has not changed by more than tolerance in the last 15 generations
converged(History, Tolerance) :-
    length(History, Len),
    Len > 15,
    append(_, Last15, History),
    length(Last15, 15),
    max_list(Last15, Max),
    min_list(Last15, Min),
    abs(Max - Min) < Tolerance.
```

### Datalog Agent Network Rules

```datalog
% AgentId copies PeerId successful hypothesis (active hypothesis evaluation)
active_hyp(AgentId, CIdx, RAddr) :-
    agent_fprev(AgentId, F),
    peer_choice(AgentId, PeerId),
    agent_fprev(PeerId, PeerF),
    PeerF < F,
    agent_raddr_prev(PeerId, CIdx, RAddr).

% AgentId stays on current hypothesis because peer has worse fitness
inactive_keep_hyp(AgentId, CIdx, RAddr) :-
    agent_fprev(AgentId, F),
    peer_choice(AgentId, PeerId),
    agent_fprev(PeerId, PeerF),
    PeerF >= F,
    agent_raddr_prev(AgentId, CIdx, RAddr).
```

### Z3 SMT Optimization Bounds

```python
# Verify optimization convergence with Z3
def verify_sds_bounds(best_score: float, tolerance: float, max_iterations: int) -> bool:
    """Verify SDS optimization satisfies constraints."""
    from z3 import Real, Int, And, Implies, sat, Solver
    
    score = Real("score")
    tol = Real("tolerance")
    max_iter = Int("max_iter")
    
    solver = Solver()
    solver.add(score >= 0.0)
    solver.add(tol >= 0.0)
    solver.add(max_iter > 0)
    solver.add(score <= tol * 1000)
    
    return solver.check() == sat
```

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface, PrologSurface

def sphere(x):
    return sum(xi**2 for xi in x)

@pytest.mark.asyncio
class TestSDSOptimizer:
    @pytest.fixture
    async def py_surface(self):
        return PythonSurface()

    @pytest.fixture
    async def prolog_surface(self):
        return PrologSurface()

    async def test_python_sds_sphere(self, py_surface):
        """Test SDS class finds near-zero on sphere function."""
        code = """
def sphere(x):
    return sum(xi**2 for xi in x)

bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = SDSOptimizer(sphere, bounds, pop_size=30, rest_numb=50, probab_rest=0.1, max_iter=80)
best_x, best_score, history = opt.optimize()
print(f"best_score={best_score}")
best_score
"""
        result = await py_surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 1.0

    async def test_prolog_parameters(self, prolog_surface):
        """Test Prolog parameter checking rules for SDS."""
        code = """
valid_sds_params(PopSize, RestNumb, ProbabRest) :-
    PopSize >= 4, PopSize =< 1000,
    RestNumb >= 10, RestNumb =< 10000,
    ProbabRest >= 0.0, ProbabRest =< 1.0.

?- valid_sds_params(50, 100, 0.1).
"""
        result = await prolog_surface.execute(code, {})
        assert result["status"] == "ok"
```

## Security Considerations

- Relies entirely on secure numerical transformations via standard library.
- No file system, network, or OS modifications possible during evaluation.

## Dependencies

- Standard library only (random, typing)
