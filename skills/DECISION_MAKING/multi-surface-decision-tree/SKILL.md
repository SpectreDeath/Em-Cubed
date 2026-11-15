---
name: multi-surface-decision-tree
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
description: Multi-surface decision tree analysis and option evaluation engine supporting ensemble-based classification, Pareto optimality checking, and fuzzy heuristic aggregation. Evaluates logical constraint violations and Pareto dominance in Prolog ($\neg \exists b \succ a$), normalizes numerical criteria values in Python ($[0, 1]$ min-max scaling), and aggregates multi-attribute scores with triangular fuzzy membership functions in Hy. Use when analyzing multi-criteria options under uncertainty, extracting decision rules, or identifying Pareto-optimal alternatives.
purpose: Analyze decision trees, evaluate multi-criteria options, and filter Pareto-optimal choices across Python, Prolog, and Hy.
dependencies:
  - DECISION_MAKING/multi-criteria-weight-calculator
tags:
  - decision-tree
  - multi-surface
  - pareto-optimality
  - fuzzy-scoring
  - rule-extraction
  - prolog-constraints
inputs:
  options:
    type: array
    required: true
    description: 'List of candidate decision option dictionaries `[{''name'': ''A'', ''risk'': 5, ''return'': 10, ...}, ...]`.'
  criteria:
    type: array
    required: true
    description: List of criteria attribute keys to evaluate `['risk', 'return', 'liquidity']`.
  weights:
    type: object
    required: false
    description: 'Criteria weight mapping `{criterion_name: weight}` (default uniform weights).'
  constraints:
    type: array
    required: false
    description: 'List of threshold constraints `[{''criterion'': ''risk'', ''max'': 7}, ...]` for Prolog filtering.'
outputs:
  ranked_options:
    type: array
    description: Ranked list of decision options with normalized scores and confidence intervals.
  pareto_optimal_set:
    type: array
    description: Subset of candidate options that are non-dominated (Pareto optimal).
  constraint_violations:
    type: object
    description: Map of each option to any triggered constraint violation codes.
  top_recommendation:
    type: object
    description: Highest-scoring compliant candidate option.
---

# Multi-Surface Decision Tree Engine

`multi-surface-decision-tree` provides a comprehensive multi-criteria decision analysis framework. It evaluates **Pareto optimality and logical constraints in Prolog**, performs **tree traversal and numerical normalization in Python**, and aggregates **fuzzy uncertainty scores in Hy**:

$$\text{Score}(a) = \sum_{c \in \mathcal{C}} w_c \cdot v_c(a), \quad \text{ParetoOptimal}(a) \iff \neg \exists b \in \mathcal{O} \text{ s.t. } b \succ a$$

$$b \succ a \iff (\forall c \in \mathcal{C}, v_c(b) \ge v_c(a)) \land (\exists c \in \mathcal{C}, v_c(b) > v_c(a))$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Multi-Surface Decision Progression

```
[1. Option & Criteria Ingest] → [2. Prolog Constraint & Pareto Dominance Proof] → [3. Visual Brief] → [4. Checkpoint] → [5. Fuzzy Score Aggregation & Emit]
```

### Stage 1: Option & Criteria Ingest
1. Ingest `options` array, `criteria` keys, and optional `weights` dictionary.
2. Normalize criteria values into $[0, 1]$ interval via min-max scaling.

> **Completion criterion**: Clean candidate options and normalized criteria established.

---

### Stage 2: Prolog Constraint & Pareto Dominance Proof
1. Evaluate hard constraint rules in Prolog:
   ```prolog
   constraint_violation(Option, high_risk) :- option_risk(Option, Risk), Risk > 7.
   ```
2. Filter Pareto optimal options: identify options for which no other option achieves equal-or-better performance on all criteria and strictly better on at least one.

> **Completion criterion**: Pareto optimal subset and constraint violations determined.

---

