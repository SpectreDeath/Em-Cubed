---
name: assert_test_constraints
domain: STATISTICS
version: 1.0.0
surfaces:
  - prolog
  - python
description: Multi-surface hybrid guardrail engine enforcing measurement-level, sample-size, normality (Shapiro-Wilk / D'Agostino), and variance homogeneity (Levene) constraints before statistical test dispatch. Routes parametric vs non-parametric test families in Prolog and bundles numerical diagnostics in Python. Use when pre-screening datasets before hypothesis testing, validating parametric assumptions, or establishing audit trails for statistical test validity.
purpose: Gate statistical test execution through hierarchical symbolic (Prolog) and numerical (Python) pre-condition checks.
dependencies:
  - guardrails/validate_measurement_level
tags:
  - test-constraints
  - assumption-verification
  - normality-check
  - homoscedasticity-check
  - prolog-routing
  - python-guardrail
inputs:
  dataset_ref:
    type: string
    required: true
    description: Logical dataset identifier for logging and state isolation.
  columns:
    type: array
    required: true
    description: Column/variable names participating in the target test.
  intended_test:
    type: string
    required: true
    description: Target test identifier (e.g. 'independent_t', 'one_way_anova', 'mann_whitney_u').
  data:
    type: object
    required: true
    description: 'Dictionary mapping column names to numeric sample vectors `{"col": [float]}`.'
  independent:
    type: boolean
    required: false
    description: True if groups represent independent samples; False if paired/repeated measures.
outputs:
  constraint_bundle:
    type: object
    description: Bundle containing sample size n, normal flag, equal_variance flag, and measurement levels.
  routing_decision:
    type: string
    description: "allowed | blocked(reason)"
  recommended_alternative:
    type: string
    description: Non-parametric or robust fallback test if intended test is blocked.
---

# Assert Test Constraints Engine

`assert_test_constraints` enforces strict mathematical pre-conditions before statistical test execution. It combines **symbolic logic routing in Prolog** (Stevens' scale hierarchy, minimum sample thresholds, and test family classification) with **numerical diagnostic evaluation in Python** (effective sample size $N$, Shapiro-Wilk normality $p \ge 0.05$, and Levene homoscedasticity $p \ge 0.05$).

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Constraint Assertion Progression

```
[1. Vector Audit & Effective N] → [2. Normality & Homoscedasticity Check] → [3. Visual Brief] → [4. Checkpoint] → [5. Prolog Gate & Permission Emit]
```

### Stage 1: Vector Audit & Effective Sample Size ($N$)
1. Ingest column data dictionary and calculate complete-case row count $N_{\text{complete}}$ across target columns.
2. Verify that $N \ge \text{min\_n}(\text{intended\_test})$ (e.g. $N \ge 2$ for t-tests, $N \ge 3$ for ANOVA, $N \ge 5$ for Chi-Square).

> **Completion criterion**: Effective sample size $N$ quantified with missing rows filtered.

---

### Stage 2: Normality & Homoscedasticity Diagnostics (Python)
1. Evaluate normality on each group vector using Shapiro-Wilk (or D'Agostino skew/kurtosis fallback):
   $$\text{normal\_flag} = \text{True} \iff \forall c \in \text{Columns}, p_{\text{shapiro}}(c) \ge 0.05$$
2. Evaluate homoscedasticity across groups using Levene's test:
   $$\text{equal\_variance\_flag} = \text{True} \iff p_{\text{levene}}(\mathbf{x}_1, \dots, \mathbf{x}_k) \ge 0.05$$

> **Completion criterion**: Binary assumption flags `normal` and `equal_variance` evaluated.

---

### Stage 3: The Visual Brief
For borderline assumption tests or non-normal residuals, generate an interactive brief:
- **Location**: Write to `%TEMP%\test-constraints-brief-<timestamp>.html` (Windows) or `/tmp/test-constraints-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render Q-Q normality plots, group variance box plots, and Prolog decision tree audit checklist.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing parametric procedures:
1. If intended test is parametric (e.g., Student's t-test or ANOVA) and `normal == False`:
   - Halt parametric dispatch.
   - Redirect to non-parametric equivalent (e.g., Mann-Whitney U or Kruskal-Wallis).
2. If `equal_variance == False` for two-sample t-test:
   - Redirect to Welch's t-test.

> **Completion criterion**: Decision gate confirmed with fallback test mapped if blocked.

---

### Stage 5: Prolog Gating & Permission Emit
1. Pass constraint bundle into Prolog module `permitted_test/4`.
2. Emit final authorization status (`allowed` or `blocked(reason)`).

> **Completion criterion**: Authorization payload emitted with `constraint_bundle` and `routing_decision`.

---

## Surface References

### Python Diagnostic Surface

```python
import math
from typing import List, Dict, Any

def _clean(vec: List[float]) -> List[float]:
    return [v for v in vec if v is not None and not (isinstance(v, float) and math.isnan(v))]

def check_normality_shapiro(vec: List[float]) -> bool:
    clean = _clean(vec)
    if len(clean) < 3:
        return False
    try:
        from scipy.stats import shapiro
        _, p = shapiro(clean)
        return p >= 0.05
    except ImportError:
        # Fallback: check skewness and kurtosis
        n = len(clean)
        mean = sum(clean) / n
        var = sum((x - mean) ** 2 for x in clean) / (n - 1)
        if var == 0: return False
        std = math.sqrt(var)
        z = [(x - mean) / std for x in clean]
        skew = sum(x ** 3 for x in z) / n
        kurt = (sum(x ** 4 for x in z) / n) - 3.0
        return abs(skew) < 1.0 and abs(kurt) < 2.0

def assert_test_constraints(dataset_ref: str, columns: List[str], test: str, data: Dict[str, List[float]], independent: bool = True) -> Dict[str, Any]:
    col_vectors = [_clean(data.get(c, [])) for c in columns]
    n_complete = len(list(zip(*col_vectors)))
    
    is_normal = all(check_normality_shapiro(v) for v in col_vectors)
    
    # Check variance ratio
    vars_ = [sum((x - sum(v)/len(v))**2 for x in v) / (len(v)-1) for v in col_vectors if len(v) >= 2]
    eq_var = (max(vars_) / min(vars_) < 4.0) if (len(vars_) >= 2 and min(vars_) > 0) else True
    
    # Routing decision logic
    blocked_reason = None
    alt = None
    
    if test in {"independent_t", "one_way_anova"} and not is_normal:
        blocked_reason = "normality_violation"
        alt = "mann_whitney_u" if test == "independent_t" else "kruskal_wallis"
    elif n_complete < 3:
        blocked_reason = "insufficient_sample_size"
        alt = "exact_permutation_test"
        
    return {
        "constraint_bundle": {
            "dataset_ref": dataset_ref,
            "columns": columns,
            "n": n_complete,
            "independent": independent,
            "normal": is_normal,
            "equal_variance": eq_var
        },
        "routing_decision": "allowed" if not blocked_reason else f"blocked({blocked_reason})",
        "recommended_alternative": alt
    }
```

### Prolog Gating Surface

```prolog
permitted_test(Test, N, Normal, EqualVar, allowed) :-
    min_n(Test, MinN),
    N >= MinN,
    (requires_normality(Test) -> Normal == true ; true),
    (requires_homoscedasticity(Test) -> EqualVar == true ; true), !.

permitted_test(Test, N, _Normal, _EqualVar, blocked(insufficient_n)) :-
    min_n(Test, MinN), N < MinN, !.

permitted_test(Test, _N, false, _EqualVar, blocked(normality_violation)) :-
    requires_normality(Test), !.
```

---

## Anti-Patterns & Guardrails

- **Bypassing Normality Screening** — Running ANOVA on heavily skewed distributions ($p_{\text{shapiro}} < 0.001$), inflating Type I error rates.
- **Ignoring Unequal Variances** — Running standard Student's t-test when group variances differ by $> 4\times$ without switching to Welch's t-test.
- **Complete-Case Neglect** — Computing sample size per column independently in paired tests, resulting in misaligned paired observations.
