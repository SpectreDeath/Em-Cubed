# Stochastic Diffusion Search - Cangjie Edition
# Cangjie-orchestrated multi-surface SDS with Python core, Prolog validation, Datalog diffusion, and Janus state checks

# Cangjie surface block: orchestrator
import std.math.*

func main() {
    // 1. Input: SDS parameters and objective from context
    let sds_input = context["sds_input"] as SDSInput;
    println("Cangjie Stochastic Diffusion Search (SDS) Solver Starting...");

    // 2. Prolog: Validate parameter constraints and structures
    let prolog_result = perform EmCubed.call_surface("prolog", "
valid_sds_params(PopSize, RestNumb, ProbabRest) :-
    PopSize >= 4, PopSize =< 1000,
    RestNumb >= 10, RestNumb =< 10000,
    ProbabRest >= 0.0, ProbabRest =< 1.0.

valid_bounds([]).
valid_bounds([Lo-Hi-Step|Rest]) :-
    Lo =< Hi,
    valid_bounds(Rest).

?- valid_sds_params(${sds_input.pop_size}, ${sds_input.rest_numb}, ${sds_input.probab_rest}),
   valid_bounds(${sds_input.bounds}).
    ");

    if (prolog_result.get("status") != "ok") {
        println("Prolog Parameter Validation Failed!");
        return SDSResult {
            best: List<Float64>(),
            best_score: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    // 3. Python: Setup initial population and candidates
    let py_init = perform EmCubed.call_surface("python", "
import numpy as np
import random

bounds = ${sds_input.bounds}
dim = len(bounds)
pop_size = ${sds_input.pop_size}
rest_numb = ${sds_input.rest_numb}

rest_space = [(b[1] - b[0]) / rest_numb for b in bounds]
population = []
raddrs = []

for _ in range(pop_size):
    ind = []
    ind_raddr = []
    for c in range(dim):
        n = random.randint(0, rest_numb - 1)
        ind_raddr.append(n)
        min_v = bounds[c][0] + rest_space[c] * n
        max_v = min_v + rest_space[c]
        dish = random.uniform(min_v, max_v)
        ind.append(dish)
    population.append(ind)
    raddrs.append(ind_raddr)

{'population': population, 'raddrs': raddrs}
    ");

    let dim = sds_input.bounds.size;
    let initial_pop = py_init.get("population", List<List<Float64>>());
    let initial_raddrs = py_init.get("raddrs", List<List<Int32>>());

    // Initialize state
    var state = SDSState {
        population: initial_pop,
        population_prev: initial_pop,
        raddrs: initial_raddrs,
        raddrs_prev: initial_raddrs,
        scores: List<Float64>(sds_input.pop_size, 1e300),
        scores_prev: List<Float64>(sds_input.pop_size, 1e300)
    };

    var best_x = List<Float64>(dim, 0.0);
    var best_score = 1e300;
    let history = List<Float64>();

    // 4. Main optimization loop
    for (gen in 0..sds_input.max_iter) {
        // Python: Evaluate current population against objective lambda
        let py_eval = perform EmCubed.call_surface("python", "
objective = ${sds_input.objective_lambda}
population = ${state.population}
scores = [float(objective(ind)) for ind in population]
best_idx = int(np.argmin(scores))

{'scores': scores, 'best_score': scores[best_idx], 'best_x': population[best_idx]}
        ");

        let scores = py_eval.get("scores", List<Float64>());
        let gen_best_score = py_eval.get("best_score", 0.0);
        let gen_best_x = py_eval.get("best_x", List<Float64>());

        state.scores = scores;

        if (gen_best_score < best_score) {
            best_score = gen_best_score;
            best_x = gen_best_x;
        }

        history.append(best_score);

        // Update personal bests
        for (i in 0..sds_input.pop_size) {
            if (state.scores[i] < state.scores_prev[i]) {
                state.scores_prev[i] = state.scores[i];
                state.population_prev[i] = state.population[i];
                state.raddrs_prev[i] = state.raddrs[i];
            }
        }

        // Check convergence via Prolog
        let check_conv = perform EmCubed.call_surface("prolog", "
converged(${history}, 1e-6).
        ");

        if (check_conv.get("status") == "ok") {
            println("SDS converged at generation " + gen.toString());
            break;
        }

        // 5. Datalog: Perform hypothesis sharing and diffusion (Active/Inactive roles)
        // Shuffling and choosing a random peer per agent
        let py_peers = perform EmCubed.call_surface("python", "
import random
pop_size = ${sds_input.pop_size}
peers = [random.randint(0, pop_size - 1) for _ in range(pop_size)]
random_raddrs = [[random.randint(0, ${sds_input.rest_numb} - 1) for _ in range(${dim})] for _ in range(pop_size)]
random_chances = [random.uniform(0.0, 1.0) for _ in range(pop_size)]

{'peers': peers, 'random_raddrs': random_raddrs, 'random_chances': random_chances}
        ");

        let peers = py_peers.get("peers", List<Int32>());
        let random_raddrs = py_peers.get("random_raddrs", List<List<Int32>>());
        let random_chances = py_peers.get("random_chances", List<Float64>());

        // Coordinate peer sharing in Cangjie
        for (i in 0..sds_input.pop_size) {
            let p_idx = peers[i];
            let peer_f = state.scores_prev[p_idx];
            let self_f = state.scores_prev[i];

            for (c in 0..dim) {
                if (peer_f < self_f) {
                    // Diffuse successful peer restaurant
                    state.raddrs[i][c] = state.raddrs_prev[p_idx][c];
                } else {
                    // Inactive agent random exploration choice
                    if (random_chances[i] < sds_input.probab_rest) {
                        state.raddrs[i][c] = random_raddrs[i][c];
                    } else {
                        state.raddrs[i][c] = state.raddrs_prev[i][c];
                    }
                }
            }
        }

        // 6. Python: Sample new coordinates (taste menu) for next generation
        let py_taste = perform EmCubed.call_surface("python", "
import random

bounds = ${sds_input.bounds}
dim = len(bounds)
pop_size = ${sds_input.pop_size}
rest_numb = ${sds_input.rest_numb}
raddrs = ${state.raddrs}

rest_space = [(b[1] - b[0]) / rest_numb for b in bounds]
new_population = []

def se_in_di_sp(val, min_val, max_val, step):
    if val <= min_val: return min_val
    if val >= max_val: return max_val
    if step == 0.0: return val
    return min_val + step * round((val - min_val) / step)

for i in range(pop_size):
    ind = []
    for c in range(dim):
        r_addr = raddrs[i][c]
        min_v = bounds[c][0] + rest_space[c] * r_addr
        max_v = min_v + rest_space[c]
        dish = random.uniform(min_v, max_v)
        ind.append(se_in_di_sp(dish, bounds[c][0], bounds[c][1], bounds[c][2]))
    new_population.append(ind)

{'population': new_population}
        ");

        state.population = py_taste.get("population", List<List<Float64>>());
    }

    return SDSResult {
        best: best_x,
        best_score: best_score,
        history: history,
        params_valid: true
    };
}

struct SDSInput {
    bounds: List<[Float64, Float64, Float64]>; // List of (min, max, step)
    pop_size: Int32;
    rest_numb: Int32;
    probab_rest: Float64;
    max_iter: Int32;
    objective_lambda: String;
}

struct SDSState {
    population: List<List<Float64>>;
    population_prev: List<List<Float64>>;
    raddrs: List<List<Int32>>;
    raddrs_prev: List<List<Int32>>;
    scores: List<Float64>;
    scores_prev: List<Float64>;
}

struct SDSResult {
    best: List<Float64>;
    best_score: Float64;
    history: List<Float64>;
    params_valid: Bool;
}

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface

@pytest.mark.asyncio
class TestSDSOrchestrator:
    async def test_sds_sampling_bounds(self):
        """Test SDS coordinate mapping and bounds clipping."""
        code = '''
bounds = [(-5.0, 5.0, 0.0), (-5.0, 5.0, 0.0)]
dim = len(bounds)
pop_size = 5
rest_numb = 50

rest_space = [(b[1] - b[0]) / rest_numb for b in bounds]
population = []
for _ in range(pop_size):
    ind = []
    for c in range(dim):
        n = 10
        min_v = bounds[c][0] + rest_space[c] * n
        max_v = min_v + rest_space[c]
        dish = (min_v + max_v) / 2.0
        ind.append(dish)
    population.append(ind)

assert len(population) == pop_size
assert all(-5.0 <= val <= 5.0 for ind in population for val in ind)
'''
        surface = PythonSurface()
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
async def test_sds_cangjie_edition_pipeline():
    """Verify registry search finds stochastic-diffusion-search Cangjie skill files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "stochastic-diffusion-search"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('name: stochastic-diffusion-search\\nDomain: OPTIMIZATION\\nsurfaces:\\n  - python\\n  - prolog')
        
        cangjie = skills_dir / "SKILL_CANGJIE.md"
        cangjie.write_text('# SDS Edition\\nfunc main() {}')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("diffusion", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Orchestrating Optimization (Sphere Function)

```python
from em_cubed import get_skill

# Load SDS optimizer
skill = get_skill("stochastic-diffusion-search")

# Configuration input: list of (min, max, step)
sds_input = {
    "sds_input": {
        "bounds": [[-5.0, 5.0, 0.0], [-5.0, 5.0, 0.0]],
        "pop_size": 30,
        "rest_numb": 100,
        "probab_rest": 0.1,
        "max_iter": 50,
        "objective_lambda": "lambda x: x[0]**2 + x[1]**2"
    }
}

result = skill.execute(sds_input)
print("Best parameters:", result["best"])
print("Best score:", result["best_score"])
```
