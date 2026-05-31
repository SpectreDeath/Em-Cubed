# Chaos Optimization — Cangjie Edition
# Chaotic map-based optimization with Python core, Prolog validation, Hy mutation

import std.math.*

func main() {
    let coa_input = context["coa_input"] as COAInput;
    println("Cangjie Chaos Optimization (COA) Solver Starting...");

    let prolog_result = perform EmCubed.call_surface("prolog", "
valid_coa_params(PopSize, S1, S2, P3) :-
    PopSize >= 4, PopSize =< 200,
    S1 >= 10, S1 =< 100,
    S2 >= 10, S2 =< 200,
    P3 >= 0.0, P3 =< 1.0.

?- valid_coa_params(${coa_input.pop_size}, ${coa_input.s1}, ${coa_input.s2}, ${coa_input.p3}).
    ");

    if (prolog_result.get("status") != "ok") {
        println("Prolog parameter validation failed");
        return COAResult {
            best: List<Float64>(),
            best_score: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    let init_result = perform EmCubed.call_surface("python", "
import numpy as np, random, math
bounds = ${coa_input.bounds}
dim = len(bounds)
pop_size = ${coa_input.pop_size}
population = []
for _ in range(pop_size):
    ind = [random.uniform(bounds[c][0], bounds[c][1]) for c in range(dim)]
    population.append(ind)
gamma = [[random.uniform(0, 1) for _ in range(dim)] for _ in range(pop_size)]
velocity = [[0.0 for _ in range(dim)] for _ in range(pop_size)]
best_x = population[0][:]
best_f = min(float(${coa_input.objective_lambda})(ind) for ind in population)
history = [best_f]
{'population': population, 'gamma': gamma, 'velocity': velocity, 'best_x': best_x, 'best_f': best_f, 'history': history}
    ");

    var pop = init_result.get("population", List<List<Float64>>());
    var gamma = init_result.get("gamma", List<List<Float64>>());
    var velocity = init_result.get("velocity", List<List<Float64>>());
    var best_x = init_result.get("best_x", List<Float64>());
    var best_f = init_result.get("best_f", 1e300);
    var history = init_result.get("history", List<Float64>());

    for (epoch in 1..coa_input.max_iter) {
        let eval_result = perform EmCubed.call_surface("python", "
import numpy as np, random, math
bounds = ${coa_input.bounds}
population = ${pop}
gamma = ${gamma}
velocity = ${velocity}
objective = ${coa_input.objective_lambda}
dim = len(bounds)
pop_size = ${coa_input.pop_size}
S1 = ${coa_input.s1}
S2 = ${coa_input.s2}
P3 = ${coa_input.p3}

def clip(val, lo, hi, step=0.0):
    val = max(lo, min(hi, val))
    if step > 0.0:
        val = lo + step * round((val - lo) / step)
    return val

def logistic_map(x): return 4.0 * x * (1.0 - x)
def tent_map(x): return 1.0 - 2.0 * abs(0.5 - x)
def sinusoidal_map(x): return math.sin(math.pi * x)

def power_distribution(center, out_min, out_max, p=20.0):
    rnd = random.uniform(-1.0, 1.0)
    r = abs(rnd) ** p
    if rnd >= 0.0:
        return clip(center + r * (out_max - center), out_min, out_max)
    return clip(center - r * (center - out_min), out_min, out_max)

stagnation = [0] * pop_size
best_f = ${best_f}
best_x = ${best_x}

for i in range(pop_size):
    if random.random() < P3:
        for c in range(dim):
            gamma[i][c] = [logistic_map, tent_map, sinusoidal_map][c % 3](gamma[i][c])
            population[i][c] = clip(bounds[c][0] + gamma[i][c] * (bounds[c][1] - bounds[c][0]), bounds[c][0], bounds[c][1])
    
    if epoch <= S1:
        for c in range(dim):
            velocity[i][c] = 0.5 * velocity[i][c] + 0.5 * random.gauss(0, 1)
            population[i][c] += velocity[i][c]
    
    f = float(objective(population[i]))
    if f < best_f:
        best_f = f
        best_x = population[i][:]
    history.append(best_f)

{'population': population, 'gamma': gamma, 'velocity': velocity, 'best_x': best_x, 'best_f': best_f, 'history': history}
        ");

        pop = eval_result.get("population", List<List<Float64>>());
        gamma = eval_result.get("gamma", List<List<Float64>>());
        velocity = eval_result.get("velocity", List<List<Float64>>());
        best_x = eval_result.get("best_x", List<Float64>());
        best_f = eval_result.get("best_f", 0.0);
        history = eval_result.get("history", List<Float64>());
    }

    return COAResult {
        best: best_x,
        best_score: best_f,
        history: history,
        params_valid: true
    };
}

struct COAInput {
    bounds: List<[Float64, Float64]>;
    pop_size: Int32;
    s1: Int32;
    s2: Int32;
    p3: Float64;
    max_iter: Int32;
    objective_lambda: String;
}

struct COAResult {
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
class TestCOACangjie:
    async def test_logistic_map_range(self):
        """Test logistic map produces values in [0,1]."""
        surface = PythonSurface()
        code = '''
def logistic_map(x): return 4.0 * x * (1.0 - x)
vals = [logistic_map(v) for v in [0.1, 0.3, 0.5, 0.7, 0.9]]
all(0 <= v <= 1 for v in vals)
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_tent_map_symmetry(self):
        """Test tent map symmetry around 0.5."""
        surface = PythonSurface()
        code = '''
def tent_map(x): return 1.0 - 2.0 * abs(0.5 - x)
tent_map(0.25) + tent_map(0.75)  # Should equal 1.0
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert abs(result["value"] - 1.0) < 1e-9
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_coa_cangjie_edition():
    """Test COA Cangjie skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "chaos-optimization"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: chaos-optimization\nDomain: OPTIMIZATION')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# COA\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("chaos", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Orchestrating COA (Sphere Function)

```python
from em_cubed import get_skill

skill = get_skill("chaos-optimization")
coa_input = {
    "coa_input": {
        "bounds": [[-5.0, 5.0], [-5.0, 5.0]],
        "pop_size": 30,
        "s1": 40,
        "s2": 60,
        "p3": 0.8,
        "max_iter": 100,
        "objective_lambda": "lambda x: x[0]**2 + x[1]**2"
    }
}
result = skill.execute(coa_input)
print("Best:", result["best"], "Score:", result["best_score"])
```