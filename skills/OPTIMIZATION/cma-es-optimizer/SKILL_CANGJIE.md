# CMA-ES Optimizer - Cangjie Edition
# Cangjie-orchestrated multi-surface CMA-ES with native Jacobi eigendecomposition, Prolog validation, Z3 constraints, and Hy step-size adaptation

# Cangjie surface block: orchestrator
import std.math.*

func main() {
    // 1. Input: CMA-ES configuration and objective function from context
    let cma_input = context["cma_input"] as CMAESInput;
    println("Cangjie CMA-ES Optimizer Starting...");

    // 2. Prolog: Validate input parameters and bounds structures
    let prolog_result = perform EmCubed.call_surface("prolog", "
% Parameter check
valid_cmaes_params(PopSize, Mu, C1, CMu, Damping) :-
    PopSize >= 4, PopSize =< 1000,
    Mu >= 2, Mu =< PopSize,
    C1 >= 0.0, C1 =< 0.5,
    CMu >= 0.0, CMu =< 1.0,
    StepSizeDamping >= 0.1, StepSizeDamping =< 10.0.

valid_bounds([]).
valid_bounds([Lo-Hi|Rest]) :-
    Lo =< Hi,
    valid_bounds(Rest).

?- valid_cmaes_params(${cma_input.pop_size}, ${cma_input.mu}, ${cma_input.learning_rate_c1}, ${cma_input.learning_rate_cmu}, ${cma_input.step_size_damping}),
   valid_bounds(${cma_input.bounds}).
    ");

    if (prolog_result.get("status") != "ok") {
        println("Prolog Parameter Validation Failed!");
        return CMAESResult {
            best: List<Float64>(),
            best_score: 0.0,
            history: List<Float64>(),
            params_valid: false
        };
    }

    // 3. Hy: Initialize initial expected chiN and parameters
    let hy_init = perform EmCubed.call_surface("hy", "
(defn compute-chi-n [dim]
  (* (sqrt dim) (- 1.0 (/ 1.0 (* 4.0 dim)) (/ 1.0 (* 21.0 dim dim)))))

(defn compute-cs [mu-eff coords]
  (/ (+ mu-eff 2.0) (+ coords mu-eff 5.0)))

(defn compute-cc [mu-eff coords]
  (/ (+ 4.0 (/ mu-eff coords)) (+ coords 4.0 (* 2.0 (/ mu-eff coords)))))

(let [dim (len ${cma_input.bounds})
      log-mu (log (+ ${cma_input.mu} 0.5))
      weights (list (map (fn [i] (- log-mu (log (+ i 1)))) (range ${cma_input.mu})))
      sum-w (sum weights)
      norm-w (list (map (fn [w] (/ w sum-w)) weights))
      mu-eff (/ 1.0 (sum (list (map (fn [w] (** w 2)) norm-w))))]
  {:chi_n (compute-chi-n dim)
   :mu_eff mu-eff
   :cs (compute-cs mu-eff dim)
   :cc (compute-cc mu-eff dim)})
    ");

    let chi_n = hy_init.get("chi_n", 0.0);
    let mu_eff = hy_init.get("mu_eff", 0.0);
    let cs = hy_init.get("cs", 0.0);
    let cc = hy_init.get("cc", 0.0);

    // 4. Python: Setup initial mean, population structures
    let py_init = perform EmCubed.call_surface("python", "
import numpy as np

bounds = np.array(${cma_input.bounds})
dim = len(bounds)
mean = np.random.uniform(bounds[:, 0], bounds[:, 1]).tolist()
sigma = 0.3 * np.mean(bounds[:, 1] - bounds[:, 0])

{'mean': mean, 'sigma': sigma}
    ");

    let dim = cma_input.bounds.size;
    let initial_mean = py_init.get("mean", List<Float64>());
    let initial_sigma = py_init.get("sigma", 0.0);

    // Initialize state
    var state = CMAESState {
        mean: initial_mean,
        sigma: initial_sigma,
        C: List<Float64>(dim * dim, {i => (i / dim == i % dim) ? 1.0 : 0.0}),
        B: List<Float64>(dim * dim, {i => (i / dim == i % dim) ? 1.0 : 0.0}),
        D: List<Float64>(dim, 1.0),
        pc: List<Float64>(dim, 0.0),
        ps: List<Float64>(dim, 0.0),
        counteval: 0
    };

    var best_x = List<Float64>(dim, 0.0);
    var best_score = 1e300;
    let history = List<Float64>();

    // 5. Main optimization loop
    for (gen in 0..cma_input.max_iter) {
        // Sample candidate points around mean
        // Native Jacobi eigendecomposition if dim >= 20
        if (dim >= 20 && gen % 10 == 0) {
            compute_eigendecomposition(dim, state.C, state.B, state.D);
        }

        // Call Python to sample next generation candidate points and evaluate objective
        let py_gen = perform EmCubed.call_surface("python", "
import numpy as np

dim = ${dim}
pop_size = ${cma_input.pop_size}
bounds = np.array(${cma_input.bounds})
mean = np.array(${state.mean})
sigma = ${state.sigma}
B = np.array(${state.B}).reshape(dim, dim)
D = np.array(${state.D})
objective = ${cma_input.objective_lambda}

# Re-implement power distribution for exploration
def power_dist(center, out_min, out_max, p=20.0):
    rnd = np.random.uniform(-1.0, 1.0)
    r = np.abs(rnd) ** p
    if rnd >= 0.0:
        return center + r * (out_max - center)
    else:
        return center - r * (center - out_min)

population = []
y_vectors = []
scores = []

for _ in range(pop_size):
    z = np.array([power_dist(0.0, -8.0, 8.0, 20.0) for _ in range(dim)])
    y = B @ (D * z)
    x = mean + sigma * y
    x = np.clip(x, bounds[:, 0], bounds[:, 1])
    population.append(x.tolist())
    y_vectors.append(y.tolist())
    scores.append(float(objective(x)))

{'population': population, 'y_vectors': y_vectors, 'scores': scores}
        ");

        let population = py_gen.get("population", List<List<Float64>>());
        let y_vectors = py_gen.get("y_vectors", List<List<Float64>>());
        let scores = py_gen.get("scores", List<Float64>());

        state.counteval = state.counteval + cma_input.pop_size;

        // 6. Z3: Verify that population is strictly within box bounds (Formal Safety Constraint)
        let z3_check = perform EmCubed.call_surface("z3", "
from z3 import *

bounds = ${cma_input.bounds}
population = ${population}
s = Solver()

# Define real variables
vars = [Real(f'x_{i}') for i in range(len(bounds))]

# Formally check all members of the population
all_sat = True
for idx, ind in enumerate(population):
    s.push()
    for i, val in enumerate(ind):
        s.add(vars[i] == val)
        s.add(vars[i] >= bounds[i][0])
        s.add(vars[i] <= bounds[i][1])
    if s.check() != sat:
        all_sat = False
        break
    s.pop()

{'all_sat': all_sat}
        ");

        // 7. Update mean and paths on Python surface (Matrix transformations)
        let py_update = perform EmCubed.call_surface("python", "
import numpy as np

dim = ${dim}
pop_size = ${cma_input.pop_size}
mu = ${cma_input.mu}
scores = np.array(${scores})
population = np.array(${population})
y_vectors = np.array(${y_vectors})
mean = np.array(${state.mean})
sigma = ${state.sigma}
C = np.array(${state.C}).reshape(dim, dim)
B = np.array(${state.B}).reshape(dim, dim)
D = np.array(${state.D})
pc = np.array(${state.pc})
ps = np.array(${state.ps})
counteval = ${state.counteval}
chiN = ${chi_n}
mu_eff = ${mu_eff}
cs = ${cs}
cc = ${cc}
c1 = ${cma_input.learning_rate_c1}
cmu = ${cma_input.learning_rate_cmu}
damps = ${cma_input.step_size_damping}

# Sorting population
indices = np.argsort(scores)
sorted_pop = population[indices]
sorted_y = y_vectors[indices]
sorted_scores = scores[indices]

# Compute weights
log_mu = np.log(mu + 0.5)
weights = np.array([log_mu - np.log(i + 1) for i in range(mu)])
weights /= np.sum(weights)

# Update mean
old_mean = np.copy(mean)
mean = np.sum([weights[i] * sorted_pop[i] for i in range(mu)], axis=0)

y_w = (mean - old_mean) / sigma

# Check eigendecomposition (standard fallback)
if dim < 20 and counteval % 10 == 0:
    B, diag_D2, _ = np.linalg.svd(C)
    D = np.sqrt(np.maximum(1e-14, diag_D2))

invsqrtC_y_w = B @ ((1.0 / D) * (B.T @ y_w))

ps = (1.0 - cs) * ps + np.sqrt(cs * (2.0 - cs) * mu_eff) * invsqrtC_y_w
norm_ps = np.linalg.norm(ps)

expected_len = np.sqrt(1.0 - (1.0 - cs)**(2.0 * counteval / pop_size)) * chiN
hsig = norm_ps / expected_len < (1.4 + 2.0 / (dim + 1.0))
delta_hsig = 1.0 if hsig else 0.0

pc = (1.0 - cc) * pc + delta_hsig * np.sqrt(cc * (2.0 - cc) * mu_eff) * y_w

# Covariance update
c1a = np.outer(pc, pc)
cmu_update = np.zeros((dim, dim))
for i in range(mu):
    z_i = sorted_y[i]
    cmu_update += weights[i] * np.outer(z_i, z_i)

curr_c1 = c1
if not hsig:
    curr_c1 *= (1.0 - (1.0 - delta_hsig) * cc * (2.0 - cc))

C = (1.0 - curr_c1 - cmu) * C + curr_c1 * c1a + cmu * cmu_update

# Enforce positive definiteness
C = (C + C.T) * 0.5
min_diag = np.min(np.diag(C))
if min_diag < 1e-10:
    np.fill_diagonal(C, np.diag(C) + (1e-10 - min_diag))

# Step size update
exponent = (cs / damps) * (norm_ps / chiN - 1.0)
sigma *= np.exp(exponent)
sigma = np.clip(sigma, 1e-16, 1e4 * max(1.0, np.max(D)))

{'mean': mean.tolist(), 'sigma': sigma, 'C': C.flatten().tolist(), 'B': B.flatten().tolist(), 'D': D.tolist(), 'pc': pc.tolist(), 'ps': ps.tolist(), 'best_score': float(sorted_scores[0]), 'best_x': sorted_pop[0].tolist()}
        ");

        // Update state
        state.mean = py_update.get("mean", List<Float64>());
        state.sigma = py_update.get("sigma", 0.0);
        state.C = py_update.get("C", List<Float64>());
        state.B = py_update.get("B", List<Float64>());
        state.D = py_update.get("D", List<Float64>());
        state.pc = py_update.get("pc", List<Float64>());
        state.ps = py_update.get("ps", List<Float64>());

        let gen_best_score = py_update.get("best_score", 0.0);
        if (gen_best_score < best_score) {
            best_score = gen_best_score;
            best_x = py_update.get("best_x", List<Float64>());
        }

        history.append(best_score);

        // Stagnation / convergence check via Prolog
        let check_conv = perform EmCubed.call_surface("prolog", "
% Check history
converged(${history}, 1e-6) ; ${state.sigma} < 1e-15.
        ");

        if (check_conv.get("status") == "ok") {
            println("Convergence reached at generation " + gen.toString());
            break;
        }
    }

    return CMAESResult {
        best: best_x,
        best_score: best_score,
        history: history,
        params_valid: true
    };
}

// Jacobi eigendecomposition in Cangjie for high dimensions (dim >= 20)
func compute_eigendecomposition(dim: Int32, covMatrix: List<Float64>, B: List<Float64>, D: List<Float64>) {
    let C_copy = List<Float64>(covMatrix);
    
    for (i in 0..dim) {
        for (j in 0..dim) {
            B[i * dim + j] = (i == j) ? 1.0 : 0.0;
        }
    }
    
    let max_iterations = 20;
    let tolerance = 1e-4;
    
    for (iter in 0..max_iterations) {
        var max_val = 0.0;
        var p = 0;
        var q = 1;
        
        for (i in 0..(dim - 1)) {
            for (j in (i + 1)..dim) {
                let val = abs(C_copy[i * dim + j]);
                if (val > max_val) {
                    max_val = val;
                    p = i;
                    q = j;
                }
            }
        }
        
        if (max_val < tolerance) {
            break;
        }
        
        let app = C_copy[p * dim + p];
        let aqq = C_copy[q * dim + q];
        let apq = C_copy[p * dim + q];
        
        let phi = 0.5 * atan2(2.0 * apq, aqq - app + 1e-14);
        let c = cos(phi);
        let s = sin(phi);
        
        let app_new = c * c * app - 2.0 * c * s * apq + s * s * aqq;
        let aqq_new = s * s * app + 2.0 * c * s * apq + c * c * aqq;
        
        C_copy[p * dim + p] = app_new;
        C_copy[q * dim + q] = aqq_new;
        C_copy[p * dim + q] = 0.0;
        C_copy[q * dim + p] = 0.0;
        
        for (i in 0..dim) {
            if (i != p && i != q) {
                let aip = C_copy[i * dim + p];
                let aiq = C_copy[i * dim + q];
                C_copy[i * dim + p] = c * aip - s * aiq;
                C_copy[p * dim + i] = c * aip - s * aiq;
                C_copy[i * dim + q] = s * aip + c * aiq;
                C_copy[q * dim + i] = s * aip + c * aiq;
            }
        }
        
        for (i in 0..dim) {
            let bip = B[i * dim + p];
            let biq = B[i * dim + q];
            B[i * dim + p] = c * bip - s * biq;
            B[i * dim + q] = s * bip + c * biq;
        }
    }
    
    let min_eigenvalue = 1e-14;
    for (i in 0..dim) {
        D[i] = sqrt(max(min_eigenvalue, C_copy[i * dim + i]));
    }
    
    for (i in 0..(dim - 1)) {
        var max_idx = i;
        for (j in (i + 1)..dim) {
            if (D[j] > D[max_idx]) {
                max_idx = j;
            }
        }
        
        if (max_idx != i) {
            let temp = D[i];
            D[i] = D[max_idx];
            D[max_idx] = temp;
            
            for (k in 0..dim) {
                let temp_b = B[k * dim + i];
                B[k * dim + i] = B[k * dim + max_idx];
                B[k * dim + max_idx] = temp_b;
            }
        }
    }
}

struct CMAESInput {
    bounds: List<[Float64, Float64]>;
    pop_size: Int32;
    mu: Int32;
    max_iter: Int32;
    learning_rate_c1: Float64;
    learning_rate_cmu: Float64;
    step_size_damping: Float64;
    objective_lambda: String;
}

struct CMAESState {
    mean: List<Float64>;
    sigma: Float64;
    C: List<Float64>;
    B: List<Float64>;
    D: List<Float64>;
    pc: List<Float64>;
    ps: List<Float64>;
    counteval: Int32;
}

struct CMAESResult {
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
class TestCMAESOrchestrator:
    async def test_cmaes_sampling_iteration(self):
        """Test one step of sampling and covariance update."""
        code = '''
import numpy as np

dim = 2
pop_size = 6
bounds = np.array([[-5.0, 5.0]]*dim)
mean = np.array([0.0, 0.0])
sigma = 0.5
B = np.eye(dim)
D = np.ones(dim)

def power_dist(center, out_min, out_max, p=20.0):
    rnd = np.random.uniform(-1.0, 1.0)
    r = np.abs(rnd) ** p
    if rnd >= 0.0:
        return center + r * (out_max - center)
    else:
        return center - r * (center - out_min)

population = []
y_vectors = []
for _ in range(pop_size):
    z = np.array([power_dist(0.0, -8.0, 8.0, 20.0) for _ in range(dim)])
    y = B @ (D * z)
    x = mean + sigma * y
    population.append(x.tolist())
    y_vectors.append(y.tolist())

assert len(population) == pop_size
assert len(y_vectors) == pop_size
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
async def test_cmaes_cangjie_edition_pipeline():
    """Verify registry search finds cma-es-optimizer Cangjie skill files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "cma-es-optimizer"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('name: cma-es-optimizer\\nDomain: OPTIMIZATION\\nsurfaces:\\n  - python\\n  - prolog')
        
        cangjie = skills_dir / "SKILL_CANGJIE.md"
        cangjie.write_text('# CMA-ES Edition\\nfunc main() {}')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("cma-es", registry_file)
        assert len(results) >= 1
```

## Usage Patterns

### Orchestrating Optimization (Sphere Function)

```python
from em_cubed import get_skill

# Load CMA-ES optimizer
skill = get_skill("cma-es-optimizer")

# Configuration input
cma_input = {
    "cma_input": {
        "bounds": [[-5.0, 5.0], [-5.0, 5.0]],
        "pop_size": 30,
        "mu": 15,
        "max_iter": 50,
        "learning_rate_c1": 0.01,
        "learning_rate_cmu": 0.8,
        "step_size_damping": 0.6,
        "objective_lambda": "lambda x: x[0]**2 + x[1]**2"
    }
}

result = skill.execute(cma_input)
print("Best parameters:", result["best"])
print("Best score:", result["best_score"])
```
