---
name: logistic-regression-classifier
domain: MACHINE_LEARNING
version: "1.0.0"
surfaces: [python, z3]
---

# Purpose
Fit probabilistic binary classifier using sigmoid transformation of linear features.

# Description
Core inputs: feature matrix (list of vectors), binary labels (list of 0/1), learning rate (float), iterations (int). Mechanical steps: initialize weights to zeros, compute sigmoid predictions, calculate gradients of log-likelihood loss, update weights via gradient ascent, iterate to convergence. Expected outputs: coefficient vector (list), bias term (float), predicted probabilities (list of floats).

## Python Surface

```python
def my_exp(x):
    if x > 50:
        return 1e21
    if x < -50:
        return 0.0
    result = 1.0
    term = 1.0
    for i in range(1, 30):
        term = term * x / i
        result = result + term
    return result

def sigmoid(z):
    exp_val = my_exp(-z)
    if exp_val > 1e10:
        return 0.0
    if exp_val < 1e-10:
        return 1.0
    return 1.0 / (1.0 + exp_val)

def logistic_regression(features, labels, learning_rate, max_iterations):
    n = len(features)
    if n == 0:
        return ([], 0.0, [])
    
    p = len(features[0])
    weights = [0.0] * p
    bias = 0.0
    
    for _ in range(max_iterations):
        dw = [0.0] * p
        db = 0.0
        
        for i in range(n):
            z = bias
            for j in range(p):
                z = z + weights[j] * features[i][j]
            pred = sigmoid(z)
            err = pred - labels[i]
            
            for j in range(p):
                dw[j] = dw[j] + err * features[i][j]
            db = db + err
        
        for j in range(p):
            weights[j] = weights[j] - learning_rate * dw[j] / n
        bias = bias - learning_rate * db / n
    
    predictions = []
    for i in range(n):
        z = bias
        for j in range(p):
            z = z + weights[j] * features[i][j]
        predictions.append(sigmoid(z))
    
    return (weights, bias, predictions)
```

## Z3 SMT Surface

```python
from z3 import RealVector, Solver, Implies, Or

def verify_logistic_bounds(weights, bias, features, labels):
    n = len(features)
    p = len(weights)
    m = len(features[0]) if n > 0 else 0
    
    s = Solver()
    
    for i in range(m):
        s.add(weights[i] >= -100.0, weights[i] <= 100.0)
    s.add(bias >= -100.0, bias <= 100.0)
    
    for i in range(n):
        s.add(Implies(labels[i] == 1, Or([features[i][j] * weights[j] + bias > 0 for j in range(m)])))
    
    return s.check() == sat
```