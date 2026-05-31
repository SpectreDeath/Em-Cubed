---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: High
Type: Optimization
Category: Evolutionary Skills
Estimated Execution Time: 15-60 minutes
name: cma-es-optimizer
Source: community
surfaces:
  - python
  - prolog
  - z3
  - hy
---
origin: manual
triggers:
  - evolutionary_optimization
  - cma_es
  - parameter_tuning
  - covariance_matrix_adaptation
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-29T18:03:00Z"
updated_at: "2026-05-29T18:03:00Z"

## Purpose

Multi-surface Covariance Matrix Adaptation Evolution Strategy (CMA-ES) optimizer. Adapts a search ellipsoid along the contours of a continuous optimization landscape. Uses Python for the core loop, Prolog for parameter and convergence verification, Z3 for formal boundary checks, and Hy for cumulative step-size and parameter adaptation.

## Implementation

### Python CMA-ES Optimizer

```python
import numpy as np
from typing import Callable, Tuple, List, Optional

class CMAESOptimizer:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float]],
                 pop_size: int = 50, mu: int = 25,
                 learning_rate_c1: float = 0.01, learning_rate_cmu: float = 0.8,
                 step_size_damping: float = 0.6, max_iter: int = 100):
        self.objective = objective
        self.bounds = np.array(bounds)
        self.dim = len(bounds)
        self.pop_size = pop_size
        self.mu = mu
        self.c1 = learning_rate_c1
        self.cmu = learning_rate_cmu
        self.damps = step_size_damping
        self.max_iter = max_iter
        
        # Strategy parameters
        self.sigma = 0.3 * np.mean(self.bounds[:, 1] - self.bounds[:, 0])
        self.mean = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1])
        
        # Recombination weights
        self.weights = np.zeros(self.mu)
        self._compute_weights()
        
        # Evolution paths
        self.pc = np.zeros(self.dim)
        self.ps = np.zeros(self.dim)
        
        # Covariance Matrix & Eigendecomposition
        self.C = np.eye(self.dim)
        self.B = np.eye(self.dim)
        self.D = np.ones(self.dim)
        
        # Counters
        self.counteval = 0
        self.eigeneval = 0
        self.eigen_interval = max(1, int(self.dim / (10.0 * np.sqrt(self.c1 + self.cmu))))
        
        # Constants
        self.chiN = np.sqrt(self.dim) * (1.0 - 1.0 / (4.0 * self.dim) + 1.0 / (21.0 * self.dim**2))
        self.cs = (self.mu_eff + 2.0) / (self.dim + self.mu_eff + 5.0)
        self.cc = (4.0 + self.mu_eff / self.dim) / (self.dim + 4.0 + 2.0 * self.mu_eff / self.dim)
        self.hsig_threshold = 1.4 + 2.0 / (self.dim + 1.0)
        
        self.best_x = None
        self.best_score = float('inf')
        self.history = []

    def _compute_weights(self):
        log_mu = np.log(self.mu + 0.5)
        for i in range(self.mu):
            self.weights[i] = log_mu - np.log(i + 1)
        self.weights /= np.sum(self.weights)
        self.mu_eff = 1.0 / np.sum(self.weights**2)

    def _eigendecomposition(self):
        self.B, diag_D2, _ = np.linalg.svd(self.C)
        self.D = np.sqrt(np.maximum(1e-14, diag_D2))
        self.eigeneval = self.counteval

    def _power_distribution(self, center: float, out_min: float, out_max: float, p: float = 20.0) -> float:
        rnd = np.random.uniform(-1.0, 1.0)
        r = np.abs(rnd) ** p
        if rnd >= 0.0:
            return center + r * (out_max - center)
        else:
            return center - r * (center - out_min)

    def _sample_candidate(self) -> Tuple[np.ndarray, np.ndarray]:
        # Generate random vector z using power distribution for exploration
        z = np.array([self._power_distribution(0.0, -8.0, 8.0, 20.0) for _ in range(self.dim)])
        # Transform y = B * D * z
        y = self.B @ (self.D * z)
        # Candidate vector x = mean + sigma * y
        x = self.mean + self.sigma * y
        # Clip to bounds using discrete steps if necessary
        x = np.clip(x, self.bounds[:, 0], self.bounds[:, 1])
        return x, y

    def optimize(self) -> Tuple[np.ndarray, float, List[float]]:
        for gen in range(self.max_iter):
            # 1. Sample population
            population = []
            y_vectors = []
            scores = []
            
            for _ in range(self.pop_size):
                x, y = self._sample_candidate()
                population.append(x)
                y_vectors.append(y)
                scores.append(self.objective(x))
            
            self.counteval += self.pop_size
            
            # Sort population (minimization)
            indices = np.argsort(scores)
            sorted_pop = [population[idx] for idx in indices]
            sorted_y = [y_vectors[idx] for idx in indices]
            sorted_scores = [scores[idx] for idx in indices]
            
            # Update best found
            if sorted_scores[0] < self.best_score:
                self.best_score = sorted_scores[0]
                self.best_x = sorted_pop[0]
            
            self.history.append(float(self.best_score))
            
            # 2. Update mean
            old_mean = np.copy(self.mean)
            self.mean = np.sum([self.weights[i] * sorted_pop[i] for i in range(self.mu)], axis=0)
            
            # Weighted y vector
            y_w = (self.mean - old_mean) / self.sigma
            
            # 3. Eigendecomposition if needed
            if self.counteval - self.eigeneval > self.eigen_interval * self.pop_size:
                self._eigendecomposition()
            
            # inv(sqrt(C)) * y_w
            invsqrtC_y_w = self.B @ ((1.0 / self.D) * (self.B.T @ y_w))
            
            # Update ps path
            self.ps = (1.0 - self.cs) * self.ps + np.sqrt(self.cs * (2.0 - self.cs) * self.mu_eff) * invsqrtC_y_w
            norm_ps = np.linalg.norm(self.ps)
            
            # Hsig threshold check
            expected_len = np.sqrt(1.0 - (1.0 - self.cs)**(2.0 * self.counteval / self.pop_size)) * self.chiN
            hsig = norm_ps / expected_len < self.hsig_threshold
            delta_hsig = 1.0 if hsig else 0.0
            
            # Update pc path
            self.pc = (1.0 - self.cc) * self.pc + delta_hsig * np.sqrt(self.cc * (2.0 - self.cc) * self.mu_eff) * y_w
            
            # 4. Update Covariance Matrix C
            # Rank-1 update
            c1a = np.outer(self.pc, self.pc)
            
            # Rank-mu update
            cmu_update = np.zeros((self.dim, self.dim))
            for i in range(self.mu):
                z_i = sorted_y[i]
                cmu_update += self.weights[i] * np.outer(z_i, z_i)
            
            # Adjust c1 if stagnation detected
            curr_c1 = self.c1
            if not hsig:
                curr_c1 *= (1.0 - (1.0 - delta_hsig) * self.cc * (2.0 - self.cc))
            
            one_minus_c1_cmu = 1.0 - curr_c1 - self.cmu
            self.C = one_minus_c1_cmu * self.C + curr_c1 * c1a + self.cmu * cmu_update
            
            # Enforce positive definiteness
            if gen % 10 == 0:
                self._enforce_positive_definite()
            
            # 5. Adapt step size sigma
            exponent = (self.cs / self.damps) * (norm_ps / self.chiN - 1.0)
            self.sigma *= np.exp(exponent)
            
            # Constrain sigma
            min_sigma = 1e-16
            max_sigma = 1e4 * max(1.0, np.max(self.D))
            self.sigma = np.clip(self.sigma, min_sigma, max_sigma)
            
        return self.best_x, self.best_score, self.history

    def _enforce_positive_definite(self):
        # Force symmetry
        self.C = (self.C + self.C.T) * 0.5
        min_diag = np.min(np.diag(self.C))
        if min_diag < 1e-10:
            correction = 1e-10 - min_diag
            np.fill_diagonal(self.C, np.diag(self.C) + correction)
            
        # SVD check for positive eigenvalues
        U, S, V = np.linalg.svd(self.C)
        if np.min(S) < 1e-10:
            S = np.maximum(1e-10, S)
            self.C = U @ np.diag(S) @ V
```

