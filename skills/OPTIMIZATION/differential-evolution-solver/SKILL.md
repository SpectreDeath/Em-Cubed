---
Domain: OPTIMIZATION
Version: 1.0.0
Complexity: High
Type: Optimization
Category: Evolutionary Skills
Estimated Execution Time: 10-30 minutes
name: differential-evolution-solver
Source: community
---
origin: manual
triggers:
  - evolutionary_optimization
  - differential_evolution
  - parameter_tuning
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:01:00Z"
updated_at: "2026-05-02T13:01:00Z"

## Purpose

Multi-surface differential evolution solver with Python for optimization, Prolog for constraint logic, and Hy for adaptive DE parameters.

## Implementation

### Python DE Solver

```python
import numpy as np
from typing import Callable, Tuple, List, Optional

class DifferentialEvolution:
    def __init__(self, objective: Callable, bounds: List[Tuple[float, float]],
                 pop_size: int = 15, F: float = 0.8, CR: float = 0.9,
                 max_iter: int = 1000):
        self.objective = objective
        self.bounds = bounds
        self.pop_size = pop_size
        self.F = F
        self.CR = CR
        self.max_iter = max_iter
        self.dim = len(bounds)
        self.population = self._init_population()
        self.best = None
        self.best_score = float('inf')
    
    def _init_population(self) -> np.ndarray:
        pop = np.zeros((self.pop_size, self.dim))
        for i in range(self.dim):
            pop[:, i] = np.random.uniform(self.bounds[i][0], self.bounds[i][1], self.pop_size)
        return pop
    
    def optimize(self) -> Tuple[np.ndarray, float]:
        for _ in range(self.max_iter):
            for i in range(self.pop_size):
                candidates = [x for x in range(self.pop_size) if x != i]
                a, b, c = np.random.choice(candidates, 3, replace=False)
                
                mutant = self.population[a] + self.F * (self.population[b] - self.population[c])
                mutant = np.clip(mutant, [b[0] for b in self.bounds], [b[1] for b in self.bounds])
                
                trial = np.copy(self.population[i])
                j_rand = np.random.randint(self.dim)
                for j in range(self.dim):
                    if np.random.rand() < self.CR or j == j_rand:
                        trial[j] = mutant[j]
                
                score = self.objective(trial)
                if score < self.objective(self.population[i]):
                    self.population[i] = trial
                    if score < self.best_score:
                        self.best_score = score
                        self.best = trial
        return self.best, self.best_score

def de_adaptive(objective, bounds, max_iter=500):
    F = 0.5 + 0.5 * np.random.rand()
    CR = 0.9
    for gen in range(max_iter):
        if gen > 100 and np.random.rand() < 0.1:
            F = np.clip(F + 0.1 * np.random.randn(), 0.4, 1.0)
            CR = np.clip(CR + 0.1 * np.random.randn(), 0.1, 0.9)
    return DifferentialEvolution(objective, bounds, F=F, CR=CR, max_iter=max_iter).optimize()
```

### Prolog Constraint Logic

```prolog
% DE parameter constraints
valid_parameters(F, CR, PopulationSize) :-
    F >= 0.4, F =< 1.0,
    CR >= 0.0, CR =< 1.0,
    PopulationSize >= 4, PopulationSize =< 100.

% Convergence detection
converged_best(History, Tolerance) :-
    findall(Score, member(score(Score), History), Scores),
    max_list(Scores, Max),
    min_list(Scores, Min),
    abs(Max - Min) < Tolerance.

% Mutation validity
valid_mutation(Vector, Bounds, ValidVector) :-
    forall(member(V-Bound, Vector-Bounds),
           between(Bound.low, Bound.high, V)).
```

### Hy Adaptive DE

```hy
(defn adaptive-f [generation max-generations]
  "Adapt mutation factor over generations"
  (+ 0.4 (* 0.6 (/ generation max-generations))))

(defn jade-strategy [current-cr success-history]
  "JADE adaptive DE strategy"
  (let [c (mean (take 5 success-history))]
    (if (< c 0.1)
        (* current-cr 0.9)
        (+ current-cr (* 0.1 (- 1 c))))))
```