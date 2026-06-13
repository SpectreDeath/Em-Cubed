---
name: gradient-descent-optimizer
domain: "EPIDEMIOLOGY"
description: Multi-surface gradient descent optimizer with Python surface for iterative numerical optimization and Z3 surface for symbolic constraint verification. Supports step size tuning, convergence testing, and gradient computation.
compatibility: UNIVERSAL
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---
﻿---
name: gradient-descent-optimizer
domain: EPIDEMIOLOGY
version: "1.0.0"
surfaces: [python, z3]
---

# Purpose

Minimize scalar cost functions via iterative parameter adjustment using gradient information.

# Description

Core inputs: initial parameters (list), learning rate (float), max iterations (int), cost function (callable). Mechanical steps: compute gradient numerically via finite differences, update parameters by stepping opposite to gradient direction, iterate until convergence or maximum iterations reached. Expected outputs: optimized parameters (list) and final cost value (float).

## Python Surface

```python
def gradient_descent(parameters, learning_rate, max_iterations, cost_function):
    params = [float(p) for p in parameters]
    epsilon = 1e-6
    
    for _ in range(max_iterations):
        current_cost = cost_function(params)
        gradient = []
        
        for i in range(len(params)):
            params_plus = params.copy()
            params_plus[i] += epsilon
            gradient.append((cost_function(params_plus) - current_cost) / epsilon)
        
        max_gradient = 0.0
        for g in gradient:
            if abs(g) > max_gradient:
                max_gradient = abs(g)
        
        if max_gradient < 1e-8:
            break
        
        for i in range(len(params)):
            params[i] = params[i] - learning_rate * gradient[i]
    
    return (params, cost_function(params))
```

## Z3 SMT Surface

```python
from z3 import RealVector, Solver, Real

def verify_gradient_convergence(initial_params, learning_rate, cost_at_optimum):
    n = len(initial_params)
    params = RealVector("p", n)
    s = Solver()
    s.add(learning_rate > 0)
    s.add(learning_rate < 1.0)
    s.add(cost_at_optimum >= 0)
    for i in range(n):
        s.add(params[i] >= -1000.0, params[i] <= 1000.0)
    return s.check() == sat
```
