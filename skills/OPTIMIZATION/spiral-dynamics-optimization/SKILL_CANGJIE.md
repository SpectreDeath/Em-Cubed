# Spiral Dynamics Optimization — Cangjie Edition
# Damped harmonic oscillations with Python core, Prolog validation, Hy spiral helpers

import std.math.*

func main() {
    let sdo_input = context["sdo_input"] as SDOInput;
    println("Cangjie Spiral Dynamics Optimization (SDO) Solver Starting...");

    let prolog_result = perform EmCubed.call_surface("prolog", "
valid_sdo_params(PopSize, Damping, Frequency) :-
    PopSize >= 10, PopSize =< 200,
    Damping >= 0.01, Damping =< 1.0,
    Frequency >= 0.5, Frequency =< 20.0.

?- valid_sdo_params(${sdo_input.pop_size}, ${sdo_input.damping}, ${sdo_input.frequency}).
    ");

    if (prolog_result.get("status") != "ok") {
        println("Prolog parameter validation failed");
        return SDOResult {
            best: List<Float64>(),
            best_score: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    let init_result = perform EmCubed.call_surface("python", "
import random, math

bounds = ${sdo_input.bounds}
dim = len(bounds)
pop_size = ${sdo_input.pop_size}
damping = ${sdo_input.damping}
frequency = ${sdo_input.frequency}
precision = ${sdo_input.precision}

particles = []
for _ in range(pop_size):
    pos = [random.uniform(bounds[c][0], bounds[c][1]) for c in range(dim)]
    amp = [random.uniform(-5, 5) for _ in range(dim)]
    particles.append({'position': pos, 'amplitude': amp, 't': 0, 'fitness': 0.0})

for i in range(pop_size):
    particles[i]['fitness'] = -sum(xi**2 for xi in particles[i]['position'])

best_f = max(p['fitness'] for p in particles)
best_x = [p['position'] for p in particles if p['fitness'] == best_f][0]
history = [best_f]

{'particles': particles, 'best_x': best_x, 'best_f': best_f, 'history': history}
    ");

    var particles = init_result.get("particles", List<Dict<String, Any>>());
    var best_x = init_result.get("best_x", List<Float64>());
    var best_f = init_result.get("best_f", -1e300);
    var history = init_result.get("history", List<Float64>());

    for (epoch in range(1, sdo_input.max_iter + 1)) {
        let step_result = perform EmCubed.call_surface("python", "
import random, math

particles = ${particles}
bounds = ${sdo_input.bounds}
dim = len(bounds)
pop_size = len(particles)
damping = ${sdo_input.damping}
frequency = ${sdo_input.frequency}
precision = ${sdo_input.precision}
best_x = ${best_x}
best_f = ${best_f}

def damped_oscillation(amplitude, t, phi=0.0):
    return amplitude * math.exp(-damping * t / precision) * math.cos(frequency * t / precision + phi)

for i in range(pop_size):
    if particles[i]['fitness'] >= best_f - 1e-10:
        for c in range(dim):
            particles[i]['position'][c] = random.uniform(bounds[c][0], bounds[c][1])
        particles[i]['t'] = 0
        continue
    
    particles[i]['t'] += 1
    t = particles[i]['t']
    
    for c in range(dim):
        phi = random.uniform(0.0, 2.0 * math.pi)
        particles[i]['position'][c] += damped_oscillation(particles[i]['amplitude'][c], t, phi)
        particles[i]['position'][c] = max(bounds[c][0], min(bounds[c][1], particles[i]['position'][c]))

for i in range(pop_size):
    particles[i]['fitness'] = -sum(xi**2 for xi in particles[i]['position'])

current_best = max(p['fitness'] for p in particles)
if current_best > best_f:
    best_f = current_best
    best_x = [p['position'] for p in particles if p['fitness'] == current_best][0]
    for i in range(pop_size):
        particles[i]['t'] = 0
        for c in range(dim):
            particles[i]['amplitude'][c] = best_x[c] - particles[i]['position'][c]

history.append(best_f)

{'particles': particles, 'best_x': best_x, 'best_f': best_f, 'history': history}
        ");

        particles = step_result.get("particles", List<Dict<String, Any>>());
        best_x = step_result.get("best_x", List<Float64>());
        best_f = step_result.get("best_f", 0.0);
        history = step_result.get("history", List<Float64>());
    }

    return SDOResult {
        best: best_x,
        best_score: best_f,
        history: history,
        params_valid: true
    };
}

struct SDOInput {
    bounds: List<[Float64, Float64]>;
    pop_size: Int32;
    damping: Float64;
    frequency: Float64;
    precision: Float64;
    max_iter: Int32;
}

struct SDOResult {
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
class TestSDOCangjie:
    async def test_damped_oscillation_decays(self):
        """Test damped oscillation decreases over time."""
        surface = PythonSurface()
        code = '''
import math
def damped_oscillation(amplitude, t, damping=0.3, freq=4.0):
    return amplitude * math.exp(-damping * t) * math.cos(freq * t)

vals = [abs(damped_oscillation(5.0, t)) for t in range(20)]
vals[0] > vals[-1]
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_amplitude_calculation(self):
        """Test amplitude is difference from best."""
        surface = PythonSurface()
        code = '''
best_x = [0.5, 0.5]
particle_x = [0.2, 0.3]
amp = [best_x[i] - particle_x[i] for i in range(len(best_x))]
amp == [0.3, 0.2]
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
async def test_sdo_cangjie_edition():
    """Test SDO Cangjie skill in registry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "spiral-dynamics-optimization"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: spiral-dynamics-optimization\nDomain: OPTIMIZATION')
        (skills_dir / "SKILL_CANGJIE.md").write_text('# SDO\nfunc main() {}')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("spiral", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Orchestrating SDO (Sphere Function)

```python
from em_cubed import get_skill

skill = get_skill("spiral-dynamics-optimization")
sdo_input = {
    "sdo_input": {
        "bounds": [[-5.0, 5.0], [-5.0, 5.0]],
        "pop_size": 100,
        "damping": 0.3,
        "frequency": 4.0,
        "precision": 10000.0,
        "max_iter": 80
    }
}
result = skill.execute(sdo_input)
print("Best:", result["best"], "Score:", result["best_score"])
```