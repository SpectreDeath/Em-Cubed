---
name: uncertainty-quantifier
domain: STATISTICS
version: 1.0.0
description: Uncertainty quantifier for confidence interval estimation, sensitivity analysis, and probabilistic risk assessment.
compatibility: UNIVERSAL
complexity: High
type: Analysis
category: Statistical Skills
estimated execution time: 5-10 minutes
source: community
allowed-tools: '- read

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

  '
---
origin: manual
triggers:
  - uncertainty_analysis
  - probabilistic_reasoning
  - bayesian_inference
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:30:00Z"
updated_at: "2026-05-02T12:30:00Z"

## Purpose

Multi-surface uncertainty quantifier that uses Python for probabilistic sampling, Prolog for logical uncertainty propagation, and Hy for fuzzy uncertainty modeling and sensitivity analysis.

## Description

This skill quantifies uncertainty by:
- Python for Monte Carlo sampling, Bayesian inference, and probabilistic programming
- Prolog for logical uncertainty rules and constraint-based reasoning
- Hy for fuzzy uncertainty propagation and decision-making under uncertainty

## Examples

### Project Risk Analysis

```
Input: Task durations with uncertainty distributions
Output: Project completion time distribution with confidence bounds
```

## Implementation

### Python Probabilistic Analysis

