---
Domain: STATISTICS
Version: 1.0.0
Complexity: High
Type: Analysis
Category: Statistical Skills
Estimated Execution Time: 5-10 minutes
name: uncertainty-quantifier
Source: community
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