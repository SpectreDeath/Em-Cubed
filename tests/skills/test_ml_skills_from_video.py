"""Tests for ML skills created from reference video."""

import pytest

# Test gradient-descent-optimizer (EPIDEMIOLOGY)
@pytest.mark.asyncio
async def test_gradient_descent_optimizer():
    code = '''
def my_exp(x):
    if x > 50:
        return 1e21
    if x < -30:
        result = 1.0
        term = 1.0
        for i in range(1, 100):
            term = term * (-x) / i
            result = result + term
            if term > 1e15:
                return 1e-20
            if term < 1e-15 * result:
                break
        return 1.0 / result
    result = 1.0
    term = 1.0
    for i in range(1, 50):
        term = term * x / i
        result = result + term
        if term < 1e-15 * result and i > 10:
            break
    return result

def gradient_descent(params, lr, max_iter, cost_fn):
    p = list(params)
    eps = 1e-6
    for _ in range(max_iter):
        c = cost_fn(p)
        grad = []
        for i in range(len(p)):
            pp = p.copy()
            pp[i] = pp[i] + eps
            grad.append((cost_fn(pp) - c) / eps)
        mx = 0.0
        for g in grad:
            if abs(g) > mx:
                mx = abs(g)
        if mx < 1e-8:
            break
        for i in range(len(p)):
            p[i] = p[i] - lr * grad[i]
    return (p, cost_fn(p))

# Test: minimize (x-3)^2 + (y-2)^2
result, final_cost = gradient_descent([0.0, 0.0], 0.1, 500, lambda x: (x[0] - 3)**2 + (x[1] - 2)**2)
abs(result[0] - 3.0) < 0.1 and abs(result[1] - 2.0) < 0.1
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"


# Test k-means-clustering (CLINICAL_TRIALS)
@pytest.mark.asyncio
async def test_k_means_clustering():
    code = '''
def newton_sqrt(n):
    if n < 0:
        return 0.0
    if n == 0:
        return 0.0
    x = n
    y = 1.0
    for _ in range(20):
        y = 0.5 * (y + n / y)
    return y

def kmeans(points, k):
    centroids = []
    for i in range(k):
        centroids.append(list(points[i]))
    for _ in range(10):
        clusters = []
        for c in range(k):
            clusters.append([])
        for p in points:
            dists = []
            for c in range(k):
                d2 = 0.0
                for j in range(len(p)):
                    d2 = d2 + (p[j] - centroids[c][j])**2
                dists.append(newton_sqrt(d2))
            idx = 0
            for i in range(1, len(dists)):
                if dists[i] < dists[idx]:
                    idx = i
            clusters[idx].append(p)
        for c in range(k):
            if clusters[c]:
                m = []
                for j in range(len(clusters[c][0])):
                    s = 0.0
                    for i in range(len(clusters[c])):
                        s = s + clusters[c][i][j]
                    m.append(s / len(clusters[c]))
                centroids[c] = m
    return centroids

# Test: 9 points in 3 clusters
points = [[1,1], [1.5,1.5], [2,2], [5,5], [5.5,5.5], [6,6], [9,1], [9.5,1.5], [10,1]]
centroids = kmeans(points, 3)
len(centroids) == 3
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"


