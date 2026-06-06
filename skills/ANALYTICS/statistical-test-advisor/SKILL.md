---
name: statistical-test-advisor
domain: ANALYTICS
version: "1.0.0"
surfaces: [python, prolog]
---

# Purpose
Statically evaluates data distributions and experiment characteristics to route workflows to the mathematically optimal statistical test.

# Description
Implements an infrastructure-safe algorithmic advisor modeled on the routing logic in LangGraph + SciPy: Building an AI That Reads Documentation and Makes Decisions. It passes structural data flags (e.g., sample size, variance equality, normality) into Prolog to enforce relational decision-tree constraints, and executes safe, fallback-aware numerical analysis within a sandboxed Python `asteval` layer.

## Prolog Surface

```prolog
% Relational routing tree to find the correct statistical test
% Enforces experiment parameter constraints cleanly without deep nested IF loops.

% Branch 1: Comparing Means between 2 Groups
route_test(2, true, true, 'Independent Two-Sample t-Test').
route_test(2, true, false, 'Mann-Whitney U Test').
route_test(2, false, true, 'Paired t-Test').
route_test(2, false, false, 'Wilcoxon Signed-Rank Test').

% Branch 2: Comparing Means between 3+ Groups (ANOVA vs Kruskal-Wallis)
route_test(Groups, true, true, 'One-Way ANOVA') :- Groups > 2.
route_test(Groups, true, false, 'Kruskal-Wallis H-Test') :- Groups > 2.

% Safety Fallback Gate
get_optimal_test(Groups, IsIndependent, IsNormal, RecommendedTest) :-
    route_test(Groups, IsIndependent, IsNormal, RecommendedTest), !.
get_optimal_test(_, _, _, 'Descriptive Bootstrapping Fallback').
```

## Python Surface

```python
def evaluate_and_advise(metrics, test_recommendation):
    # 1. Fallback safety logic checks using raw loops
    total_samples = 0
    for seq in metrics.get('samples', []):
        total_samples += len(seq)
        
    if total_samples < 8:
        return {
            "recommended_test": "Exact Permutation Test",
            "reasoning": "sample size too small for asymptotic approximations recommended by Prolog rule."
        }
        
    # 2. Return the structured validation payload
    return {
        "recommended_test": test_recommendation,
        "sample_count": total_samples,
        "execution_status": "ready_for_calculation"
    }

# Execute handler mapping the Prolog string recommendation into the context
evaluate_and_advise(data_metrics, prolog_recommended_test)
```