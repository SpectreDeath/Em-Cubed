# Dialectic Search — Cangjie Edition
# Philosophical optimization with Python core, Prolog validation, Hy synthesis

import std.math.*

func main() {
    let da_input = context["da_input"] as DAInput;
    println("Cangjie Dialectic Search (DA) Solver Starting...");

    let prolog_result = perform EmCubed.call_surface("prolog", "
valid_da_params(PopSize, K1, K2) :-
    PopSize >= 4, PopSize =< 200,
    K1 >= 1, K1 =< 10,
    K2 >= 5, K2 =< 50.

?- valid_da_params(${da_input.pop_size}, ${da_input.k1}, ${da_input.k2}).
    ");

    if (prolog_result.get("status") != "ok") {
        println("Prolog parameter validation failed");
        return DAResult {
            best: List<Float64>(),
            best_score: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    let init_result = perform EmCubed.call_surface("python", "
import numpy as np, random
bounds = ${da_input.bounds}
dim = len(bounds)
pop_size = ${da_input.pop_size}
population = []
for _ in range(pop_size):
    ind = [random.uniform(bounds[c][0], bounds[c][1]) for c in range(dim)]
    population.append(ind)
{'population': population}
    ");

    let pop = init_result.get("population", List<List<Float64>>());
    let dim = da_input.bounds.size;
    var best_x = List<Float64>(dim, 0.0);
    var best_score = 1e300;
    let history = List<Float64>();

    for (gen in 0..da_input.max_iter) {
        let eval_result = perform EmCubed.call_surface("python", "
import numpy as np, random
objective = ${da_input.objective_lambda}
population = ${pop}
pop_size = ${da_input.pop_size}
k1 = ${da_input.k1}
k2 = ${da_input.k2}
dim = len(population[0]) if population else 2

def euclidean_distance(a, b):
    return np.sqrt(sum((ai - bi)**2 for ai, bi in zip(a, b)))

def clip(val, lo, hi):
    return max(lo, min(hi, val))

# Evaluate fitness
fitness = [float(objective(ind)) for ind in population]
# Sort descending by fitness
sorted_idx = sorted(range(len(fitness)), key=lambda i: fitness[i])
population = [population[i] for i in sorted_idx]
fitness = [fitness[i] for i in sorted_idx]

# Best thinker moves toward second best
for c in range(dim):
    population[0][c] = clip(population[0][c] + random.random() * (population[1][c] - population[0][c]), bounds[c][0], bounds[c][1])

# Practical thinkers move toward nearest speculative thinker
for i in range(k1, pop_size):
    anti1 = random.randint(0, k1 - 1)
    anti2 = random.randint(0, k1 - 1)
    while anti1 == anti2:
        anti2 = random.randint(0, k1 - 1)
    dist1 = euclidean_distance(population[i], population[anti1])
    dist2 = euclidean_distance(population[i], population[anti2])
    anti_idx = anti1 if dist1 < dist2 else anti2
    for c in range(dim):
        population[i][c] = clip(population[i][c] + random.random() * (population[anti_idx][c] - population[i][c]), bounds[c][0], bounds[c][1])

best_score = min(fitness)
best_idx = fitness.index(best_score)
best_x = population[best_idx][:]
{'population': population, 'best_score': best_score, 'best_x': best_x}
        ");

        pop = eval_result.get("population", List<List<Float64>>());
        let gen_best = eval_result.get("best_score", 0.0);
        let gen_best_x = eval_result.get("best_x", List<Float64>());

        if (gen_best < best_score) {
            best_score = gen_best;
            best_x = gen_best_x;
        }
        history.append(best_score);
    }

    return DAResult {
        best: best_x,
        best_score: best_score,
        history: history,
        params_valid: true
    };
}

struct DAInput {
    bounds: List<[Float64, Float64]>;
    pop_size: Int32;
    k1: Int32;
    k2: Int32;
    max_iter: Int32;
    objective_lambda: String;
}

struct DAResult {
    best: List<Float64>;
    best_score: Float64;
    history: List<Float64>;
    params_valid: Bool;
}

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface

@pytest.mark.asyncio
class TestDACangjie:
    async def test_da_euclidean_distance(self):
        """Test Euclidean distance computation."""
        surface = PythonSurface()
        code = '''
import numpy as np
def euclidean_distance(a, b):
    return np.sqrt(sum((ai - bi)**2 for ai, bi in zip(a, b)))
euclidean_distance([0.0, 0.0], [3.0, 4.0])
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert abs(result["value"] - 5.0) < 1e-9

    async def test_da_convergence_check(self):
        """Test convergence detection."""
        surface = PythonSurface()
        code = '''
history = [0.5, 0.4, 0.35, 0.33, 0.32, 0.315, 0.312, 0.311, 0.3105, 0.3102]
max_h = max(history); min_h = min(history)
abs(max_h - min_h) < 0.001
'''
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
async def test_da_cangjie_edition():
    """Test DA Cangjie skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "dialectic-search"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: dialectic-search\nDomain: OPTIMIZATION')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# DA\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("dialectic", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Orchestrating DA (Sphere Function)

```python
from em_cubed import get_skill

skill = get_skill("dialectic-search")
da_input = {
    "da_input": {
        "bounds": [[-5.0, 5.0], [-5.0, 5.0]],
        "pop_size": 30,
        "k1": 3,
        "k2": 10,
        "max_iter": 80,
        "objective_lambda": "lambda x: x[0]**2 + x[1]**2"
    }
}
result = skill.execute(da_input)
print("Best:", result["best"], "Score:", result["best_score"])
```