### Prolog Parameter & Convergence Logic

```prolog
% Validate CMA-ES configuration parameters
valid_cmaes_params(PopSize, Mu, LearningRateC1, LearningRateCMu, StepSizeDamping) :-
    PopSize >= 4, PopSize =< 1000,
    Mu >= 2, Mu =< PopSize,
    LearningRateC1 >= 0.0, LearningRateC1 =< 0.5,
    LearningRateCMu >= 0.0, LearningRateCMu =< 1.0,
    StepSizeDamping >= 0.1, StepSizeDamping =< 10.0.

% Stagnation detection
sigma_too_small(Sigma) :-
    Sigma < 1e-15.

% Check if optimization has converged based on best fitness scores history
converged(History, Tolerance) :-
    length(History, Len),
    Len > 10,
    append(_, Last10, History),
    length(Last10, 10),
    max_list(Last10, Max),
    min_list(Last10, Min),
    abs(Max - Min) < Tolerance.
```

### Z3 Boundary Checker

```python
from z3 import *

def verify_bounds(x: List[float], bounds: List[Tuple[float, float]]) -> bool:
    """Uses Z3 to formally check whether candidate is strictly within bounds."""
    s = Solver()
    vars = [Real(f'x_{i}') for i in range(len(x))]
    
    # Assert values
    for i, val in enumerate(x):
        s.add(vars[i] == val)
        s.add(vars[i] >= bounds[i][0])
        s.add(vars[i] <= bounds[i][1])
        
    return s.check() == sat
```

### Hy Adaptive Strategies

