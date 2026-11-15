# Skill Summary Card: `gradient-descent-optimizer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        gradient-descent-optimizer                │
│ Category:    EPIDEMIOLOGY / Numerical Optimization    │
│ Invocation:  /gradient-descent-optimizer               │
│ Trigger:     "optimize gradient", "tune step size",    │
│              "minimize cost function", "fit epidemic"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Minimize scalar cost functions with finite│
│              differences and verify parameter search   │
│              bounds using Z3 SMT constraints.          │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Loss & Space Audit** | Validate dimensions and initial cost evaluations | Parameter Spec AST | Initial cost evaluates to finite scalar |
| **2. SMT Bound Check** | Verify parameter boundary satisfiability via Z3 | Solver Status | Z3 solver returns `sat` |
| **3. Visual Brief** | Render loss profile and parameter trajectory | `%TEMP%\gradient-optimizer-brief-*.html` | Dark theme HTML trajectory report |
| **4. Step Checkpoint** | Validate learning rate bounds and divergence risk | Verification Record | Initial 5-step loss gradient verified stable |
| **5. Iteration & Finish** | Execute gradient steps until tolerance reached | `(params, cost, status)` | `convergence_status == "converged"` or budget hit |

---

## Surface Cheat Sheet

### Python Numerical Surface
```python
params, final_cost, status = gradient_descent(
    parameters=[0.5, 0.1],
    learning_rate=0.01,
    max_iterations=1000,
    cost_function=loss_fn,
)
```

### Z3 SMT Verification Surface
```python
is_valid = verify_gradient_convergence(
    initial_params=[0.5, 0.1],
    learning_rate=0.01,
    cost_at_optimum=0.002,
)
```

---

## Invariants & Guardrails

- [ ] **Bounded Search Space**: Parameters checked against domain bounds `[0, 1]` or defined physical bounds.
- [ ] **Finite Differences Stability**: Perturbation `epsilon` set to `1e-6` with protection against division by zero.
- [ ] **Zero NaN Tolerance**: Abort immediately if any step yields non-finite numbers.
- [ ] **Positive Learning Rate**: Strict check `0 < lr < 1` prior to iteration dispatch.