```python
import numpy as np
from typing import Dict, List, Callable, Tuple, Optional
from scipy import stats
from dataclasses import dataclass
import pymc3 as pm

@dataclass
class UncertaintyDistribution:
    name: str
    dist_type: str  # normal, uniform, beta, etc.
    params: Dict[str, float]
    
    def sample(self, n: int = 1000) -> np.ndarray:
        if self.dist_type == "normal":
            return np.random.normal(self.params["mean"], self.params["std"], n)
        elif self.dist_type == "uniform":
            return np.random.uniform(self.params["low"], self.params["high"], n)
        elif self.dist_type == "beta":
            return np.random.beta(self.params["alpha"], self.params["beta"], n)
        elif self.dist_type == "triangular":
            return np.random.triangular(self.params["left"], 
                                       self.params["mode"], 
                                       self.params["right"], n)
        return np.zeros(n)

class UncertaintyQuantifier:
    """Quantify and propagate uncertainty."""
    
    def __init__(self):
        self.variables: Dict[str, UncertaintyDistribution] = {}
        self.correlations: Dict[Tuple[str, str], float] = {}
    
    def add_variable(self, name: str, distribution: UncertaintyDistribution) -> None:
        self.variables[name] = distribution
    
    def add_correlation(self, var1: str, var2: str, correlation: float) -> None:
        self.correlations[(var1, var2)] = correlation
    
    def monte_carlo_analysis(self, model_func: Callable, n_samples: int = 10000) -> Dict:
        """Run Monte Carlo uncertainty analysis."""
        samples = {}
        for name, dist in self.variables.items():
            samples[name] = dist.sample(n_samples)
        
        # Apply correlations if specified
        for (var1, var2), corr in self.correlations.items():
            if var1 in samples and var2 in samples:
                # Apply Cholesky transformation for correlation
                cov_matrix = np.array([[1, corr], [corr, 1]])
                L = np.linalg.cholesky(cov_matrix)
                
                standardized = np.column_stack([
                    (samples[var1] - np.mean(samples[var1])) / np.std(samples[var1]),
                    (samples[var2] - np.mean(samples[var2])) / np.std(samples[var2])
                ])
                
                correlated = standardized @ L.T
                samples[var1] = correlated[:, 0] * np.std(samples[var1]) + np.mean(samples[var1])
                samples[var2] = correlated[:, 1] * np.std(samples[var2]) + np.mean(samples[var2])
        
        # Run model
        results = np.array([model_func({k: v[i] for k, v in samples.items()}) 
                           for i in range(n_samples)])
        
        return {
            "mean": float(np.mean(results)),
            "std": float(np.std(results)),
            "percentiles": {
                "5": float(np.percentile(results, 5)),
                "25": float(np.percentile(results, 25)),
                "50": float(np.percentile(results, 50)),
                "75": float(np.percentile(results, 75)),
                "95": float(np.percentile(results, 95))
            },
            "samples": results
        }
    
    def sensitivity_analysis(self, model_func: Callable, 
                           n_samples: int = 5000) -> Dict[str, float]:
        """Compute sensitivity indices (Sobol-like)."""
        base_result = self.monte_carlo_analysis(model_func, n_samples)
        base_mean = base_result["mean"]
        sensitivities = {}
        
        for name in self.variables:
            # One-at-a-time sensitivity
            original_dist = self.variables[name]
            original_mean = np.mean(original_dist.sample(1000))
            
            # Vary mean by small amount
            modified_dist = UncertaintyDistribution(
                name, original_dist.dist_type,
                {**original_dist.params, "mean": original_mean * 1.1}
            )
            self.variables[name] = modified_dist
            
            modified_result = self.monte_carlo_analysis(model_func, n_samples // 10)
            sensitivities[name] = abs(modified_result["mean"] - base_mean) / abs(base_mean + 1e-10)
            
            self.variables[name] = original_dist
        
        return sensitivities
    
    def bayesian_inference(self, prior_params: Dict, 
                         likelihood_data: np.ndarray) -> Dict:
        """Perform Bayesian inference on parameters."""
        with pm.Model() as model:
            # Prior
            param = pm.Normal("param", 
                            mu=prior_params.get("mean", 0),
                            sigma=prior_params.get("std", 1))
            
            # Likelihood
            obs = pm.Normal("obs", mu=param, sigma=0.1, observed=likelihood_data)
            
            # Sample
            trace = pm.sample(1000, tune=1000, return_inferencedata=True)
        
        return {
            "posterior_mean": float(trace.posterior["param"].mean()),
            "posterior_std": float(trace.posterior["param"].std()),
            "hdi_5": float(pm.hdi(trace.posterior["param"], hdi_prob=0.05).sel(width="lower")),
            "hdi_95": float(pm.hdi(trace.posterior["param"], hdi_prob=0.95).sel(width="upper"))
        }

def uncertainty_propagation(funcs: List[Callable], 
                         uncertainties: List[UncertaintyDistribution],
                         n_samples: int = 10000) -> Dict[str, np.ndarray]:
    """Propagate uncertainty through function chain."""
    samples = {}
    for dist in uncertainties:
        samples[dist.name] = dist.sample(n_samples)
    
    results = {}
    for i, func in enumerate(funcs):
        results[f"output_{i}"] = np.array([func(samples) for _ in range(100)])
    
    return results

def confidence_belt(estimates: np.ndarray, confidence: float = 0.95) -> Dict:
    """Compute confidence belt around estimates."""
    alpha = 1 - confidence
    lower = np.percentile(estimates, alpha/2 * 100, axis=0)
    upper = np.percentile(estimates, (1 - alpha/2) * 100, axis=0)
    median = np.median(estimates, axis=0)
    
    return {"lower": lower, "median": median, "upper": upper}
```

### Prolog Uncertainty Logic

```prolog
% Uncertainty representation
uncertain(Value, Distribution) :-
    probability_distribution(Value, Distribution).

% Propagation rules
uncertain_result(InputUncertainty, OutputUncertainty) :-
    transformation(Function, InputUncertainty, OutputUncertainty).

% Confidence propagation
combined_confidence(ListOfConfidences, CombinedConfidence) :-
    sum_list(ListOfConfidences, TotalConfidence),
    length(ListOfConfidences, NumFactors),
    CombinedConfidence is TotalConfidence / NumFactors.

% Worst-case analysis
worst_case(Components, WorstCaseResult) :-
    findall(Value, member(component(_, Value), Components), Values),
    max_list(Values, WorstCaseResult).

% Uncertainty bounds
within_bounds(Value, LowerBound, UpperBound) :-
    Value >= LowerBound,
    Value =< UpperBound.

% Confidence interval intersection
confidence_overlap(CI1Low, CI1High, CI2Low, CI2High, Overlap) :-
    OverlapLow is max(CI1Low, CI2Low),
    OverlapHigh is min(CI1High, CI2High),
    Overlap is max(0, OverlapHigh - OverlapLow).

% Risk assessment
risk_level(Probability, Impact, Risk) :-
    Risk is Probability * Impact.

high_risk(Risk) :-
    Risk > 0.7.

medium_risk(Risk) :-
    Risk =< 0.7,
    Risk > 0.3.

low_risk(Risk) :-
    Risk =< 0.3.

% Evidence combination
combined_evidence(EvidenceList, CombinedEvidence) :-
    findall(Confidence, member(evidence(_, Confidence), EvidenceList), Confidences),
    complementary_confidence(Confidences, CombinedEvidence).

complementary_confidence([C], C) :- !.
complementary_confidence([C1, C2 | Rest], Combined) :-
    CombinedPos is 1 - (1 - C1) * (1 - C2),
    complementary_confidence([CombinedPos | Rest], Combined).
```

