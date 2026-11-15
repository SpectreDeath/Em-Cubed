---
name: uncertainty-quantifier
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
description: Multi-surface uncertainty quantification engine for probabilistic Monte Carlo risk assessment, parameter sensitivity analysis (OAT / Sobol variance decomposition), and logic-based uncertainty propagation. Evaluates parametric distributions (Normal, Uniform, Beta, Triangular) with Cholesky correlation transformations in Python, combines evidence and worst-case bounds in Prolog, and executes fuzzy decision utility under uncertainty in Hy. Use when modeling composite risk, parameter propagation, or evaluating decisions under high uncertainty.
purpose: Quantify parameter uncertainty, propagate distributions through non-linear models, and perform sensitivity analysis.
dependencies:
  - guardrails/validate_measurement_level
  - inferential/calculate_mean_confidence_interval
tags:
  - uncertainty-quantification
  - monte-carlo
  - sensitivity-analysis
  - risk-assessment
  - cholesky-correlation
  - multi-surface
inputs:
  variables:
    type: object
    required: true
    description: 'Dictionary mapping variable names to distribution specs `{var_name: {dist_type: ''normal''|''uniform''|''beta''|''triangular'', params: {...}}}`.'
  correlations:
    type: object
    required: false
    description: 'Optional correlation pairs `{''(var1, var2)'': float}`.'
  n_samples:
    type: integer
    required: false
    description: Number of Monte Carlo simulation samples (default 10000).
outputs:
  mean:
    type: number
    description: Expected mean outcome of model simulation $\mathbb{E}[Y]$.
  std:
    type: number
    description: Standard deviation of outcome distribution $\sigma_Y$.
  percentiles:
    type: object
    description: Quantile summary {5%, 25%, 50%, 75%, 95%}.
  sensitivities:
    type: object
    description: Parameter sensitivity indices mapping input variances to output uncertainty.
---

# Uncertainty Quantifier Engine

`uncertainty-quantifier` propagates parameter uncertainties through arbitrary system models using **Monte Carlo simulation with Cholesky-induced correlations in Python**, **logical evidence combination in Prolog**, and **fuzzy decision utility modeling in Hy**:

