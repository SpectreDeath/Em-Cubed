---
name: builtin-occams-razor-evaluator
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
  - z3
description: Bayesian model comparison engine calculating global marginal likelihood ratios (Bayes Factor $B_{12}$) and Occam factors between competing architectures. Implements Jaynesian prior density dilution to penalize overparameterized models, verifies dimensional complexity axioms in Z3 SMT, and computes evidence ratios, log Bayes factors, and Jeffreys/Kass-Raftery confidence bands in Python. Use when selecting between competing models, evaluating polynomial vs. linear fits, or penalizing model complexity under Bayesian evidence principles.
purpose: Compare competing models using Bayes Factors and Occam prior dilution penalties with Z3 complexity verification.
dependencies:
  - guardrails/validate_measurement_level
  - nuisance-parameter-integrator
tags:
  - occams-razor
  - bayes-factor
  - model-selection
  - prior-dilution
  - marginal-likelihood
  - z3-smt
inputs:
  model_a:
    type: object
    required: true
    description: 'First model spec `{name: str, parameters: int, log_likelihood: float}`.'
  model_b:
    type: object
    required: true
    description: 'Second model spec `{name: str, parameters: int, log_likelihood: float}`.'
  n_observations:
    type: integer
    required: true
    description: Sample observation count $N$.
  prior_odds:
    type: number
    required: false
    description: Prior model odds $P(M_A) / P(M_B)$ (default 1.0).
outputs:
  bayes_factor:
    type: number
    description: Marginal likelihood ratio $B_{AB} = P(D \mid M_A) / P(D \mid M_B)$.
  log10_bayes_factor:
    type: number
    description: Base-10 log Bayes factor $\log_{10}(B_{AB})$.
  occam_penalty_ratio:
    type: number
    description: Ratio of prior volume shrinkage factors $\Omega_A / \Omega_B$.
  preferred_model:
    type: string
    description: Name of favored model based on posterior odds.
  evidence_strength:
    type: string
    description: Kass-Raftery evidence classification ('negligible', 'positive', 'strong', 'decisive').
---

# Built-in Occam's Razor Evaluator Engine

`builtin-occams-razor-evaluator` implements Jaynesian Bayesian model comparison, penalizing over-parameterized models through **prior volume dilution across parameter dimensions**. It validates **complexity axioms in Z3 SMT** and calculates exact **BIC / Bayes Factors ($B_{AB}$)** and evidence classifications in **Python**:

$$\text{BIC}_i = -2 \ln \hat{L}_i + k_i \ln N, \quad \ln B_{AB} \approx -\frac{1}{2}(\text{BIC}_A - \text{BIC}_B)$$

$$\text{Occam Factor: } \Omega_i = \frac{\Delta \theta_i^{\text{posterior}}}{\Delta \theta_i^{\text{prior}}} \approx \frac{1}{\sqrt{N}^{k_i}}, \quad B_{AB} = \frac{\hat{L}_A}{\hat{L}_B} \cdot \frac{\Omega_A}{\Omega_B}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Occam Evaluator Progression

```
[1. Model Specification Audit] → [2. Z3 SMT Complexity Axiom Verification] → [3. Visual Brief] → [4. Checkpoint] → [5. Bayes Factor & Evidence Emit]
```

### Stage 1: Model Specification Audit
1. Ingest model descriptors `model_a` and `model_b` with parameter counts $k_A, k_B \ge 1$.
2. Ingest sample size $N$ and log-likelihood values $\ln L_A, \ln L_B$.

> **Completion criterion**: Clean model specifications verified ($N \ge 3, k_i \ge 1$).

---

### Stage 2: Z3 SMT Complexity Axiom Verification
1. Assert complexity axioms in Z3:
   - $k_A > 0 \land k_B > 0$
   - $\text{PriorVolume}_i = (1.0 / k_i)$
2. Execute Z3 check to ensure non-degenerate parameter spaces.

> **Completion criterion**: Z3 solver returns `sat` confirming valid parameter dimensionality.

---

