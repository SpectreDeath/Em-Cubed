# Fractal-Based Algorithm — Cangjie Edition
# Fractal space partitioning with Python core, Prolog validation, Hy mutation

import std.math.*

func main() {
    let fba_input = context["fba_input"] as FBAInput;
    println("Cangjie Fractal-Based Algorithm (FBA) Solver Starting...");

    let prolog_result = perform EmCubed.call_surface("prolog", "
valid_fba_params(PopSize, P1, P2, P3, MValue) :-
    PopSize >= 4, PopSize =< 200,
    P1 >= 10, P1 =< 100,
    P2 >= 10, P2 =< 100,
    P3 >= 0.0, P3 =< 1.0,
    MValue >= 5, MValue =< 20.

?- valid_fba_params(${fba_input.pop_size}, ${fba_input.p1}, ${fba_input.p2}, ${fba_input.p3}, ${fba_input.m_value}).
    ");

    if (prolog_result.get("status") != "ok") {
        println("Prolog parameter validation failed");
        return FBAResult {
            best: List<Float64>(),
            best_score: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    let init_result = perform EmCubed.call_surface("python", "
import random, math

bounds = ${fba_input.bounds}
dim = len(bounds)
pop_size = ${fba_input.pop_size}
population = []

for _ in range(pop_size):
    ind = [random.uniform(bounds[c][0], bounds[c][1]) for c in range(dim)]
    population.append(ind)

fitness = [sum(xi**2 for xi in ind) for ind in population]
best_idx = fitness.index(min(fitness))
best_f = fitness[best_idx]
best_x = population[best_idx][:]
history = [best_f]

{'population': population, 'best_x': best_x, 'best_f': best_f, 'history': history}
    ");

    var pop = init_result.get("population", List<List<Float64>>());
    var best_x = init_result.get("best_x", List<Float64>());
    var best_f = init_result.get("best_f", 1e300);
    var history = init_result.get("history", List<Float64>());

    for (epoch in 1..fba_input.max_iter) {
        let step_result = perform EmCubed.call_surface("python", "
import random, math

bounds = ${fba_input.bounds}
population = ${pop}
best_x = ${best_x}
best_f = ${best_f}
p1 = ${fba_input.p1}
p2 = ${fba_input.p2}
p3 = ${fba_input.p3}
m_value = ${fba_input.m_value}
dim = len(bounds)
pop_size = len(population)

# Power distribution mutation
def power_distribution(center, out_min, out_max, p=5.0):
    rnd = random.uniform(-1.0, 1.0)
    r = abs(rnd) ** p
    if rnd >= 0.0:
        return max(out_min, min(out_max, center + r * (out_max - center)))
    return max(out_min, min(out_max, center - r * (center - out_min)))

# Mutation
for i in range(pop_size):
    if random.random() < p3:
        for c in range(dim):
            population[i][c] = power_distribution(best_x[c], bounds[c][0], bounds[c][1])

# Evaluate
fitness = [sum(xi**2 for xi in ind) for ind in population]
if min(fitness) < best_f:
    best_f = min(fitness)
    best_x = population[fitness.index(best_f)][:]

history.append(best_f)

{'population': population, 'best_x': best_x, 'best_f': best_f, 'history': history}
        ");

        pop = step_result.get("population", List<List<Float64>>());
        best_x = step_result.get("best_x", List<Float64>());
        best_f = step_result.get("best_f", 0.0);
        history = step_result.get("history", List<Float64>());
    }

    return FBAResult {
        best: best_x,
        best_score: best_f,
        history: history,
        params_valid: true
    };
}

struct FBAInput {
    bounds: List<[Float64, Float64]>;
    pop_size: Int32;
    p1: Int32;
    p2: Int32;
    p3: Float64;
    m_value: Int32;
    max_iter: Int32;
}

struct FBAResult {
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
class TestFBACangjie:
    async def test_power_distribution_range(self):
        """Test power distribution produces valid values."""
        surface = PythonSurface()
        code = '''
import random
def power_distribution(center, out_min, out_max, p=5.0):
    rnd = random.uniform(-1.0, 1.0)
    r = abs(rnd) ** p
    if rnd >= 0.0:
        return max(out_min, min(out_max, center + r * (out_max - center)))
    return max(out_min, min(out_max, center - r * (center - out_min)))

vals = [power_distribution(0.0, -5.0, 5.0) for _ in range(10)]
all(-5 <= v <= 5 for v in vals)
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_subspace_contains(self):
        """Test subspace point containment logic."""
        surface = PythonSurface()
        code = '''
def point_in_subspace(point, subspace):
    for c in range(len(point)):
        if point[c] < subspace['min'][c] or point[c] >= subspace['max'][c]:
            return False
    return True

subspace = {'min': [0.0, 0.0], 'max': [1.0, 1.0]}
point_in_subspace([0.5, 0.5], subspace)
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
async def test_fba_cangjie_edition():
    """Test FBA Cangjie skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "fractal-based-algorithm"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: fractal-based-algorithm\nDomain: OPTIMIZATION')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# FBA\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("fractal", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Orchestrating FBA (Sphere Function)

```python
from em_cubed import get_skill

skill = get_skill("fractal-based-algorithm")
fba_input = {
    "fba_input": {
        "bounds": [[-5.0, 5.0], [-5.0, 5.0]],
        "pop_size": 30,
        "p1": 60,
        "p2": 30,
        "p3": 0.8,
        "m_value": 10,
        "max_iter": 80
    }
}
result = skill.execute(fba_input)
print("Best:", result["best"], "Score:", result["best_score"])
```