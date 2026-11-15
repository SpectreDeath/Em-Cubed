---
name: statistical-test-advisor
domain: ANALYTICS
version: 1.0.0
surfaces:
  - python
  - prolog
description: Multi-surface statistical test advisor and experiment routing engine. Evaluates experimental design characteristics (group count, sample independence, normality, variance equality) in Prolog relational decision trees, and enforces small-sample asymptotic safety fallbacks (e.g. Exact Permutation / Bootstrapping) in Python. Use when routing empirical datasets to mathematically optimal statistical hypothesis tests, avoiding parametric test assumption violations, or choosing between ANOVA, t-tests, Mann-Whitney, and Kruskal-Wallis.
purpose: Route empirical experiment datasets to mathematically optimal statistical hypothesis tests using Prolog relational decision trees and Python sample size fallbacks.
dependencies: []
tags:
  - statistical-tests
  - hypothesis-testing
  - decision-tree
  - prolog-routing
  - parametric-assumptions
  - normality-check
inputs:
  groups_count:
    type: integer
    required: true
    description: Number of experimental comparison groups ($k \ge 1$).
  is_independent:
    type: boolean
    required: true
    description: True if groups represent independent samples; False if paired/repeated measures.
  is_normal:
    type: boolean
    required: true
    description: True if sample residuals satisfy normality assumptions (e.g. Shapiro-Wilk $p > 0.05$).
  sample_sizes:
    type: array
    required: true
    description: Array of sample size counts per group `[n_1, n_2, ...]`.
outputs:
  recommended_test:
    type: string
    description: Optimal statistical test name (e.g. 'Independent Two-Sample t-Test', 'One-Way ANOVA', 'Mann-Whitney U Test').
  test_category:
    type: string
    description: "PARAMETRIC | NON_PARAMETRIC | EXACT_PERMUTATION | BOOTSTRAP"
  routing_rationale:
    type: string
    description: Logical explanation of the decision tree path and assumption checks.
  execution_status:
    type: string
    description: "ready_for_calculation | sample_too_small_fallback"
---

# Statistical Test Advisor Engine

`statistical-test-advisor` statically evaluates empirical dataset characteristics and experiment design constraints to route workflows to the mathematically optimal statistical hypothesis test. It enforces clean relational decision trees in Prolog, applying sample size safety gates in Python to prevent improper parametric asymptotic approximations on micro-samples ($N < 8$).

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Test Routing Progression

```
[1. Experiment Invariant Audit] → [2. Prolog Relational Decision Tree] → [3. Visual Brief] → [4. Checkpoint] → [5. Sample Size Gating & Emit]
```

### Stage 1: Experiment Design & Metric Invariant Audit
1. Ingest `groups_count` ($k \ge 1$), `is_independent`, `is_normal`, and `sample_sizes`.
2. Validate that $\text{len}(\text{sample\_sizes}) = k$ and all $n_i > 0$.

> **Completion criterion**: Experiment parameters validated with matching group counts and positive sample sizes.

---

### Stage 2: Prolog Relational Decision-Tree Test Selection
1. Evaluate relational routing rules in Prolog:
   - **2 Groups, Independent, Normal**: *Independent Two-Sample t-Test*
   - **2 Groups, Independent, Non-Normal**: *Mann-Whitney U Test*
   - **2 Groups, Paired, Normal**: *Paired t-Test*
   - **2 Groups, Paired, Non-Normal**: *Wilcoxon Signed-Rank Test*
   - **3+ Groups, Independent, Normal**: *One-Way ANOVA*
   - **3+ Groups, Independent, Non-Normal**: *Kruskal-Wallis H-Test*

> **Completion criterion**: Base candidate test selected from Prolog relational tree.

---

### Stage 3: The Visual Brief
For complex multi-group experiment designs, generate an interactive routing brief:
- **Location**: Write to `%TEMP%\stat-advisor-brief-<timestamp>.html` (Windows) or `/tmp/stat-advisor-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render decision tree flow chart highlighting the active traversal path and test category badge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing recommended test:
1. Calculate total sample size $N_{\text{total}} = \sum n_i$.
2. If $N_{\text{total}} < 8$, intercept asymptotic approximations and redirect to **Exact Permutation Test** or **Descriptive Bootstrapping**.

> **Completion criterion**: Asymptotic sample size sufficiency verified ($N \ge 8$).

---

### Stage 5: Test Specification & Dispatch Preparation
1. Compile final recommendation payload with test category and mathematical rationale.
2. Emit structured recommendation ready for downstream SciPy execution.

> **Completion criterion**: Output emitted with `recommended_test` and `execution_status: "ready_for_calculation"`.

---

## Surface References

### Python Diagnostic Surface

```python
from typing import List, Dict, Any

def advise_statistical_test(groups: int, independent: bool, normal: bool, sample_sizes: List[int]) -> Dict[str, Any]:
    total_n = sum(sample_sizes)
    
    # 1. Micro-sample safety fallback
    if total_n < 8:
        return {
            "recommended_test": "Exact Permutation Test",
            "test_category": "EXACT_PERMUTATION",
            "routing_rationale": "Total sample size (N < 8) is too small for asymptotic distribution approximations.",
            "execution_status": "sample_too_small_fallback"
        }
        
    # 2. Relational decision mapping
    if groups == 2:
        if independent:
            test = "Independent Two-Sample t-Test" if normal else "Mann-Whitney U Test"
        else:
            test = "Paired t-Test" if normal else "Wilcoxon Signed-Rank Test"
    elif groups > 2:
        test = "One-Way ANOVA" if (independent and normal) else "Kruskal-Wallis H-Test"
    else:
        test = "One-Sample t-Test" if normal else "Wilcoxon Signed-Rank Test"
        
    category = "PARAMETRIC" if normal else "NON_PARAMETRIC"
    
    return {
        "recommended_test": test,
        "test_category": category,
        "routing_rationale": f"Routed based on {groups} groups, independent={independent}, normal={normal}, N={total_n}.",
        "execution_status": "ready_for_calculation"
    }
```

### Prolog Decision Tree Surface

```prolog
% Branch 1: Comparing 2 Groups
route_test(2, true, true, 'Independent Two-Sample t-Test').
route_test(2, true, false, 'Mann-Whitney U Test').
route_test(2, false, true, 'Paired t-Test').
route_test(2, false, false, 'Wilcoxon Signed-Rank Test').

% Branch 2: Comparing 3+ Groups
route_test(Groups, true, true, 'One-Way ANOVA') :- Groups > 2.
route_test(Groups, true, false, 'Kruskal-Wallis H-Test') :- Groups > 2.

% Fallback Gate
get_optimal_test(Groups, IsIndependent, IsNormal, RecommendedTest) :-
    route_test(Groups, IsIndependent, IsNormal, RecommendedTest), !.
get_optimal_test(_, _, _, 'Descriptive Bootstrapping Fallback').
```

---

## Anti-Patterns & Guardrails

- **Parametric Overconfidence on Micro-Samples** — Recommending Student's t-test or ANOVA on sample sizes $N < 8$ where normality cannot be reliably established.
- **Ignoring Sample Pairing** — Applying independent two-sample tests to paired pre/post measurements, discarding statistical power.
- **Parametric Testing Under Extreme Skew** — Routing to ANOVA despite strong non-normality ($p < 0.001$).