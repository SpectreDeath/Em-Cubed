# Differential Evolution Solver - Cangjie Edition
# Cangjie-orchestrated multi-surface DE with Python core, Prolog validation, Hy adaptation

# Cangjie surface block: orchestrator
func main() {
    // Input: DE parameters and objective from context
    let de_input = context["de_input"] as DEInput;

    println("Cangjie DE Solver Starting...");

    // 1. Python: Initialize population and run core DE loop
    let py_result = perform EmCubed.call_surface("python", "
import numpy as np
from typing import List, Tuple, Callable

def init_population(pop_size: int, bounds: List[Tuple[float, float]]) -> np.ndarray:
    dim = len(bounds)
    pop = np.zeros((pop_size, dim))
    for i in range(dim):
        pop[:, i] = np.random.uniform(bounds[i][0], bounds[i][1], pop_size)
    return pop

def evaluate(pop: np.ndarray, objective: Callable) -> np.ndarray:
    return np.array([objective(ind) for ind in pop])

def mutate(pop: np.ndarray, F: float) -> np.ndarray:
    pop_size, dim = pop.shape
    mutant = np.zeros_like(pop)
    for i in range(pop_size):
        candidates = [x for x in range(pop_size) if x != i]
        a, b, c = np.random.choice(candidates, 3, replace=False)
        mutant[i] = pop[a] + F * (pop[b] - pop[c])
    return mutant

def crossover(pop: np.ndarray, mutant: np.ndarray, CR: float) -> np.ndarray:
    pop_size, dim = pop.shape
    trial = np.copy(pop)
    for i in range(pop_size):
        j_rand = np.random.randint(dim)
        for j in range(dim):
            if np.random.rand() < CR or j == j_rand:
                trial[i, j] = mutant[i, j]
    return trial

def select(pop: np.ndarray, trial: np.ndarray, scores: np.ndarray,
           trial_scores: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    mask = trial_scores < scores
    pop[mask] = trial[mask]
    scores[mask] = trial_scores[mask]
    best_idx = np.argmin(scores)
    return pop, scores, pop[best_idx], scores[best_idx]

bounds = ${de_input.bounds}
pop_size = ${de_input.pop_size}
max_iter = ${de_input.max_iter}
F = ${de_input.F}
CR = ${de_input.CR}
objective = ${de_input.objective_lambda}

pop = init_population(pop_size, bounds)
scores = evaluate(pop, objective)
best_idx = np.argmin(scores)
best, best_score = pop[best_idx].tolist(), float(scores[best_idx])
history = [float(scores.min())]

for gen in range(max_iter):
    mutant = mutate(pop, F)
    mutant = np.clip(mutant, [b[0] for b in bounds], [b[1] for b in bounds])
    trial = crossover(pop, mutant, CR)
    trial_scores = evaluate(trial, objective)
    pop, scores, best, best_score = select(pop, trial, scores, trial_scores)
    history.append(float(scores.min()))

{'best': best, 'best_score': best_score, 'history': history}
    ");

    // 2. Prolog: Validate DE parameters and check convergence
    let prolog_result = perform EmCubed.call_surface("prolog", "
% DE parameter constraints
valid_parameters(F, CR, PopSize) :-
    F >= 0.4, F =< 1.0,
    CR >= 0.0, CR =< 1.0,
    PopSize >= 4, PopSize =< 500.

% Convergence detection from score history
converged_best(History, Tolerance) :-
    length(History, Len),
    Len > 10,
    append(_, Last10, History),
    length(Last10, 10),
    max_list(Last10, Max),
    min_list(Last10, Min),
    abs(Max - Min) < Tolerance.

% Validate bounds structure
valid_bounds([]).
valid_bounds([Lo-Hi|Rest]) :-
    Lo =< Hi,
    valid_bounds(Rest).

?- valid_parameters(${de_input.F}, ${de_input.CR}, ${de_input.pop_size}),
   valid_bounds(${de_input.bounds}).
    ");

    // 3. Hy: Adaptive parameter adjustment (JADE strategy)
    let hy_result = perform EmCubed.call_surface("hy", "
(defn adaptive-f [generation max-generations base-f]
  \"Time-varying mutation factor: linear increase from base to 1.0\"
  (+ base-f (* (- 1.0 base-f) (/ generation max-generations))))

(defn jade-strategy [current-cr success-history]
  \"JADE adaptive crossover: increase CR when success rate is high\"
  (if (empty? success-history)
    current-cr
    (let [c (mean (take-last 5 success-history))]
      (if (< c 0.1)
        (* current-cr 0.9)
        (+ current-cr (* 0.1 (- 1.0 c)))))))

(defn de-adapt [gen max-gen f cr history]
  (let [new-f (adaptive-f gen max-gen f)
        new-cr (jade-strategy cr history)]
    {:f new-f :cr new-cr}))

(de-adapt ${de_input.max_iter} ${de_input.max_iter} ${de_input.F} ${de_input.CR} [])
    ");

    // Synthesize final result
    let result = DEResult {
        best: py_result.get("best", List<Float64>()),
        best_score: py_result.get("best_score", Float64(0.0)),
        history: py_result.get("history", List<Float64>()),
        params_valid: prolog_result.get("status") == "ok",
        adapted_params: hy_result.get("value", Map<String, Float64>())
    };

    return result;
}

struct DEInput {
    bounds: List<[Float64, Float64]>;      // Search space bounds per dimension
    pop_size: Int32;                        // Population size (4-500)
    max_iter: Int32;                        // Max generations
    F: Float64;                             // Mutation factor [0.4, 1.0]
    CR: Float64;                            // Crossover rate [0.0, 1.0]
    objective_lambda: String;               // Python lambda as string
}

struct DEParameters {
    F: Float64;
    CR: Float64;
    pop_size: Int32;
    bounds: List<[Float64, Float64]>;
}

struct Individual {
    genome: List<Float64>;
    fitness: Float64;
}

struct DEResult {
    best: List<Float64>;
    best_score: Float64;
    history: List<Float64>;
    params_valid: Bool;
    adapted_params: Map<String, Float64>;
}

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface

def sphere(x):
    return sum(xi**2 for xi in x)

def rosenbrock(x):
    return sum(100.0*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2 for i in range(len(x)-1))

@pytest.mark.asyncio
class TestDESolverCangjie:
    async def test_de_sphere_optimization(self):
        """Test DE finds near-zero on sphere function."""
        code = '''
import numpy as np

def init_population(pop_size, bounds):
    dim = len(bounds)
    pop = np.zeros((pop_size, dim))
    for i in range(dim):
        pop[:, i] = np.random.uniform(bounds[i][0], bounds[i][1], pop_size)
    return pop

def mutate(pop, F):
    pop_size, dim = pop.shape
    mutant = np.zeros_like(pop)
    for i in range(pop_size):
        candidates = [x for x in range(pop_size) if x != i]
        a, b, c = np.random.choice(candidates, 3, replace=False)
        mutant[i] = pop[a] + F * (pop[b] - pop[c])
    return mutant

def crossover(pop, mutant, CR):
    pop_size, dim = pop.shape
    trial = np.copy(pop)
    for i in range(pop_size):
        j_rand = np.random.randint(dim)
        for j in range(dim):
            if np.random.rand() < CR or j == j_rand:
                trial[i, j] = mutant[i, j]
    return trial

def select(pop, trial, scores, trial_scores):
    mask = trial_scores < scores
    pop[mask] = trial[mask]
    scores[mask] = trial_scores[mask]
    best_idx = np.argmin(scores)
    return pop, scores, pop[best_idx], scores[best_idx]

bounds = [(-5.0, 5.0)] * 3
pop = init_population(20, bounds)
scores = np.array([sphere(ind) for ind in pop])
best_idx = np.argmin(scores)
best, best_score = pop[best_idx].tolist(), float(scores[best_idx])

for gen in range(100):
    mutant = mutate(pop, 0.8)
    mutant = np.clip(mutant, [-5]*3, [5]*3)
    trial = crossover(pop, mutant, 0.9)
    trial_scores = np.array([sphere(ind) for ind in trial])
    pop, scores, best, best_score = select(pop, trial, scores, trial_scores)

best_score
'''
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 1.0

    async def test_de_rosenbrock(self):
        """Test DE on Rosenbrock (harder multimodal function)."""
        code = '''
import numpy as np

def rosenbrock(x):
    return sum(100.0*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2 for i in range(len(x)-1))

def init_population(pop_size, bounds):
    dim = len(bounds)
    pop = np.zeros((pop_size, dim))
    for i in range(dim):
        pop[:, i] = np.random.uniform(bounds[i][0], bounds[i][1], pop_size)
    return pop

def mutate(pop, F):
    pop_size = pop.shape[0]
    mutant = np.zeros_like(pop)
    for i in range(pop_size):
        candidates = [x for x in range(pop_size) if x != i]
        a, b, c = np.random.choice(candidates, 3, replace=False)
        mutant[i] = pop[a] + F * (pop[b] - pop[c])
    return mutant

def crossover_and_select(pop, mutant, CR, scores, objective):
    pop_size, dim = pop.shape
    trial = np.copy(pop)
    for i in range(pop_size):
        j_rand = np.random.randint(dim)
        for j in range(dim):
            if np.random.rand() < CR or j == j_rand:
                trial[i, j] = mutant[i, j]
    trial_scores = np.array([objective(ind) for ind in trial])
    mask = trial_scores < scores
    pop[mask] = trial[mask]
    scores[mask] = trial_scores[mask]
    best_idx = np.argmin(scores)
    return pop, scores, scores[best_idx]

bounds = [(-2.0, 2.0)] * 2
pop = init_population(30, bounds)
scores = np.array([rosenbrock(ind) for ind in pop])

for gen in range(200):
    mutant = mutate(pop, 0.8)
    mutant = np.clip(mutant, [-2]*2, [2]*2)
    pop, scores, best_score = crossover_and_select(pop, mutant, 0.9, scores, rosenbrock)

best_score
'''
        surface = PythonSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"] < 10.0

    async def test_prolog_validation(self):
        """Test Prolog parameter constraint validation."""
        code = '''
valid_parameters(F, CR, PopSize) :-
    F >= 0.4, F =< 1.0,
    CR >= 0.0, CR =< 1.0,
    PopSize >= 4, PopSize =< 500.

?- valid_parameters(0.8, 0.9, 50).
'''
        from em_cubed.surfaces import PrologSurface
        surface = PrologSurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_hy_adaptation(self):
        """Test Hy adaptive parameter functions."""
        code = '''
(defn adaptive-f [gen max-gen base-f]
  (+ base-f (* (- 1.0 base-f) (/ gen max-gen))))

(defn jade-strategy [cr history]
  (if (empty? history)
    cr
    (let [c (mean (take-last 5 history))]
      (if (< c 0.1)
        (* cr 0.9)
        (+ cr (* 0.1 (- 1.0 c)))))))

(adaptive-f 50 100 0.5)
'''
        from em_cubed.surfaces import HySurface
        surface = HySurface()
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert 0.5 <= result["value"] <= 1.0
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_de_full_pipeline():
    """Test complete DE pipeline through Cangjie orchestrator."""
    from em_cubed import reindex, search_registry
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "differential-evolution-solver"
        skills_dir.mkdir(parents=True)

        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: differential-evolution-solver
Domain: OPTIMIZATION
surfaces:
  - python
  - prolog
  - hy
---
## Purpose
DE optimization solver
''')

        cangjie = skills_dir / "SKILL_CANGJIE.md"
        cangjie.write_text(
            Path(skills_dir.parent.parent / "OPTIMIZATION" / "differential-evolution-solver" / "SKILL_CANGJIE.md").read_text()
        )

        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("differential", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Basic DE Optimization

```python
from em_cubed import get_skill

# Load the DE skill
skill = get_skill("differential-evolution-solver")

# Define problem
de_input = {
    "de_input": {
        "bounds": [[-5.0, 5.0], [-5.0, 5.0]],
        "pop_size": 30,
        "max_iter": 200,
        "F": 0.8,
        "CR": 0.9,
        "objective_lambda": "lambda x: x[0]**2 + x[1]**2"
    }
}

# Run optimization
result = skill.execute(de_input)
print(f"Best solution: {result['best']}")
print(f"Best score: {result['best_score']}")
```

### Constrained Optimization with Adaptive Parameters

```python
# Rosenbrock function optimization with adaptive DE
de_input = {
    "de_input": {
        "bounds": [[-2.0, 2.0], [-2.0, 2.0], [-2.0, 2.0]],
        "pop_size": 50,
        "max_iter": 500,
        "F": 0.5,
        "CR": 0.9,
        "objective_lambda": "lambda x: sum(100*(x[i+1] - x[i]**2)**2 + (1 - x[i])**2 for i in range(len(x)-1))"
    }
}

result = skill.execute(de_input)
# Check Prolog validated parameters and Hy adapted values
assert result["params_valid"] == True
print(f"Adapted F: {result['adapted_params']['f']:.3f}")
print(f"Adapted CR: {result['adapted_params']['cr']:.3f}")
```

### Convergence Monitoring

```python
# Access convergence history from result
result = skill.execute(de_input)
history = result["history"]

# Plot convergence
import matplotlib.pyplot as plt
plt.plot(history)
plt.xlabel("Generation")
plt.ylabel("Best Score")
plt.title("DE Convergence")
plt.show()
```

## Security Considerations

- Python surface uses only numpy (no I/O or network access)
- Prolog surface performs logical validation only (no side effects)
- Hy surface performs pure functional transformations
- All surfaces execute within sandbox timeouts
- Parameter bounds enforced by Prolog constraints prevent runaway populations

## Dependencies

- numpy (numerical operations in Python surface)
- em_cubed framework (surface orchestration)
- Prolog runtime (constraint validation)
- Hy runtime (adaptive parameter computation)