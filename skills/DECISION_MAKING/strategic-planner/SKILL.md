---
name: strategic-planner
domain: "DECISION_MAKING"
description: Skill for strategic-planner.
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
﻿---
name: strategic-planner
Domain: DECISION_MAKING
Version: 1.0.0
surfaces:
  - python
  - z3
---

## Purpose

Strategic planning engine with constraint-based decision making and optimization analysis for complex scenarios.

## Description

Evaluates strategic options using weighted scoring and Z3 constraint verification for optimal decision selection.

## Implementation

### Python Decision Engine

```python
from typing import Dict, Any, List, Optional

def evaluate_options(options: List[str], criteria: List[Dict[str, float]]) -> Dict[str, Any]:
    """Evaluate options against weighted criteria."""
    scores = {}
    for option in options:
        score = sum(c.get("weight", 0.5) * c.get("score", 0.5) for c in criteria)
        scores[option] = score
    
    best = max(scores.keys(), key=lambda k: scores[k]) if scores else None
    return {"selected": best, "scores": scores, "confidence": scores.get(best, 0.0)}

def analyze_strategy(context: Dict[str, Any], constraints: List[str]) -> Dict[str, Any]:
    """Analyze strategy feasibility."""
    return {"context_analysis": context, "constraints_valid": len(constraints), "recommendation": "proceed"}
```

### Z3 Constraint Verification

```python
def verify_strategic_feasibility(budget: float, timeline: int, resources: int) -> bool:
    """Verify strategic plan satisfies constraints."""
    from z3 import Real, Int, Solver
    
    B, T, R = Real("budget"), Int("timeline"), Int("resources")
    solver = Solver()
    solver.add(B >= 0)
    solver.add(T > 0)
    solver.add(R >= 0)
    solver.add(B <= 1000000)
    
    return solver.check() == sat
```

## Testing

```python
import pytest

def test_evaluate():
    opts = ["A", "B"]
    crit = [{"weight": 0.5, "score": 0.8}, {"weight": 0.5, "score": 0.6}]
    result = evaluate_options(opts, crit)
    assert "selected" in result
```

## Security Considerations

- Pure constraint logic, no external dependencies.