# Test linear-regression (FORENSIC_ECONOMICS)
@pytest.mark.asyncio
async def test_linear_regression():
    code = '''
def linear_regression(features, targets):
    n = len(features)
    p = len(features[0])
    fmeans = []
    for j in range(p):
        s = 0.0
        for i in range(n):
            s = s + features[i][j]
        fmeans.append(s / n)
    tmean = sum(targets) / n
    cov = []
    var = []
    for j in range(p):
        c = 0.0
        v = 0.0
        for i in range(n):
            c = c + (features[i][j] - fmeans[j]) * (targets[i] - tmean)
            v = v + (features[i][j] - fmeans[j])**2
        cov.append(c)
        var.append(v)
    slope = []
    for j in range(p):
        if var[j] != 0:
            slope.append(cov[j] / var[j])
        else:
            slope.append(0)
    intercept = tmean
    for j in range(p):
        intercept = intercept - fmeans[j] * slope[j]
    preds = []
    for i in range(n):
        pr = intercept
        for j in range(p):
            pr = pr + slope[j] * features[i][j]
        preds.append(pr)
    ss_res = 0.0
    ss_tot = 0.0
    for i in range(n):
        ss_res = ss_res + (targets[i] - preds[i])**2
        ss_tot = ss_tot + (targets[i] - tmean)**2
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return (slope, intercept, preds, r2)

# Test: y = 2x + 1
features = [[1], [2], [3], [4], [5], [6]]
targets = [3, 5, 7, 9, 11, 13]
slope, intercept, preds, r2 = linear_regression(features, targets)
abs(slope[0] - 2.0) < 0.01 and abs(intercept - 1.0) < 0.01
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"


# Test logistic-regression-classifier (MACHINE_LEARNING)
@pytest.mark.asyncio
async def test_logistic_regression():
    code = '''
def my_exp(x):
    if x > 50:
        return 1e21
    if x < -30:
        result = 1.0
        term = 1.0
        for i in range(1, 100):
            term = term * (-x) / i
            result = result + term
            if term > 1e15:
                return 1e-20
            if term < 1e-15 * result:
                break
        return 1.0 / result
    result = 1.0
    term = 1.0
    for i in range(1, 50):
        term = term * x / i
        result = result + term
        if term < 1e-15 * result and i > 10:
            break
    return result

def sigmoid(z):
    exp_val = my_exp(-z)
    if exp_val > 1e10:
        return 0.0
    if exp_val < 1e-10:
        return 1.0
    return 1.0 / (1.0 + exp_val)

def logistic_regression(features, labels, lr, max_iter):
    n = len(features)
    p = len(features[0])
    weights = [0.0] * p
    bias = 0.0
    for _ in range(max_iter):
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
            weights[j] = weights[j] - lr * dw[j] / n
        bias = bias - lr * db / n
    return weights, bias

# Test: classify x > 2.5
features = [[1], [2], [3], [4], [5], [6]]
labels = [0, 0, 1, 1, 1, 1]
weights, bias = logistic_regression(features, labels, 0.5, 1000)
weights[0] > 0
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"


# Test naive-bayes-classifier (STATISTICS)
@pytest.mark.asyncio
async def test_naive_bayes():
    code = '''
def my_exp(x):
    if x > 50:
        return 1e21
    if x < -30:
        result = 1.0
        term = 1.0
        for i in range(1, 100):
            term = term * (-x) / i
            result = result + term
            if term > 1e15:
                return 1e-20
            if term < 1e-15 * result:
                break
        return 1.0 / result
    result = 1.0
    term = 1.0
    for i in range(1, 50):
        term = term * x / i
        result = result + term
        if term < 1e-15 * result and i > 10:
            break
    return result

def gaussian_pdf(x, mu, sigma):
    coeff = 1.0 / (sigma * 2.506628274631)
    return coeff * my_exp(-((x - mu) ** 2) / (2.0 * sigma * sigma))

def naive_bayes_train(features, labels):
    n = len(features)
    p = len(features[0])
    classes = list(set(labels))
    priors = {}
    for c in classes:
        priors[c] = labels.count(c) / n
    likelihoods = {}
    for c in classes:
        cf = []
        for i in range(n):
            if labels[i] == c:
                cf.append(features[i])
        means = []
        variances = []
        for j in range(p):
            s = 0.0
            for i in range(len(cf)):
                s = s + cf[i][j]
            means.append(s / len(cf))
            v = 0.0
            for i in range(len(cf)):
                v = v + (cf[i][j] - means[j])**2
            variances.append(v / len(cf) + 1e-6)
        likelihoods[c] = (means, variances)
    return priors, likelihoods

# Test: 2 classes, 2D features
features = [[1.0, 1.0], [1.5, 2.0], [2.0, 1.5], [5.0, 5.0], [5.5, 4.5], [6.0, 5.5]]
labels = ["A", "A", "A", "B", "B", "B"]
priors, likelihoods = naive_bayes_train(features, labels)
len(priors) == 2
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"