### Stage 3: The Visual Brief
For multi-criteria option comparisons and Pareto frontiers, generate an interactive brief:
- **Location**: Write to `%TEMP%\decision-tree-brief-<timestamp>.html` (Windows) or `/tmp/decision-tree-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render decision tree branch hierarchy, 2D Pareto frontier scatter plot (Risk vs. Return), and multi-criteria score ranking table with violation badges.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing ranking:
1. Verify that weights sum to 1.0: $\sum w_c = 1.0 \pm 10^{-5}$.
2. Separate compliant options (zero constraint violations) from non-compliant alternatives.

> **Completion criterion**: Weight normalization and compliance partitioning verified.

---

### Stage 5: Fuzzy Score Aggregation & Output Emission
1. Calculate weighted composite scores and fuzzy confidence intervals in Hy/Python.
2. Rank compliant options descending by composite score.
3. Identify `top_recommendation`.
4. Emit complete `DecisionTreeResult` record.

> **Completion criterion**: Full decision tree recommendation payload emitted.

---

## Surface References

### Prolog Pareto Surface

```prolog
:- module(decision_tree_logic, [
    dominated_by/2,
    pareto_optimal/1,
    meets_constraints/1
]).

dominated_by(Opt1, Opt2) :-
    option_score(Opt1, risk, R1), option_score(Opt2, risk, R2),
    option_score(Opt1, return, Ret1), option_score(Opt2, return, Ret2),
    R1 >= R2, Ret1 =< Ret2,
    (R1 > R2 ; Ret1 < Ret2).

pareto_optimal(Opt) :-
    \+ (dominated_by(Opt, _)).
```

### Python Calculation Surface

```python
from typing import Dict, List, Any, Optional

def evaluate_decision_tree(
    options: List[Dict[str, Any]],
    criteria: List[str],
    weights: Optional[Dict[str, float]] = None,
    constraints: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    if not options:
        raise ValueError("empty_options: Requires at least 1 option.")
    if not criteria:
        raise ValueError("empty_criteria: Requires at least 1 criterion.")
        
    # Weight setup
    if weights is None:
        w_dict = {c: 1.0 / len(criteria) for c in criteria}
    else:
        tot = sum(weights.values())
        w_dict = {c: weights.get(c, 0.0) / (tot if tot > 0 else 1.0) for c in criteria}
        
    # Min-max normalization
    norm_options = []
    for opt in options:
        norm_opt = dict(opt)
        for c in criteria:
            vals = [o.get(c, 0.0) for o in options]
            min_v, max_v = min(vals), max(vals)
            rng = max_v - min_v if max_v != min_v else 1.0
            norm_opt[f"{c}_norm"] = (opt.get(c, 0.0) - min_v) / rng
        norm_options.append(norm_opt)
        
    # Constraint violations
    violations = {}
    for opt in options:
        v_list = []
        if constraints:
            for cons in constraints:
                c = cons.get("criterion")
                val = opt.get(c, 0.0)
                if "max" in cons and val > cons["max"]:
                    v_list.append(f"exceeds_max_{c}")
                if "min" in cons and val < cons["min"]:
                    v_list.append(f"below_min_{c}")
        violations[opt.get("name", "unnamed")] = v_list
        
    # Pareto dominance
    pareto_set = []
    for i, opt_a in enumerate(norm_options):
        dominated = False
        for j, opt_b in enumerate(norm_options):
            if i == j: continue
            # b dominates a if b >= a on all criteria and b > a on at least one
            ge_all = all(opt_b[f"{c}_norm"] >= opt_a[f"{c}_norm"] for c in criteria)
            gt_one = any(opt_b[f"{c}_norm"] > opt_a[f"{c}_norm"] for c in criteria)
            if ge_all and gt_one:
                dominated = True
                break
        if not dominated:
            pareto_set.append(opt_a.get("name", f"Option_{i}"))
            
    # Composite scoring
    ranked = []
    for opt in norm_options:
        score = sum(w_dict[c] * opt[f"{c}_norm"] for c in criteria)
        name = opt.get("name", "unnamed")
        ranked.append({
            "name": name,
            "score": round(score, 4),
            "is_pareto": name in pareto_set,
            "violations": violations.get(name, [])
        })
        
    ranked.sort(key=lambda x: x["score"], reverse=True)
    compliant = [o for o in ranked if not o["violations"]]
    top_rec = compliant[0] if compliant else (ranked[0] if ranked else None)
    
    return {
        "ranked_options": ranked,
        "pareto_optimal_set": pareto_set,
        "constraint_violations": violations,
        "top_recommendation": top_rec
    }
```

---

## Anti-Patterns & Guardrails

- **Recommending Non-Compliant Alternatives** — Selecting an option with the highest score despite violating hard constraints (e.g. risk $> 8$).
- **Confusing Directionality in Min-Max Scaling** — Treating cost/risk criteria as "higher is better" without inverting the normalization scale.
- **Ignoring Pareto Dominated Sub-Optimal Choices** — Favouring dominated options over strictly superior alternatives on all evaluation axes.