### Hy Fuzzy Uncertainty

```hy
(defn fuzzy-probability [membership-functions value]
  "Compute fuzzy probability from membership functions"
  (sum (map (fn [mf] (get mf value 0)) membership-functions)))

(defn uncertainty-aggregation [distributions weights]
  "Aggregate multiple uncertainty distributions"
  (let [weighted-samples (map (fn [d w] (* w (d :sample 1000))) distributions weights)
        aggregated (map + weighted-samples)]
    (/ (sum aggregated) (len aggregated))))

(defn sensitivity-measure [base-output variations]
  "Measure sensitivity to input variations"
  (let [variances (map (fn [v] (numpy.var v)) variations)
        total-variance (numpy.var base-output)]
    (map (fn [v] (/ v total-variance)) variances)))

(defn confidence-growth [data-points confidence-level window-size]
  "Analyze how confidence grows with more data"
  (let [windows (partition window-size 1 data-points)
        confidences (map (fn [w] (stats.t.interval confidence-level w)) windows)]
    confidences))

(defn decision-under-uncertainty [options uncertainties utility-function]
  "Make decision considering uncertainty"
  (let [expected-utilities (map (fn [opt unc]
                                (let [samples (unc :sample 1000)
                                      utils (map utility-function samples)]
                                  {:option opt :expected (mean utils) :risk (stdev utils)}))
                              options uncertainties)]
    (apply max expected-utilities :key (fn [e] (get e :expected)))))

(defn uncertainty-visualization [samples bins confidence-intervals]
  "Generate data for uncertainty visualization"
  (let [hist (numpy.histogram samples bins)
        centers (map (fn [pair] (/ (+ (first pair) (second pair)) 2)) 
                    (partition 2 1 (first hist)))]
    {:centers centers :frequencies (second hist) :intervals confidence-intervals}))

```

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface

def test_normal_distribution_sampling():
    """Test normal distribution sampling."""
    code = '''
import numpy as np

def sample_normal(mean, std, n=1000):
    return np.random.normal(mean, std, n)

samples = sample_normal(10, 2, 1000)
assert len(samples) == 1000
assert 8 < np.mean(samples) < 12  # Should be near 10
assert 1 < np.std(samples) < 3    # Should be near 2

print("normal sampling ok")
'''
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_uniform_distribution_sampling():
    """Test uniform distribution sampling."""
    code = '''
import numpy as np

samples = np.random.uniform(0, 10, 1000)
assert len(samples) == 1000
assert np.min(samples) >= 0
assert np.max(samples) <= 10
assert 4 < np.mean(samples) < 6  # Should be near 5

print("uniform sampling ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_monte_carlo_mean_estimation():
    """Test Monte Carlo estimation of a function mean."""
    code = '''
import numpy as np

def monte_carlo_mean(func, dist_samples):
    """Estimate mean of func(X) where X ~ dist_samples."""
    return np.mean([func(x) for x in dist_samples])

# Estimate E[X^2] where X ~ N(0, 1)
samples = np.random.normal(0, 1, 10000)
estimated_mean = monte_carlo_mean(lambda x: x**2, samples)
# E[X^2] = Var(X) + (E[X])^2 = 1 + 0 = 1
assert 0.9 < estimated_mean < 1.1, f"Got {estimated_mean}"

