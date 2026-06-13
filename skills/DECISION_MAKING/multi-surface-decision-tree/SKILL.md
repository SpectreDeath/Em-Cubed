---
Domain: DECISION_MAKING
Version: 1.0.0
Complexity: High
Type: Process
Category: Cognitive Skills
Estimated Execution Time: 2-5 minutes
name: multi-surface-decision-tree
Source: community
description: Multi-surface decision tree supporting ensemble-based classification and rule extraction across Python, Prolog, and Hy surfaces.
compatibility: UNIVERSAL
allowed-tools: |
  - read
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
---
origin: manual
triggers:
  - decision_support
  - problem_solving
  - multi_criteria_analysis
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T09:53:00Z"
updated_at: "2026-05-02T09:53:00Z"

## Purpose

Multi-surface decision tree analyzer that combines Python for data processing, Prolog for logical inference, and Hy for fuzzy decision scoring across complex criteria.

## Description

This skill provides a comprehensive decision-making framework:
- Python for tree traversal, data normalization, and numerical calculations
- Prolog for logical rule evaluation and constraint satisfaction checking
- Hy for fuzzy scoring and weighted heuristic aggregation

The skill handles multi-criteria decision scenarios with uncertainty and complex dependencies.

## Examples

### Investment Portfolio Decision

```
Input: Portfolio options with risk, return, and liquidity criteria
Output: Ranked options with confidence scores and constraint violations
```

## Implementation

### Python Tree Traversal

```python
import math
from typing import Dict, List, Any

def build_decision_tree(options: List[Dict], criteria: List[str]) -> Dict:
    """Build and traverse decision tree with weighted scoring."""
    
    def calculate_weighted_score(option: Dict, weights: Dict[str, float]) -> float:
        """Calculate weighted score across all criteria."""
        total = 0.0
        for criterion, weight in weights.items():
            value = option.get(criterion, 0)
            normalized = normalize_value(value, criterion)
            total += normalized * weight
        return total
    
    def normalize_value(value: float, criterion: str) -> float:
        """Normalize values to 0-1 scale."""
        # Implementation varies by criterion type
        if criterion == "risk":
            return 1.0 - min(value / 10.0, 1.0)  # Lower risk is better
        elif criterion == "return":
            return min(value / 20.0, 1.0)  # Higher return is better
        elif criterion == "liquidity":
            return min(value / 100.0, 1.0)  # Higher liquidity is better
        return value
    
    def traverse(node: Dict, path: List = None) -> Dict:
        """Recursive tree traversal with scoring."""
        if path is None:
            path = []
        
        if "children" not in node:
            # Leaf node - calculate final score
            return {
                "path": path,
                "option": node.get("option"),
                "score": node.get("score", 0)
            }
        
        results = []
        for child in node.get("children", []):
            new_path = path + [child.get("decision")]
            results.append(traverse(child, new_path))
        
        return {"branches": results}
    
    return calculate_weighted_score

def normalize_criteria(options: List[Dict]) -> List[Dict]:
    """Normalize all criteria values across options."""
    all_keys = set()
    for opt in options:
        all_keys.update(opt.keys())
    
    numeric_keys = [k for k in all_keys if any(isinstance(v, (int, float)) for v in [opt.get(k) for opt in options])]
    
    for key in numeric_keys:
        values = [opt.get(key, 0) for opt in options]
        min_val, max_val = min(values), max(values)
        range_val = max_val - min_val if max_val != min_val else 1
        
        for opt in options:
            opt[f"{key}_normalized"] = (opt.get(key, 0) - min_val) / range_val
    
    return options
```

### Prolog Logical Inference

```prolog
% Decision constraint rules
valid_decision(Option) :-
    option_risk(Option, Risk),
    option_return(Option, Return),
    option_liquidity(Option, Liquidity),
    Risk =< 7,           % Risk threshold
    Return >= 5,         % Minimum return
    Liquidity >= 20.     % Minimum liquidity

% Constraint violation detection
constraint_violation(Option, high_risk) :-
    option_risk(Option, Risk),
    Risk > 8.

constraint_violation(Option, low_return) :-
    option_return(Option, Return),
    Return < 3.

constraint_violation(Option, illiquid) :-
    option_liquidity(Option, Liquidity),
    Liquidity < 10.

% Multi-criteria satisfaction
meets_all_criteria(Option) :-
    \+ constraint_violation(Option, _).

% Dominance relationships
dominated_by(Option1, Option2) :-
    option_risk(Option1, Risk1),
    option_risk(Option2, Risk2),
    option_return(Option1, Ret1),
    option_return(Option2, Ret2),
    Risk1 >= Risk2, Ret1 =< Ret2,
    (Risk1 > Risk2 ; Ret1 < Ret2).

pareto_optimal(Option) :-
    \+ (dominated_by(Option, Other)).
```

### Hy Fuzzy Scoring

```hy
(defn fuzzy-and [a b]
  "Fuzzy AND operation using minimum"
  (min a b))

(defn fuzzy-or [a b]
  "Fuzzy OR operation using maximum"
  (max a b))

(defn fuzzy-not [a]
  "Fuzzy NOT operation"
  (- 1 a))

(defn triangular-membership [x a b c]
  "Triangular membership function"
  (cond
    (<= x a) 0
    (<= x b) (/ (- x a) (- b a))
    (<= x c) (/ (- c x) (- c b))
    True 0))

(defn score-with-uncertainty [base-score uncertainty-factor]
  "Adjust score based on uncertainty"
  (* base-score (- 1 uncertainty-factor)))

(defn multi-criteria-aggregation [scores weights]
  "Aggregate scores with fuzzy weights"
  (/ (sum (list (* s w) (for [s scores w weights])))
     (sum weights)))

(defn confidence-interval [score samples]
  "Calculate confidence interval for decision"
  (let [std-dev (sqrt (/ (sum (list ** (- x score) 2) (for [x samples])) (len samples)))
        margin (* 1.96 (/ std-dev (sqrt (len samples))))]
    {:lower (- score margin) :upper (+ score margin) :confidence (* 100 (- 1 (/ margin score)))}))
```

## Testing

> **Note:** These tests use direct imports for standalone illustration. In production, use the `SkillExecutor` which injects surface plugins via `context["surfaces"]`. See [Multi-Surface Guide](../../docs/MULTI_SURFACE_GUIDE.md) for the recommended pattern.

### Python Tree Test

```python
# Test Python tree operations (standalone)
from skills.multi_surface_decision_tree import build_decision_tree, normalize_criteria

options = [
    {"risk": 5, "return": 10, "liquidity": 50, "name": "Option A"},
    {"risk": 3, "return": 8, "liquidity": 80, "name": "Option B"},
]

normalized = normalize_criteria(options)
assert len(normalized) == 2
```

### Multi-Surface Integration Test (Recommended Pattern)

```python
# Production pattern: use SkillExecutor with context injection
from em_cubed.skills.executor import SkillExecutor, SkillExecutionRequest

executor = SkillExecutor(plugin_manager, registry, skills_dir)
request = SkillExecutionRequest(
    skill_id="DECISION_MAKING/multi-surface-decision-tree",
    input_data={
        "options": [
            {"risk": 5, "return": 10, "liquidity": 50},
            {"risk": 3, "return": 8, "liquidity": 80}
        ],
        "criteria": ["risk", "return", "liquidity"],
        "weights": {"risk": 0.4, "return": 0.4, "liquidity": 0.2}
    }
)
result = await executor.execute(request)
assert result.success
```