### Stage 3: The Visual Brief
For model selection and architecture comparisons, generate an interactive brief:
- **Location**: Write to `%TEMP%\occams-razor-brief-<timestamp>.html` (Windows) or `/tmp/occams-razor-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render log-likelihood vs parameter complexity trade-off chart, BIC decomposition bars, and Bayes Factor evidence strength meter.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing model selection:
1. Inspect BIC difference $\Delta \text{BIC} = \text{BIC}_B - \text{BIC}_A$.
2. If $|\Delta \text{BIC}| < 2.0$, mark evidence as "negligible" (models are indistinguishable given the data).

> **Completion criterion**: Evidence resolution threshold evaluated.

---

### Stage 5: Bayes Factor & Evidence Strength Emission
1. Calculate $\text{BIC}_A, \text{BIC}_B$, approximate Bayes Factor $B_{AB}$, and $\log_{10}(B_{AB})$.
2. Classify evidence according to Kass & Raftery (1995):
   - $2 \ln B_{AB} < 2 \implies \text{"negligible"}$
   - $2 \le 2 \ln B_{AB} < 6 \implies \text{"positive"}$
   - $6 \le 2 \ln B_{AB} < 10 \implies \text{"strong"}$
   - $2 \ln B_{AB} \ge 10 \implies \text{"decisive"}$
3. Determine `preferred_model` and emit complete `OccamComparisonResult` record.

> **Completion criterion**: Full model selection record emitted with Bayes factor and Occam penalties.

---

## Surface References

### Z3 Complexity Surface

```python
from z3 import Solver, Real, sat

def verify_occam_axioms(param_a: int, param_b: int) -> bool:
    s = Solver()
    k_a = Real('k_a')
    k_b = Real('k_b')
    vol_a = Real('vol_a')
    vol_b = Real('vol_b')
    
    s.add(k_a == param_a)
    s.add(k_b == param_b)
    s.add(k_a > 0, k_b > 0)
    s.add(vol_a == 1.0 / k_a)
    s.add(vol_b == 1.0 / k_b)
    
    return s.check() == sat
```

### Python Calculation Surface

```python
import math
from typing import Dict, Any

def compare_models_occam(model_a: Dict[str, Any], model_b: Dict[str, Any], n_observations: int, prior_odds: float = 1.0) -> Dict[str, Any]:
    kA = int(model_a.get("parameters", 1))
    kB = int(model_b.get("parameters", 1))
    log_l_a = float(model_a.get("log_likelihood", 0.0))
    log_l_b = float(model_b.get("log_likelihood", 0.0))
    N = int(n_observations)
    
    if N < 3 or kA < 1 or kB < 1:
        raise ValueError("invalid_model_spec: Requires N >= 3 and parameters >= 1.")
        
    # BIC calculation
    bic_a = -2.0 * log_l_a + kA * math.log(N)
    bic_b = -2.0 * log_l_b + kB * math.log(N)
    delta_bic = bic_b - bic_a # positive favors model A
    
    # Bayes Factor approximation: B_AB = exp(0.5 * delta_bic)
    log_b_ab = 0.5 * delta_bic
    bayes_factor = math.exp(min(500.0, max(-500.0, log_b_ab)))
    log10_bf = log_b_ab / math.log(10.0)
    
    # Occam factor ratio
    occam_ratio = math.pow(N, (kB - kA) / 2.0)
    
    # Kass & Raftery (1995) 2 * ln(B_AB) scale
    two_ln_bf = 2.0 * log_b_ab
    abs_two_ln = abs(two_ln_bf)
    if abs_two_ln < 2.0:
        strength = "negligible"
    elif abs_two_ln < 6.0:
        strength = "positive"
    elif abs_two_ln < 10.0:
        strength = "strong"
    else:
        strength = "decisive"
        
    favored = model_a.get("name", "model_a") if log_b_ab >= 0 else model_b.get("name", "model_b")
    
    return {
        "model_a": model_a.get("name", "model_a"),
        "model_b": model_b.get("name", "model_b"),
        "bic_a": round(bic_a, 4),
        "bic_b": round(bic_b, 4),
        "delta_bic": round(delta_bic, 4),
        "bayes_factor": round(bayes_factor, 6),
        "log10_bayes_factor": round(log10_bf, 4),
        "occam_penalty_ratio": round(occam_ratio, 4),
        "preferred_model": favored,
        "evidence_strength": strength
    }
```

---

## Anti-Patterns & Guardrails

- **Comparing Models Without Complexity Penalties** — Comparing unpenalized raw likelihoods $\hat{L}_A$ vs $\hat{L}_B$, guaranteeing selection of over-fitted, higher-parameter models.
- **Applying BIC on Micro-Samples ($N < 5$)** — Using asymptotic BIC approximations on samples smaller than parameter counts ($N \le k$).
- **Asserting Decisive Evidence for $\Delta \text{BIC} < 2$** — Selecting a model as "significantly superior" when Bayes Factor is within random sampling noise.
