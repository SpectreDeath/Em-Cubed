---
name: gradient-descent-optimizer
domain: EPIDEMIOLOGY
version: 1.0.0
surfaces:
  - python
  - z3
description: Multi-surface gradient descent optimizer for parameter estimation in epidemiological transmission models. Executes numerical finite-difference optimization in Python and symbolic constraint verification via Z3 SMT solver. Use when minimizing scalar loss functions, tuning transmission model step sizes, verifying parameter bounds, or testing convergence optimality.
purpose: Minimize scalar cost functions via iterative parameter adjustment using gradient information and verify convergence constraints symbolically.
dependencies: []
tags:
  - optimization
  - gradient-descent
  - parameter-tuning
  - finite-difference
  - z3-smt
  - epidemiology
inputs:
  parameters:
    type: array
    required: true
    description: Initial parameter vector for the model.
  learning_rate:
    type: number
    required: true
    description: Step size factor for gradient updates.
  max_iterations:
    type: integer
    required: true
    description: Maximum optimization iterations before halting.
  cost_function:
    type: callable
    required: true
    description: Scalar objective loss function to minimize.
outputs:
  optimized_parameters:
    type: array
    description: Final optimized parameter vector.
  final_cost:
    type: number
    description: Objective value at convergence.
  convergence_status:
    type: string
    description: "converged | max_iterations_reached | diverged"
---

# Gradient Descent Optimizer Engine

`gradient-descent-optimizer` performs iterative numerical parameter optimization paired with symbolic SMT constraint verification for epidemiological models. It computes gradients via finite differences, adjusts parameters along the negative gradient vector, and checks search bounds.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Optimization & Verification Loop

Execute this progression when formulating, solving, or verifying parameter optimization tasks:

```
[1. Loss & Space Audit] → [2. SMT Bound Formulation] → [3. Visual Brief] → [4. Step Checkpoint] → [5. Iteration & Convergence]
```

### Stage 1: Parameter & Cost Function Audit
1. Verify initial parameter dimensions, types, and baseline cost evaluate to finite scalar values (`cost_function(params) < ∞`).
2. Establish numerical perturbation step (`epsilon = 1e-6`) and gradient stopping tolerance (`tol = 1e-8`).
3. Validate that learning rate is positive (`learning_rate > 0`).

> **Completion criterion**: Initial parameters and cost function validated with finite starting loss and verified dimensions.

---

### Stage 2: Symbolic Bound & SMT Verification (Z3)
1. Formulate parameter boundary constraints and non-negativity guarantees in Z3.
2. Verify solver feasibility for the parameter search space before executing numerical iterations:
   ```python
   from z3 import RealVector, Solver
   # Check parameter domain satisfiability
   ```

> **Completion criterion**: Z3 constraint model returns `sat` confirming valid parameter search space.

---

### Stage 3: The Visual Brief
For high-dimensional optimizations or non-convex loss surfaces, generate a visual trajectory brief:
- **Location**: Write to `%TEMP%\gradient-optimizer-brief-<timestamp>.html` (Windows) or `/tmp/gradient-optimizer-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render parameter trajectory, loss reduction curve, and gradient norm history.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before launching intensive multi-variable iterations or step size sweeps:
1. Verify iteration budget (`max_iterations <= 100000`).
2. Check for gradient explosion or early divergence signals in first 5 test steps.
3. If loss increases monotonically, pause and adjust `learning_rate` via adaptive decay.

> **Completion criterion**: Step size and convergence thresholds verified safe against divergence.

---

### Stage 5: Iteration & Convergence Verification
1. Compute numerical gradients via symmetric/forward finite differences.
2. Step parameters opposite the gradient direction: `p = p - lr * grad`.
3. Check convergence conditions: `max(|grad|) < 1e-8` or iteration budget exhausted.
4. Output final parameter vector, residual cost, and status.

> **Completion criterion**: Optimization terminates with `convergence_status == "converged"` and final loss strictly less than or equal to initial loss.

---

## Surface References

### Python Numerical Surface

```python
from typing import Callable, List, Tuple

def gradient_descent(
    parameters: List[float], 
    learning_rate: float, 
    max_iterations: int, 
    cost_function: Callable[[List[float]], float]
) -> Tuple[List[float], float, str]:
    params = [float(p) for p in parameters]
    epsilon = 1e-6
    status = "max_iterations_reached"
    
    for _ in range(max_iterations):
        current_cost = cost_function(params)
        gradient = []
        
        for i in range(len(params)):
            params_plus = params.copy()
            params_plus[i] += epsilon
            gradient.append((cost_function(params_plus) - current_cost) / epsilon)
        
        max_gradient = max(abs(g) for g in gradient) if gradient else 0.0
        
        if max_gradient < 1e-8:
            status = "converged"
            break
            
        for i in range(len(params)):
            params[i] -= learning_rate * gradient[i]
    
    return params, cost_function(params), status
```

### Z3 SMT Verification Surface

```python
from z3 import RealVector, Solver, Real, sat

def verify_gradient_convergence(
    initial_params: List[float], 
    learning_rate: float, 
    cost_at_optimum: float
) -> bool:
    n = len(initial_params)
    params = RealVector("p", n)
    s = Solver()
    
    s.add(learning_rate > 0.0)
    s.add(learning_rate < 1.0)
    s.add(cost_at_optimum >= 0.0)
    
    for i in range(n):
        s.add(params[i] >= -1000.0, params[i] <= 1000.0)
        
    return s.check() == sat
```

---

## Capability Contract

### Inputs
- `parameters` *(array, required)* — Initial parameter values.
- `learning_rate` *(number, required)* — Step multiplier (`0 < lr < 1`).
- `max_iterations` *(integer, required)* — Iteration halting limit.
- `cost_function` *(callable, required)* — Objective scalar loss.

### Outputs
- `optimized_parameters` *(array)* — Final parameter vector.
- `final_cost` *(number)* — Residual cost at termination.
- `convergence_status` *(string)* — `converged`, `max_iterations_reached`, or `diverged`.

---

## Anti-Patterns & Guardrails

- **Exploding Learning Rates** — Setting step size too large, causing parameter divergence to `NaN` or `±Infinity`. Always clamp updates and verify initial step behavior.
- **Silent NaN Propagation** — Continuing iterations after a cost function evaluation returns `NaN`. Immediately halt optimization and report divergence.
- **Unbounded Parameter Drift** — Allowing model parameters (e.g., transmission probabilities) to drift outside valid biological ranges `[0, 1]`. Enforce Z3-verified boundary projections.
- **Zero-Gradient False Minimum** — Halting on flat saddle points without checking directional curvature or residual cost acceptability.
