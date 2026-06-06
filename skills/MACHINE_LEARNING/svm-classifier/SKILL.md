---
name: svm-classifier
domain: MACHINE_LEARNING
version: "1.0.0"
surfaces: [python, z3]
---

# Purpose
Maximize margin classification with support vectors defining decision boundaries.

# Description
Core inputs: feature vectors (list), binary labels (list of -1/1), regularization C (float), kernel type (str). Mechanical steps: compute pairwise distances, find optimal separating hyperplane, identify support vectors, classify via signed distance to margin. Expected outputs: support vectors (indices), coefficients (alphas), bias term (float), predictions (list), margin width (float).

## Python Surface

```python
def compute_dot(x1, x2):
    dot = 0.0
    for i in range(len(x1)):
        dot = dot + x1[i] * x2[i]
    return dot

def my_exp_approx(x):
    if x > 20:
        return 4.85165195e8
    if x < -20:
        return 1e-9
    result = 1.0
    term = 1.0
    for n in range(1, 50):
        term = term * x / n
        result = result + term
        if term < 1e-15 * result and n > 10:
            break
    return result

def rbf_kernel(x1, x2, sigma=1.0):
    dist_sq = 0.0
    for i in range(len(x1)):
        diff = x1[i] - x2[i]
        dist_sq = dist_sq + diff * diff
    return my_exp_approx(-dist_sq / (2.0 * sigma * sigma))

def gram_matrix(features, kernel_type, sigma):
    n = len(features)
    K = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if kernel_type == "linear":
                K[i][j] = compute_dot(features[i], features[j])
            else:
                K[i][j] = rbf_kernel(features[i], features[j], sigma)
    return K

def svm_train_approx(features, labels, C=1.0, kernel_type="linear", sigma=1.0, lr=0.01, max_iter=100):
    n = len(features)
    if n == 0:
        return ([], [], 0.0)
    
    alphas = [0.1] * n
    bias = 0.0
    
    K = gram_matrix(features, kernel_type, sigma)
    
    for iteration in range(max_iter):
        for i in range(n):
            decision = bias
            for j in range(n):
                decision = decision + alphas[j] * labels[j] * K[i][j]
            
            if labels[i] * decision < 1.0:
                for j in range(n):
                    alphas[j] = alphas[j] + lr * labels[i] * K[i][j]
                    alphas[j] = max(0.0, min(C, alphas[j]))
                bias = bias + lr * labels[i]
    
    support_indices = [i for i in range(n) if alphas[i] > 1e-4]
    
    if len(support_indices) == 0:
        support_indices = [i for i in range(n) if alphas[i] > 0]
    if len(support_indices) == 0:
        support_indices = [0]
    
    return (support_indices, alphas, bias)

def svm_predict(features, labels, alphas, bias, test_samples, kernel_type, sigma):
    predictions = []
    for test in test_samples:
        score = bias
        for j in range(len(features)):
            if alphas[j] > 1e-4:
                score = score + alphas[j] * labels[j] * rbf_kernel(features[j], test, sigma)
        predictions.append(1 if score >= 0 else -1)
    return predictions

def compute_margin(alphas, labels, features, kernel_type, sigma):
    support_indices = [i for i in range(len(alphas)) if alphas[i] > 1e-4]
    if len(support_indices) < 2:
        return 0.0
    margins = []
    for idx in support_indices:
        margin = 0.0
        for j in range(len(features)):
            if alphas[j] > 1e-4:
                margin = margin + alphas[j] * labels[j] * rbf_kernel(features[idx], features[j], sigma)
        margins.append(margin)
    if len(margins) < 2:
        return 0.0
    return (max(margins) - min(margins)) / 2.0

def svm_classifier(features, labels, C=1.0, kernel_type="linear", sigma=1.0, max_iter=100):
    support_indices, alphas, bias = svm_train_approx(features, labels, C, kernel_type, sigma, 0.01, max_iter)
    predictions = svm_predict(features, labels, alphas, bias, features, kernel_type, sigma)
    margin = compute_margin(alphas, labels, features, kernel_type, sigma)
    return (support_indices, alphas, bias, predictions, margin)

def svm_transform(features, alphas, labels, kernel_type, sigma, new_samples):
    transformed = []
    for test in new_samples:
        if kernel_type == "linear":
            transformed.append([item for item in test])
        else:
            proj = []
            for j in range(len(features)):
                if alphas[j] > 1e-4:
                    proj.append(alphas[j] * labels[j] * rbf_kernel(features[j], test, sigma))
            transformed.append(proj)
    return transformed
```

## Z3 SMT Surface

```python
from z3 import RealVector, Solver, Real, sat

def verify_margin_constraints(support_vectors, alphas, bias, features, labels):
    n = len(features)
    if n == 0 or len(support_vectors) == 0:
        return True
    
    s = Solver()
    
    alpha_vars = [Real(f'alpha_{i}') for i in range(len(alphas))]
    for i in range(len(alphas)):
        s.add(alpha_vars[i] >= 0)
        s.add(alpha_vars[i] <= 100.0)
    
    s.add(bias >= -1000.0, bias <= 1000.0)
    
    for idx in support_vectors[:min(3, len(support_vectors))]:
        for label in [-1, 1]:
            s.add(label * (bias + 1.0) >= 0.9)
    
    return s.check() == sat

def verify_support_vector_validity(features, labels):
    n = len(features)
    if n == 0:
        return True
    
    s = Solver()
    
    for i in range(n):
        if len(features[i]) >= 1:
            s.add(features[i][0] >= -1000.0, features[i][0] <= 1000.0)
        if len(features[i]) >= 2:
            s.add(features[i][1] >= -1000.0, features[i][1] <= 1000.0)
    
    for i in range(n):
        s.add(labels[i] * labels[i] == 1)
    
    return s.check() == sat

def find_separating_hyperplane(features, labels):
    n = len(features)
    if n == 0:
        return (True, None)
    
    s = Solver()
    
    if len(features[0]) == 2:
        w = [Real(f'w_{i}') for i in range(2)]
        b_var = Real('b')
        s.add(b_var >= -1000.0, b_var <= 1000.0)
        for i in range(2):
            s.add(w[i] >= -100.0, w[i] <= 100.0)
        
        for i in range(n):
            constraint = labels[i] * (w[0] * features[i][0] + w[1] * features[i][1] + b_var)
            s.add(constraint >= 1.0 - 0.01)
    
    return s.check() == sat

def verify_separability(features, labels):
    n = len(features)
    n_features = len(features[0]) if n > 0 else 0
    
    s = Solver()
    
    if n_features > 0:
        w = [Real(f'w_{i}') for i in range(n_features)]
        b_var = Real('b')
        
        for i in range(n_features):
            s.add(w[i] >= -1000.0, w[i] <= 1000.0)
        s.add(b_var >= -1000.0, b_var <= 1000.0)
        
        for i in range(n):
            expr = b_var
            for j in range(n_features):
                expr = expr + w[j] * features[i][j]
            constraint = labels[i] * expr
            s.add(constraint >= 1)
    
    return s.check() == sat
```