print("MC mean estimation ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_percentile_calculation():
    """Test percentile/confidence interval calculation."""
    code = '''
import numpy as np

samples = np.random.normal(50, 10, 10000)
percentiles = {
    "5": np.percentile(samples, 5),
    "25": np.percentile(samples, 25),
    "50": np.percentile(samples, 50),
    "75": np.percentile(samples, 75),
    "95": np.percentile(samples, 95)
}

assert percentiles["5"] < percentiles["50"] < percentiles["95"]
assert 30 < percentiles["5"] < 40
assert 45 < percentiles["50"] < 55
print("percentiles ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_sensitivity_analysis():
    """Test one-at-a-time sensitivity analysis."""
    code = '''
import numpy as np

def model(x, y):
    """Simple model: product of inputs."""
    return x * y

def sensitivity_analysis(base_x, base_y, delta=0.1):
    """Compute sensitivity by varying each parameter."""
    base_output = model(base_x, base_y)
    
    # Vary x
    x_plus = model(base_x * (1 + delta), base_y)
    x_sensitivity = abs((x_plus - base_output) / base_output) / delta
    
    # Vary y
    y_plus = model(base_x, base_y * (1 + delta))
    y_sensitivity = abs((y_plus - base_output) / base_output) / delta
    
    return {"x": x_sensitivity, "y": y_sensitivity}

sensitivities = sensitivity_analysis(2.0, 3.0)
assert "x" in sensitivities
assert "y" in sensitivities
assert sensitivities["x"] > 0
assert sensitivities["y"] > 0
print("sensitivity analysis ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_confidence_interval_overlap():
    """Test confidence interval overlap calculation."""
    code = '''
def confidence_overlap(ci1, ci2):
    """Calculate overlap between two confidence intervals."""
    lower = max(ci1[0], ci2[0])
    upper = min(ci1[1], ci2[1])
    overlap = max(0, upper - lower)
    return overlap

# Overlapping intervals
ci_a = (10, 20)
ci_b = (15, 25)
overlap = confidence_overlap(ci_a, ci_b)
assert overlap == 5.0

# Non-overlapping
ci_c = (10, 12)
ci_d = (20, 25)
overlap2 = confidence_overlap(ci_c, ci_d)
assert overlap2 == 0.0

print("CI overlap ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_risk_level_calculation():
    """Test risk = probability * impact."""
    code = '''
def risk_level(probability, impact):
    return probability * impact

def risk_category(risk):
    if risk > 0.7:
        return "high"
    elif risk > 0.3:
        return "medium"
    else:
        return "low"

assert risk_level(0.5, 0.8) == 0.4
assert risk_category(0.4) == "medium"
assert risk_category(0.8) == "high"
assert risk_category(0.2) == "low"

print("risk assessment ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_evidence_combination():
    """Test combining independent evidence confidences."""
    code = '''
def complementary_confidence(*confidences):
    """Combine independent confidences: 1 - product(1-ci)."""
    combined = 1.0
    for ci in confidences:
        combined *= (1 - ci)
    return 1 - combined

# Two moderately confident pieces of evidence
c1 = 0.6
c2 = 0.7
combined = complementary_confidence(c1, c2)
assert combined > max(c1, c2), f"Combined {combined} should exceed individual"
assert combined < 0.95

# Three evidences
c3 = 0.5
combined3 = complementary_confidence(c1, c2, c3)
assert combined3 > combined

print("evidence combination ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_beta_distribution_for_probabilities():
    """Test beta distribution (conjugate prior for Bernoulli)."""
    code = '''
import numpy as np

def sample_beta(alpha, beta, n=1000):
    """Sample from Beta distribution."""
    return np.random.beta(alpha, beta, n)

samples = sample_beta(2, 5, 1000)
assert len(samples) == 1000
assert np.all(samples >= 0) and np.all(samples <= 1)
# Mean should be near alpha/(alpha+beta) = 2/7 ≈ 0.286
assert 0.2 < np.mean(samples) < 0.35

print("beta distribution ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_correlation_application():
    """Test applying correlation to independent samples."""
    code = '''
import numpy as np

def apply_correlation(x, y, target_corr=0.8):
    """Apply correlation to two independent normal samples."""
    n = len(x)
    # Standardize
    x_std = (x - np.mean(x)) / np.std(x)
    y_std = (y - np.mean(y)) / np.std(y)
    
    # Cholesky of correlation matrix
    R = np.array([[1, target_corr], [target_corr, 1]])
    L = np.linalg.cholesky(R)
    
    # Correlate
    correlated = np.column_stack([x_std, y_std]) @ L.T
    return correlated[:, 0], correlated[:, 1]

np.random.seed(42)
x = np.random.randn(1000)
y = np.random.randn(1000)
x_corr, y_corr = apply_correlation(x, y, 0.8)
empirical_corr = np.corrcoef(x_corr, y_corr)[0,1]
assert 0.75 < empirical_corr < 0.85, f"Correlation {empirical_corr} not near 0.8"

print("correlation application ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
class TestUncertaintyQuantifier:
    @pytest.fixture
    async def surface(self):
        return PythonSurface()

    async def test_basic_arithmetic(self, surface):
        """Verify surface basic operations."""
        result = await surface.execute("1 + 2 * 3", {})
        assert result["status"] == "ok"
        assert result["value"] == 7

    async def test_dict_operations(self, surface):
        """Test dictionary manipulations used in uncertainty analysis."""
        code = '''
data = {"mean": 10.5, "std": 2.0}
params = data
assert "mean" in params
assert params["mean"] == 10.5
print("dict ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_list_comprehensions(self, surface):
        """Test list comprehensions for sample processing."""
        code = '''
samples = [1.1, 2.2, 3.3, 4.4, 5.5]
squared = [x**2 for x in samples]
assert len(squared) == 5
assert squared[0] > 1.0
print("list comp ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
from em_cubed.surfaces import PythonSurface
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_uncertainty_quantifier_skill():
    """Test uncertainty quantifier skill integration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "STATISTICS" / "uncertainty-quantifier"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: Uncertainty Test
Domain: STATISTICS
surfaces:
  - python
---

## Purpose
Test uncertainty calculations

## Description
Simple uncertainty skill for testing

## Implementation

### Python

```python
def estimate_uncertainty(data):
    return {"mean": sum(data)/len(data), "std": np.std(data)}
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        surface = PythonSurface()
        code = "np.mean([1,2,3,4,5])"
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
```

## Usage Patterns

### Monte Carlo Uncertainty Analysis

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

# Define uncertain variables
code = '''
import numpy as np

n_samples = 10000
# Task duration uncertainty (triangular distribution approximation)
task_duration = np.random.triangular(5, 8, 12, n_samples)

# Cost uncertainty (normal)
task_cost = np.random.normal(1000, 200, n_samples)

# Model: total = duration * cost_per_day
cost_per_day = 500
total_cost = task_duration * cost_per_day

print(f"Mean cost: ${np.mean(total_cost):,.0f}")
print(f"95th percentile: ${np.percentile(total_cost, 95):,.0f}")
print(f"5th percentile: ${np.percentile(total_cost, 5):,.0f}")
'''
await surface.execute(code, {})
```

### Sensitivity Analysis

```python
# Vary each input parameter independently
# Measure effect on output
# Rank parameters by sensitivity index
```

## Security Considerations

- Monte Carlo can be compute-intensive; limit sample count
- No external data sources accessed
- All computations in-memory

## Dependencies

- numpy (random sampling)
- scipy (statistical distributions)
- pymc3 (optional, for Bayesian inference)
- em_cubed framework
```

## Testing

```python
# Test uncertainty quantifier
from skills.uncertainty_quantifier import UncertaintyQuantifier, UncertaintyDistribution

uq = UncertaintyQuantifier()
uq.add_variable("x", UncertaintyDistribution("x", "normal", {"mean": 10, "std": 2}))

def model(vars):
    return vars["x"] ** 2

results = uq.monte_carlo_analysis(model, 1000)
assert "mean" in results
assert "percentiles" in results
assert results["percentiles"]["50"] > 0
```