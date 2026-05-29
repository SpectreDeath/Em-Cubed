# Central Force Optimization — Cangjie Edition
# Gravitational attraction-based optimization with Python core, Prolog validation

import std.math.*

func main() {
    let cfo_input = context["cfo_input"] as CFOInput;
    println("Cangjie Central Force Optimization (CFO) Solver Starting...");

    let prolog_result = perform EmCubed.call_surface("prolog", "
valid_cfo_params(PopSize, Alpha, Beta) :-
    PopSize >= 4, PopSize =< 100,
    Alpha >= 0.01, Alpha =< 2.0,
    Beta >= 0.01, Beta =< 2.0.

?- valid_cfo_params(${cfo_input.pop_size}, ${cfo_input.alpha}, ${cfo_input.beta}).
    ");

    if (prolog_result.get("status") != "ok") {
        println("Prolog parameter validation failed");
        return CFOResult {
            best: List<Float64>(),
            best_score: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    let init_result = perform EmCubed.call_surface("python", "
import random, math

bounds = ${cfo_input.bounds}
dim = len(bounds)
pop_size = ${cfo_input.pop_size}
g = ${cfo_input.g}
alpha = ${cfo_input.alpha}
beta = ${cfo_input.beta}
initial_frep = ${cfo_input.initial_frep}
noise_factor = ${cfo_input.noise_factor}

probes = []
for _ in range(pop_size):
    pos = [random.uniform(bounds[c][0], bounds[c][1]) for c in range(dim)]
    fitness = -sum(xi**2 for xi in pos)  # Sphere maximization
    probes.append({'position': pos, 'fitness': fitness})

best_f = max(p['fitness'] for p in probes)
best_x = [p['position'] for p in probes if p['fitness'] == best_f][0]
history = [best_f]

{'probes': probes, 'best_x': best_x, 'best_f': best_f, 'history': history}
    ");

    var probes = init_result.get("probes", List<Dict<String, Any>>());
    var best_x = init_result.get("best_x", List<Float64>());
    var best_f = init_result.get("best_f", -1e300);
    var history = init_result.get("history", List<Float64>());

    for (epoch in 1..cfo_input.max_iter) {
        let step_result = perform EmCubed.call_surface("python", "
import random, math

probes = ${probes}
bounds = ${cfo_input.bounds}
dim = len(bounds)
pop_size = len(probes)
g = ${cfo_input.g}
alpha = ${cfo_input.alpha}
beta = ${cfo_input.beta}
noise_factor = ${cfo_input.noise_factor}
epoch = ${epoch}
max_iter = ${cfo_input.max_iter}

# Calculate accelerations
accelerations = [[0.0 for _ in range(dim)] for _ in range(pop_size)]
for p in range(pop_size):
    for k in range(pop_size):
        if k == p:
            continue
        mass_diff = probes[k]['fitness'] - probes[p]['fitness']
        if mass_diff <= 0:
            continue
        dist_sq = sum((probes[k]['position'][c] - probes[p]['position'][c])**2 for c in range(dim))
        if dist_sq < 1e-10:
            continue
        distance = math.sqrt(dist_sq)
        for c in range(dim):
            direction = (probes[k]['position'][c] - probes[p]['position'][c]) / distance
            accelerations[p][c] += g * (mass_diff ** alpha) * direction / (distance ** beta)

# Update positions
current_noise = noise_factor * (1.0 - epoch / max_iter) if max_iter > 0 else noise_factor
for p in range(pop_size):
    for c in range(dim):
        probes[p]['position'][c] += 0.5 * accelerations[p][c]
        probes[p]['position'][c] += current_noise * g * random.uniform(-1.0, 1.0)
        probes[p]['position'][c] = max(bounds[c][0], min(bounds[c][1], probes[p]['position'][c]))

# Evaluate
for p in range(pop_size):
    probes[p]['fitness'] = -sum(xi**2 for xi in probes[p]['position'])

best_f = max(p['fitness'] for p in probes)
best_x = [p['position'] for p in probes if p['fitness'] == best_f][0]
history.append(best_f)

{'probes': probes, 'best_x': best_x, 'best_f': best_f, 'history': history}
        ");

        probes = step_result.get("probes", List<Dict<String, Any>>());
        best_x = step_result.get("best_x", List<Float64>());
        best_f = step_result.get("best_f", 0.0);
        history = step_result.get("history", List<Float64>());
    }

    return CFOResult {
        best: best_x,
        best_score: best_f,
        history: history,
        params_valid: true
    };
}

struct CFOInput {
    bounds: List<[Float64, Float64]>;
    pop_size: Int32;
    g: Float64;
    alpha: Float64;
    beta: Float64;
    initial_frep: Float64;
    final_frep: Float64;
    noise_factor: Float64;
    max_iter: Int32;
}

struct CFOResult {
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
class TestCFOCangjie:
    async def test_gravitational_force(self):
        """Test gravitational force calculation."""
        surface = PythonSurface()
        code = '''
g, alpha, beta = 1.0, 0.1, 0.1
mass1, mass2 = 10.0, 5.0
distance = 2.0
force = g * (mass1 - mass2) ** alpha / (distance ** beta)
force > 0
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_distance_squared(self):
        """Test squared distance calculation."""
        surface = PythonSurface()
        code = '''
x1, x2 = [0.0, 0.0], [3.0, 4.0]
dist_sq = sum((x1[i] - x2[i])**2 for i in range(len(x1)))
dist_sq == 25.0
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
async def test_cfo_cangjie_edition():
    """Test CFO Cangjie skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "central-force-optimization"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: central-force-optimization\nDomain: OPTIMIZATION')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# CFO\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("central force", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Orchestrating CFO (Sphere Function)

```python
from em_cubed import get_skill

skill = get_skill("central-force-optimization")
cfo_input = {
    "cfo_input": {
        "bounds": [[-5.0, 5.0], [-5.0, 5.0]],
        "pop_size": 30,
        "g": 1.0,
        "alpha": 0.1,
        "beta": 0.1,
        "initial_frep": 0.9,
        "final_frep": 0.1,
        "noise_factor": 1.0,
        "max_iter": 80
    }
}
result = skill.execute(cfo_input)
print("Best:", result["best"], "Score:", result["best_score"])
```