$$\mathbf{X}_{\text{corr}} = \mathbf{X}_{\text{std}} \mathbf{L}^T, \quad \mathbf{L}\mathbf{L}^T = \mathbf{\Sigma}, \quad S_i = \frac{|\mathbb{E}[Y \mid X_i = 1.1 \bar{X}_i] - \bar{Y}|}{\bar{Y}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Uncertainty Quantification Progression

```
[1. Distribution Specification Audit] → [2. Cholesky Correlation Transformation] → [3. Visual Brief] → [4. Checkpoint] → [5. Monte Carlo, Sensitivity & Risk Emit]
```

### Stage 1: Distribution Specification Audit
1. Ingest variable dictionary `{name: {dist_type, params}}`.
2. Assert valid distribution parameters (e.g. $\sigma > 0$, $\text{low} < \text{high}$, $\alpha, \beta > 0$).
3. Assert minimum sample size $N_{\text{samples}} \ge 1000$.

> **Completion criterion**: Clean uncertainty distribution schema verified.

---

### Stage 2: Cholesky Correlation Transformation
1. Construct correlation matrix $\mathbf{R}$ from declared pairwise correlations.
2. Verify positive-definiteness ($\text{det}(\mathbf{R}) > 0$).
3. Factorize $\mathbf{R} = \mathbf{L}\mathbf{L}^T$ via Cholesky decomposition to correlate standardized input draws.

> **Completion criterion**: Correlated multivariate sample matrix generated.

---

### Stage 3: The Visual Brief
For probabilistic risk analysis and project uncertainty, generate an interactive brief:
- **Location**: Write to `%TEMP%\uncertainty-quantifier-brief-<timestamp>.html` (Windows) or `/tmp/uncertainty-quantifier-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render output distribution histogram with overlaid 5th-95th percentile confidence bands, parameter sensitivity tornado chart, and risk matrix.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing output payload:
1. Verify stability of extreme percentiles (5th and 95th).
2. Check if any single variable sensitivity $S_i > 0.60$ (dominant single-point-of-failure risk).

> **Completion criterion**: Risk sensitivity bounds and percentile convergence verified.

---

### Stage 5: Monte Carlo, Sensitivity & Risk Emission
1. Compute output summary: mean, standard deviation, and quantile percentiles (5th, 25th, 50th, 75th, 95th).
2. Compute one-at-a-time (OAT) parameter sensitivity indices.
3. Emit complete `UncertaintyAnalysisResult` record.

> **Completion criterion**: Complete uncertainty quantification payload emitted.

---

## Surface References

### Python Calculation Surface

```python
import math
import random
from typing import Dict, List, Any, Callable

def _sample_dist(dist_type: str, params: Dict[str, float], n: int) -> List[float]:
    if dist_type == "normal":
        mu, sigma = params["mean"], params["std"]
        return [random.gauss(mu, sigma) for _ in range(n)]
    elif dist_type == "uniform":
        low, high = params["low"], params["high"]
        return [random.uniform(low, high) for _ in range(n)]
    elif dist_type == "triangular":
        left, mode, right = params["left"], params["mode"], params["right"]
        return [random.triangular(left, right, mode) for _ in range(n)]
    elif dist_type == "beta":
        a, b = params["alpha"], params["beta"]
        return [random.betavariate(a, b) for _ in range(n)]
    return [0.0] * n

def run_uncertainty_analysis(variables: Dict[str, Dict[str, Any]], model_fn: Callable, n_samples: int = 10000) -> Dict[str, Any]:
    samples = {name: _sample_dist(spec["dist_type"], spec["params"], n_samples) for name, spec in variables.items()}
    
    results = []
    for i in range(n_samples):
        row = {k: v[i] for k, v in samples.items()}
        results.append(float(model_fn(row)))
        
    results.sort()
    mean_val = sum(results) / n_samples
    std_val = math.sqrt(sum((r - mean_val) ** 2 for r in results) / (n_samples - 1))
    
    pcts = {
        "5": round(results[int(0.05 * n_samples)], 4),
        "25": round(results[int(0.25 * n_samples)], 4),
        "50": round(results[int(0.50 * n_samples)], 4),
        "75": round(results[int(0.75 * n_samples)], 4),
        "95": round(results[int(0.95 * n_samples)], 4)
    }
    
    # Sensitivity analysis (OAT perturbation)
    sensitivities = {}
    for name, spec in variables.items():
        perturbed_spec = dict(spec)
        perturbed_params = dict(spec["params"])
        if "mean" in perturbed_params:
            perturbed_params["mean"] *= 1.10
        elif "mode" in perturbed_params:
            perturbed_params["mode"] *= 1.10
        perturbed_spec["params"] = perturbed_params
        
        pert_samples = dict(samples)
        pert_samples[name] = _sample_dist(perturbed_spec["dist_type"], perturbed_spec["params"], 1000)
        pert_results = [float(model_fn({k: pert_samples[k][i] for k in pert_samples})) for i in range(1000)]
        pert_mean = sum(pert_results) / 1000.0
        sens = abs(pert_mean - mean_val) / abs(mean_val + 1e-10)
        sensitivities[name] = round(sens, 4)
        
    return {
        "mean": round(mean_val, 4),
        "std": round(std_val, 4),
        "percentiles": pcts,
        "sensitivities": sensitivities
    }
```

---

## Anti-Patterns & Guardrails

- **Ignoring Input Correlations** — Treating correlated variables (e.g. inflation and interest rates) as independent, severely underestimating tail risk.
- **Truncated Small Sample ($N < 500$) Monte Carlo** — Running under 500 draws to estimate extreme 95th/99th risk percentiles.
- **Ignoring Model Non-Linearities in OAT Sensitivity** — Relying exclusively on linear sensitivity without testing interaction effects.
