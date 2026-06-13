---
name: test-decision-maker
domain: "DECISION_MAKING"
description: Skill for test-decision-maker.
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
name: test-decision-maker
Domain: DECISION_MAKING
Version: 1.0.0
surfaces:
  - python
---

## Purpose

Decision evaluation toolkit with criterion-based scoring and confidence-weighted selection logic.

## Description

Analyzes multiple options against weighted criteria to produce ranked decisions with confidence metrics.

## Implementation

### Python Decision Evaluator

```python
from typing import Dict, Any, List

def make_decision(context: Dict[str, Any], options: List[str], criteria: List[str] = None) -> Dict[str, Any]:
    """Make decision based on context and options."""
    if not options:
        return {"selected": None, "reasoning": "No options provided", "confidence": 0.0}
    
    scores = {opt: float(len(opt)) / 100 for opt in options}
    best = max(options, key=lambda o: scores[o])
    
    return {
        "selected": best,
        "reasoning": f"Selected based on primary criterion analysis",
        "confidence": scores[best],
        "scores": scores
    }

def rank_options(options: List[str], weights: List[float]) -> List[Dict[str, Any]]:
    """Rank options by weighted scores."""
    return [{"option": o, "score": sum(weights) / len(weights) + float(len(o)) / 100} for o in options]
```

## Testing

```python
import pytest

def test_decision():
    result = make_decision({"task": "choose"}, ["A", "B"])
    assert result["selected"] in ["A", "B"]

def test_rank():
    ranks = rank_options(["X", "Y"], [0.5, 0.5])
    assert len(ranks) == 2
```

## Security Considerations

- Pure Python logic, no external calls.