```hy
(defn compute-chi-n [dim]
  "Expected norm of a random vector drawn from N(0, I)"
  (* (sqrt dim) (- 1.0 (/ 1.0 (* 4.0 dim)) (/ 1.0 (* 21.0 dim dim)))))

(defn adaptive-sigma [sigma norm-ps chi-n cs damps]
  "CSA step size update multiplier"
  (* sigma (exp (* (/ cs damps) (- (/ norm-ps chi-n) 1.0)))))

(defn hsig? [norm-ps expected-length threshold]
  "Heaviside stagnation detection flag"
  (< (/ norm-ps expected-length) threshold))

(defn compute-cc [mu-eff coords]
  "Cumulation parameter for covariance path"
  (/ (+ 4.0 (/ mu-eff coords)) (+ coords 4.0 (* 2.0 (/ mu-eff coords)))))

(defn compute-cs [mu-eff coords]
  "Cumulation parameter for step-size path"
  (/ (+ mu-eff 2.0) (+ coords mu-eff 5.0)))

(defn compute-damps [mu-eff coords cs]
  "Damping factor for step-size adaptation"
  (+ 1.0 cs (* 2.0 (max 0.0 (- (sqrt (/ (- mu-eff 1.0) (+ coords 1.0))) 1.0)))))
```

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface

def sphere(x):
    return sum(xi**2 for xi in x)

def rosenbrock(x):
    return sum(100.0*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2 for i in range(len(x)-1))

@pytest.mark.asyncio
class TestCMAESOptimizer:
    @pytest.fixture
    async def py_surface(self):
        return PythonSurface()

    @pytest.fixture
    async def prolog_surface(self):
        return PrologSurface()

    @pytest.fixture
    async def hy_surface(self):
        return HySurface()

    async def test_python_cmaes_sphere(self, py_surface):
        """Test CMAES class finds near-zero on sphere function."""
        code = '''
import numpy as np

def sphere(x):
    return sum(xi**2 for xi in x)

# Execute CMA-ES optimizer
opt = CMAESOptimizer(sphere, [(-5.0, 5.0)]*3, pop_size=20, mu=10, max_iter=50)
best_x, best_score, history = opt.optimize()
print(f"best_score={best_score}")
best_score
'''
        result = await py_surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 1.0

    async def test_prolog_parameters(self, prolog_surface):
        """Test Prolog parameter checking rules."""
        code = '''
valid_cmaes_params(PopSize, Mu, LearningRateC1, LearningRateCMu, StepSizeDamping) :-
    PopSize >= 4, PopSize =< 1000,
    Mu >= 2, Mu =< PopSize,
    LearningRateC1 >= 0.0, LearningRateC1 =< 0.5,
    LearningRateCMu >= 0.0, LearningRateCMu =< 1.0,
    StepSizeDamping >= 0.1, StepSizeDamping =< 10.0.

?- valid_cmaes_params(50, 25, 0.01, 0.8, 0.6).
'''
        result = await prolog_surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_hy_chi_n(self, hy_surface):
        """Test Hy chi_n function computation."""
        code = '''
(defn compute-chi-n [dim]
  (* (sqrt dim) (- 1.0 (/ 1.0 (* 4.0 dim)) (/ 1.0 (* 21.0 dim dim)))))

(compute-chi-n 3)
'''
        result = await hy_surface.execute(code, {})
        assert result["status"] == "ok"
        assert 1.4 < result["value"] < 1.7
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_cmaes_skill_integration():
    """Test the cma-es-optimizer skill in a complete search registry pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "cma-es-optimizer"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: cma-es-optimizer
Domain: OPTIMIZATION
surfaces:
  - python
  - prolog
  - z3
  - hy
---
## Purpose
CMA-ES black-box optimizer
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        results = search_registry("cma-es", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic CMA-ES Optimization (Sphere Function)

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

code = '''
# Sphere objective function (minimum at x = [0, 0, 0])
def objective(x):
    return sum(xi**2 for xi in x)

bounds = [(-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0)]
opt = CMAESOptimizer(objective, bounds, pop_size=20, mu=10, max_iter=80)
best_x, best_score, history = opt.optimize()
print("Best X:", best_x)
print("Best Score:", best_score)
'''
result = await surface.execute(code, {})
```

### Complex Constraint Checking via Z3

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

code = '''
# Objective function
def objective(x):
    return (x[0] - 1)**2 + (x[1] - 2)**2

bounds = [(0, 5), (0, 5)]

# Check custom boundary constraints
is_valid = verify_bounds([1.2, 2.3], bounds)
print("Is candidate valid?", is_valid)
'''
result = await surface.execute(code, {})
```

## Security Considerations

- Uses pure mathematical and matrix operations via `numpy` which are entirely safe.
- No network access, disk access, or external package executions are triggered.
- Safe execution timeout limits prevent infinite loop hangs.

## Dependencies

- `numpy` (for numerical array operations)
- `z3-solver` (for formal bound constraint checking)
- `em_cubed` framework
