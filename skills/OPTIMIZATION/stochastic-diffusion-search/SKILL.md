---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: Medium
Type: Optimization
Category: Swarm Intelligence
Estimated Execution Time: 5-20 minutes
name: stochastic-diffusion-search
Source: community
surfaces:
  - python
  - prolog
  - datalog
  - janus
---
origin: manual
triggers:
  - stochastic_diffusion_search
  - global_optimization
  - agent_based_search
  - restaurant_game
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T18:32:00Z"
updated_at: "2026-05-29T18:32:00Z"

## Purpose

Multi-surface Stochastic Diffusion Search (SDS) optimizer. Models a self-organizing dynamic swarm of communicating agents to identify the global optimum of a continuous optimization landscape. Uses partial candidate evaluations and pairwise peer communication to diffuse promising search hypotheses (restaurants/hills), preventing local minima entrapment.

## Implementation

### Python SDS Optimizer

```python
import numpy as np
import random
from typing import Callable, Tuple, List, Optional

class Candidate:
    def __init__(self, dim: int):
        self.raddr = [0] * dim
        self.raddr_prev = [0] * dim
        self.c = [0.0] * dim
        self.c_prev = [0.0] * dim
        self.f = float('inf')
        self.f_prev = float('inf')

class SDSOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float, float]],
                 pop_size: int = 50, rest_numb: int = 100,
                 probab_rest: float = 0.1, max_iter: int = 100):
        """
        bounds: List of (min, max, step) for each coordinate.
        """
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
        self.best_score = float('inf')
        self.history = []

    def _se_in_di_sp(self, val: float, min_val: float, max_val: float, step: float) -> float:
        if val <= min_val:
            return min_val
        if val >= max_val:
            return max_val
        if step == 0.0:
            return val
        return min_val + step * round((val - min_val) / step)

    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        for gen in range(self.max_iter):
            # 1. First iteration initialization / sample
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
            
            # 2. Evaluate fitness & update global best
            for i in range(self.pop_size):
                self.cands[i].f = self.objective(self.cands[i].c)
                if self.cands[i].f < self.best_score:
                    self.best_score = self.cands[i].f
                    self.best_x = self.cands[i].c.copy()
            
            self.history.append(float(self.best_score))
            
            # 3. Update personal bests
            for i in range(self.pop_size):
                if self.cands[i].f < self.cands[i].f_prev:
                    self.cands[i].f_prev = self.cands[i].f
                    self.cands[i].c_prev = self.cands[i].c.copy()
                    self.cands[i].raddr_prev = self.cands[i].raddr.copy()
            
            # Skip diffusion on last generation
            if gen == self.max_iter - 1:
                break
                
            # 4. Diffusion and tasting step
            for i in range(self.pop_size):
                for c in range(self.dim):
                    # Select a random peer
                    n = random.randint(0, self.pop_size - 1)
                    
                    if self.cands[n].f_prev < self.cands[i].f_prev:
                        # Diffuse: borrow peer's successful restaurant address
                        self.cands[i].raddr[c] = self.cands[n].raddr_prev[c]
                    else:
                        # Non-active choice
                        if random.uniform(0.0, 1.0) < self.probab_rest:
                            self.cands[i].raddr[c] = random.randint(0, self.rest_numb - 1)
                        else:
                            self.cands[i].raddr[c] = self.cands[i].raddr_prev[c]
                    
                    # Sample a new dish coordinate in the selected restaurant space
                    min_v = self.bounds[c][0] + self.rest_space[c] * self.cands[i].raddr[c]
                    max_v = min_v + self.rest_space[c]
                    dish = random.uniform(min_v, max_v)
                    self.cands[i].c[c] = self._se_in_di_sp(dish, self.bounds[c][0], self.bounds[c][1], self.bounds[c][2])
                    
        return np.array(self.best_x), self.best_score, self.history
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
% Represent the social network of agents and active hypothesis propagation
% Schema:
%   agent_fprev(AgentId, Fitness)
%   agent_raddr_prev(AgentId, CoordIndex, RestaurantAddr)
%   peer_choice(AgentId, PeerId)
%   random_restaurant(AgentId, CoordIndex, RandomRAddr)

% AgentId copies PeerId's successful hypothesis (active hypothesis evaluation)
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

### Janus/QuickJS Agent State Transition

```javascript
// Lightweight state transition for quick evaluation of agent fitness
function evaluateAgentTransition(currentScore, previousScore, randomChance, thresholdProb) {
    let state = "inactive";
    if (currentScore < previousScore) {
        state = "active"; // Found a better hypothesis
    } else if (randomChance < thresholdProb) {
        state = "exploring"; // Explore random space
    } else {
        state = "retaining"; // Keep current space
    }
    return { status: state };
}
```

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface, PrologSurface, DatalogSurface

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
        code = '''
import numpy as np

def sphere(x):
    return sum(xi**2 for xi in x)

bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = SDSOptimizer(sphere, bounds, pop_size=30, rest_numb=50, probab_rest=0.1, max_iter=80)
best_x, best_score, history = opt.optimize()
print(f"best_score={best_score}")
best_score
'''
        result = await py_surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 1.0

    async def test_prolog_parameters(self, prolog_surface):
        """Test Prolog parameter checking rules for SDS."""
        code = '''
valid_sds_params(PopSize, RestNumb, ProbabRest) :-
    PopSize >= 4, PopSize =< 1000,
    RestNumb >= 10, RestNumb =< 10000,
    ProbabRest >= 0.0, ProbabRest =< 1.0.

?- valid_sds_params(50, 100, 0.1).
'''
        result = await prolog_surface.execute(code, {})
        assert result["status"] == "ok"
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_sds_skill_integration():
    """Test the stochastic-diffusion-search skill in a search registry pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "stochastic-diffusion-search"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: stochastic-diffusion-search
Domain: OPTIMIZATION
surfaces:
  - python
  - prolog
  - datalog
---
## Purpose
SDS global optimizer
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        results = search_registry("diffusion", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic SDS Optimization (Sphere Function)

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

code = '''
def objective(x):
    return sum(xi**2 for xi in x)

# Define bounds: (min, max, step)
bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
opt = SDSOptimizer(objective, bounds, pop_size=30, rest_numb=80, probab_rest=0.1, max_iter=50)
best_x, best_score, history = opt.optimize()
print("Best X:", best_x)
print("Best Score:", best_score)
'''
result = await surface.execute(code, {})
```

## Security Considerations

- Relies entirely on secure numerical transformations via standard library loops and `numpy`.
- No file system, network, or OS modifications are possible during evaluation.
- Strictly safe thread isolation during background executions.

## Dependencies

- `numpy`
- `em_cubed` framework
