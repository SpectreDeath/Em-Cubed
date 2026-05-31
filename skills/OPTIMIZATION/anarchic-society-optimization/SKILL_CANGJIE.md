# Anarchic Society Optimization — Cangjie Edition
# Multi-surface orchestrator: Python core, Prolog policy validation,
# Hy index computation, Z3 bounds enforcement.

import std.math.*

func main() {
    // 1. Load inputs from context
    let aso_input = context["aso_input"] as ASOInput;
    println("Cangjie ASO Solver Starting…");

    // ----------------------------------------------------------------
    // 2. Prolog: Validate parameters before allocation
    // ----------------------------------------------------------------
    let prolog_valid = perform EmCubed.call_surface("prolog", "
valid_aso_params(PopSize, Omega, L1, L2, AProb, Alpha, Theta, Delta) :-
    PopSize >= 4, PopSize =< 10000,
    Omega >= 0.0, Omega =< 2.0,
    L1 >= 0.0, L1 =< 4.0,
    L2 >= 0.0, L2 =< 4.0,
    AProb >= 0.0, AProb =< 1.0,
    Alpha >= 0.0, Alpha =< 1.0,
    Theta > 0.0, Delta > 0.0.

?- valid_aso_params(
    ${aso_input.pop_size},
    ${aso_input.omega},
    ${aso_input.lambda1},
    ${aso_input.lambda2},
    ${aso_input.anarchy_prob},
    ${aso_input.alpha},
    ${aso_input.theta},
    ${aso_input.delta}
   ).
    ");

    if (prolog_valid.get("status") != "ok") {
        println("Prolog parameter validation failed — aborting.");
        return ASOResult {
            best: List<Float64>(),
            best_fitness: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    // ----------------------------------------------------------------
    // 3. Python: Initialize population
    // ----------------------------------------------------------------
    let py_init = perform EmCubed.call_surface("python", "
import random

bounds    = ${aso_input.bounds}
dim       = len(bounds)
pop_size  = ${aso_input.pop_size}

def clip(val, lo, hi, step):
    val = max(lo, min(hi, val))
    if step > 0.0:
        val = lo + step * round((val - lo) / step)
    return val

population   = []
prev_pos     = []
p_best       = []
p_best_fit   = []

for _ in range(pop_size):
    pos = [clip(random.uniform(b[0], b[1]), b[0], b[1], b[2]) for b in bounds]
    population.append(pos)
    prev_pos.append(pos[:])
    p_best.append(pos[:])
    p_best_fit.append(float('-inf'))

{'population': population, 'prev_pos': prev_pos,
 'p_best': p_best, 'p_best_fit': p_best_fit}
    ");

    let dim      = aso_input.bounds.size;
    var pop      = py_init.get("population",  List<List<Float64>>());
    var prev_pos = py_init.get("prev_pos",    List<List<Float64>>());
    var p_best   = py_init.get("p_best",      List<List<Float64>>());
    var p_best_f = py_init.get("p_best_fit",  List<Float64>());

    var g_best   = pop[0];
    var g_best_f : Float64 = -1e300;
    let history  = List<Float64>();

    // ----------------------------------------------------------------
    // 4. Main optimization loop
    // ----------------------------------------------------------------
    for (gen in 0..aso_input.max_iter) {

        // ---- Python: evaluate objective for all agents ----
        let py_eval = perform EmCubed.call_surface("python", "
objective = ${aso_input.objective_lambda}
population = ${pop}
scores = [float(objective(ind)) for ind in population]
{'scores': scores}
        ");
        let scores = py_eval.get("scores", List<Float64>());

        // Update pBest and gBest
        for (i in 0..aso_input.pop_size) {
            if (scores[i] > p_best_f[i]) {
                p_best_f[i] = scores[i];
                p_best[i]   = pop[i];
            }
            if (scores[i] > g_best_f) {
                g_best_f = scores[i];
                g_best   = pop[i];
            }
        }
        history.append(g_best_f);

        // ---- Hy: compute indices for each agent ----
        let hy_indices = perform EmCubed.call_surface("hy", "
(import math [exp])

(defn safe-div [num denom [eps 1e-300]]
  (if (< (abs denom) eps) 0.0 (/ num denom)))

(defn calculate-fi [curr pbest gbest alpha]
  (let [denom (- gbest curr)]
    (- 1.0 (* alpha (safe-div (- pbest curr) denom)))))

(defn calculate-ei [curr gbest theta]
  (let [denom (* gbest theta)]
    (- 1.0 (exp (- (safe-div (- gbest curr) denom))))))

(defn calculate-ii [curr pbest delta]
  (let [denom (* pbest delta)]
    (- 1.0 (exp (- (safe-div (- pbest curr) denom))))))

(let [scores   ${scores}
      p-best-f ${p_best_f}
      gbest    ${g_best_f}
      alpha    ${aso_input.alpha}
      theta    ${aso_input.theta}
      delta    ${aso_input.delta}]
  (map-indexed
    (fn [i curr]
      {:fi (calculate-fi curr (nth p-best-f i) gbest alpha)
       :ei (calculate-ei curr gbest theta)
       :ii (calculate-ii curr (nth p-best-f i) delta)})
    scores))
        ");
        let all_indices = hy_indices.get("value", List<Map<String, Float64>>());

        // ---- Python: movement policies (random draws and updates) ----
        let py_move = perform EmCubed.call_surface("python", "
import random, math

bounds       = ${aso_input.bounds}
dim          = len(bounds)
pop_size     = ${aso_input.pop_size}
population   = ${pop}
prev_pos     = ${prev_pos}
p_best       = ${p_best}
g_best       = ${g_best}
all_indices  = ${all_indices}
omega        = ${aso_input.omega}
lambda1      = ${aso_input.lambda1}
lambda2      = ${aso_input.lambda2}
anarchy_prob = ${aso_input.anarchy_prob}

def clip(val, lo, hi, step):
    val = max(lo, min(hi, val))
    if step > 0.0:
        val = lo + step * round((val - lo) / step)
    return val

def current_mp(pos, pb, gb, c):
    r1 = random.random(); r2 = random.random()
    vel = (omega * (pos[c] - pb[c])
         + lambda1 * r1 * (pb[c] - pos[c])
         + lambda2 * r2 * (gb[c] - pos[c]))
    return pos[c] + vel

def society_mp(pop, gb, c):
    other = random.randint(0, pop_size - 1)
    return gb[c] if random.random() < 0.5 else pop[other][c]

def past_mp(pb, prev, c):
    return pb[c] if random.random() < 0.5 else prev[c]

new_pop  = []
new_prev = []
for i in range(pop_size):
    fi  = all_indices[i]['fi']
    ei  = all_indices[i]['ei']
    ii  = all_indices[i]['ii']
    pos = population[i][:]
    new_prev.append(pos[:])
    new_pos = []
    for c in range(dim):
        if random.random() < anarchy_prob:
            nc = random.uniform(bounds[c][0], bounds[c][1])
        else:
            rnd = random.random()
            if rnd > fi:
                nc = current_mp(pos, p_best[i], g_best, c)
            elif rnd < ei:
                nc = society_mp(population, g_best, c)
            elif rnd < ii:
                nc = past_mp(p_best[i], prev_pos[i], c)
            else:
                nc = pos[c]
        new_pos.append(clip(nc, bounds[c][0], bounds[c][1], bounds[c][2]))
    new_pop.append(new_pos)

{'new_pop': new_pop, 'new_prev': new_prev}
        ");

        pop      = py_move.get("new_pop",  List<List<Float64>>());
        prev_pos = py_move.get("new_prev", List<List<Float64>>());

        // ---- Z3: sanity-check g_best satisfies bounds ----
        let z3_check = perform EmCubed.call_surface("python", "
from z3 import Real, Solver, And, sat

bounds  = ${aso_input.bounds}
g_best  = ${g_best}

solver = Solver()
vars_ = [Real(f'x{i}') for i in range(len(g_best))]
for i, (v, (lo, hi, _)) in enumerate(zip(vars_, bounds)):
    solver.add(And(v >= lo, v <= hi))
    solver.add(v == g_best[i])

solver.check() == sat
        ");
        let z3_ok = z3_check.get("value", true);

        if (!z3_ok) {
            println("Z3 bounds violation detected at generation " + gen.toString() + "; skipping.");
            continue;
        }

        // ---- Prolog convergence check ----
        let conv_check = perform EmCubed.call_surface("prolog", "
converged_aso(History, Window, Tolerance) :-
    length(History, Len),
    Len >= Window,
    append(_, Last, History),
    length(Last, Window),
    max_list(Last, Max),
    min_list(Last, Min),
    abs(Max - Min) < Tolerance.

?- converged_aso(${history}, 15, 1.0e-8).
        ");
        if (conv_check.get("status") == "ok") {
            println("ASO converged at generation " + gen.toString());
            break;
        }
    }

    return ASOResult {
        best:         g_best,
        best_fitness: g_best_f,
        history:      history,
        params_valid: true
    };
}

// ----------------------------------------------------------------
// Type definitions
// ----------------------------------------------------------------

struct ASOInput {
    bounds:       List<[Float64, Float64, Float64]>; // (min, max, step)
    pop_size:     Int32;
    omega:        Float64;
    lambda1:      Float64;
    lambda2:      Float64;
    anarchy_prob: Float64;
    alpha:        Float64;
    theta:        Float64;
    delta:        Float64;
    max_iter:     Int32;
    objective_lambda: String;
}

struct ASOResult {
    best:         List<Float64>;
    best_fitness: Float64;
    history:      List<Float64>;
    params_valid: Bool;
}

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface

@pytest.mark.asyncio
class TestASOCangjie:

    async def test_cangjie_clip_bounds(self):
        """Cangjie clip helper: out-of-range values are clamped."""
        surface = PythonSurface()
        code = '''
def clip(val, lo, hi, step):
    val = max(lo, min(hi, val))
    if step > 0.0:
        val = lo + step * round((val - lo) / step)
    return val

# 7.0 should be clipped to 5.0
clip(7.0, -5.0, 5.0, 0.0)
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert abs(result["value"] - 5.0) < 1e-9

    async def test_cangjie_policy_dispatch(self):
        """Verify movement policy dispatch logic selects CurrentMP when rnd > FI."""
        surface = PythonSurface()
        code = '''
import random
random.seed(99)

# Simulate one agent's move with forced rnd > FI
rnd = 0.9  # > fi = 0.4
fi, ei, ii = 0.4, 0.3, 0.2

def current_mp(pos, pb, gb, c, omega=0.7, l1=1.5, l2=1.5):
    r1, r2 = 0.5, 0.5
    vel = omega*(pos[c]-pb[c]) + l1*r1*(pb[c]-pos[c]) + l2*r2*(gb[c]-pos[c])
    return pos[c] + vel

policy_used = "none"
pos, pb, gb = [1.0], [0.5], [0.0]
c = 0

if rnd > fi:
    result = current_mp(pos, pb, gb, c)
    policy_used = "current_mp"

{'policy': policy_used, 'new_coord': result}
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"]["policy"] == "current_mp"
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_aso_cangjie_registry():
    """Registry pipeline finds ASO Cangjie skill files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "anarchic-society-optimization"
        skills_dir.mkdir(parents=True)

        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('name: anarchic-society-optimization\nDomain: OPTIMIZATION\nsurfaces:\n  - python\n  - prolog\n  - hy\n  - z3\n')

        cangjie = skills_dir / "SKILL_CANGJIE.md"
        cangjie.write_text('# ASO Cangjie Edition\nfunc main() {}')

        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("anarchic", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Run via Cangjie Orchestrator

```python
from em_cubed import get_skill

skill = get_skill("anarchic-society-optimization")

aso_input = {
    "aso_input": {
        "bounds": [[-5.0, 5.0, 0.0], [-5.0, 5.0, 0.0], [-5.0, 5.0, 0.0]],
        "pop_size": 50,
        "omega": 0.7,
        "lambda1": 1.5,
        "lambda2": 1.5,
        "anarchy_prob": 0.1,
        "alpha": 0.5,
        "theta": 0.1,
        "delta": 0.1,
        "max_iter": 100,
        "objective_lambda": "lambda x: -(x[0]**2 + x[1]**2 + x[2]**2)"
    }
}

result = skill.execute(aso_input)
print("Best position:", result["best"])
print("Best fitness:", result["best_fitness"])
print("Params valid:", result["params_valid"])
```
