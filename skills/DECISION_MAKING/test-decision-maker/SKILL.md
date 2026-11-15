---
name: test-decision-maker
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
description: Decision evaluation and criterion-based scoring toolkit providing confidence-weighted alternative selection and diagnostic ranking verification. Evaluates candidate options across weighted attribute criteria, computes normalized score profiles and selection confidence metrics ($C = \text{Score}(a^*) - \text{Score}(a_{\text{second}})$), generates reasoning rationales, and validates decision pipelines in Python. Use when testing decision workflows, benchmarking ranking algorithms, or performing quick multi-attribute selection.
purpose: Evaluate and rank candidate options using criterion-based scoring and confidence-weighted selection logic.
dependencies:
  - DECISION_MAKING/multi-surface-decision-tree
tags:
  - decision-evaluation
  - option-selection
  - confidence-scoring
  - criterion-ranking
  - decision-pipeline-test
  - python
inputs:
  options:
    type: array
    required: true
    description: List of candidate option strings or dictionaries `['Option A', 'Option B']`.
  criteria_scores:
    type: object
    required: false
    description: 'Optional mapping of options to criterion score vectors `{opt: [s1, s2, ...]}`.'
  weights:
    type: array
    required: false
    description: Optional criterion weight vector `[w1, w2, ...]`.
  context:
    type: object
    required: false
    description: 'Background operational context `{task: str, constraints: [...]}`.'
outputs:
  selected:
    type: string
    description: Identifier of the top-ranked selected option.
  reasoning:
    type: string
    description: Explanatory rationale detailing why the option was chosen.
  confidence:
    type: number
    description: Confidence score $C \in [0, 1]$ measuring margin of victory over alternative choices.
  scores:
    type: object
    description: Normalized score dictionary mapping each option to its total score.
  ranked_options:
    type: array
    description: Ordered list of all options with individual scores and ranks.
---

# Test Decision Maker Engine

`test-decision-maker` provides lightweight **criterion-based scoring and confidence-weighted alternative selection** for decision pipeline verification in Python:

$$\text{Score}(o) = \sum_{j=1}^m w_j \cdot s_j(o), \quad o^* = \arg\max_{o \in \mathcal{O}} \text{Score}(o)$$

$$\text{Confidence}(o^*) = \begin{cases} \text{Score}(o^*) - \text{Score}(o_{\text{second}}) & \text{if } |\mathcal{O}| \ge 2 \\ 1.0 & \text{if } |\mathcal{O}| = 1 \end{cases}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Decision Evaluation Progression

```
[1. Options & Criteria Ingest] → [2. Score Calculation & Normalization] → [3. Visual Brief] → [4. Checkpoint] → [5. Decision Selection, Confidence & Emit]
```

### Stage 1: Options & Criteria Ingest
1. Ingest `options` array, `criteria_scores`, and optional `weights`.
2. Validate non-empty option set ($|\mathcal{O}| \ge 1$).

> **Completion criterion**: Clean candidate options verified.

---

### Stage 2: Score Calculation & Normalization
1. Compute weighted composite score for each candidate option:
   $$\text{Score}(o) = \sum_j w_j \cdot s_j(o)$$
2. Normalize all composite scores into the $[0, 1]$ interval.

> **Completion criterion**: Option score dictionary evaluated.

---

### Stage 3: The Visual Brief
For option selection and decision confidence validation, generate an interactive brief:
- **Location**: Write to `%TEMP%\test-decision-brief-<timestamp>.html` (Windows) or `/tmp/test-decision-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render option score comparison bar chart, selection margin confidence gauge, and decision reasoning summary card.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before emitting decision:
1. Verify tie-breaking rules: if multiple options share the top score, choose first deterministically and note tie in reasoning.
2. Ensure confidence score satisfies $0.0 \le C \le 1.0$.

> **Completion criterion**: Top candidate and confidence bounds verified.

---

### Stage 5: Decision Selection, Confidence & Output Emission
1. Select top candidate $o^*$.
2. Compute victory margin confidence $C = \text{Score}(o^*) - \text{Score}(o_{\text{second}})$.
3. Synthesize human-readable explanatory reasoning string.
4. Emit complete `DecisionResult` record.

> **Completion criterion**: Full decision evaluation payload emitted.

---

## Surface References

### Python Calculation Surface

```python
from typing import Dict, List, Any, Optional, Union

def make_decision(
    options: List[Union[str, Dict[str, Any]]],
    criteria_scores: Optional[Dict[str, List[float]]] = None,
    weights: Optional[List[float]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if not options:
        return {
            "selected": None,
            "reasoning": "No candidate options provided.",
            "confidence": 0.0,
            "scores": {},
            "ranked_options": []
        }
        
    opt_names = [o if isinstance(o, str) else o.get("name", str(i)) for i, o in enumerate(options)]
    n = len(opt_names)
    
    scores = {}
    if criteria_scores and weights:
        w_norm = [w / sum(weights) for w in weights] if sum(weights) > 0 else [1.0 / len(weights)] * len(weights)
        for name in opt_names:
            c_vec = criteria_scores.get(name, [0.5] * len(w_norm))
            s_val = sum(w * c for w, c in zip(w_norm, c_vec))
            scores[name] = round(s_val, 4)
    else:
        for name in opt_names:
            # Baseline length/lexicographic heuristic if raw options passed
            scores[name] = round(0.5 + (len(name) % 10) * 0.05, 4)
            
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_opt, best_score = ranked[0]
    
    if len(ranked) > 1:
        second_score = ranked[1][1]
        confidence = round(best_score - second_score, 4)
        confidence = max(0.05, min(1.0, confidence))
    else:
        confidence = 1.0
        
    reasoning = f"Selected '{best_opt}' with score {best_score} (margin of victory: {confidence})."
    
    return {
        "selected": best_opt,
        "reasoning": reasoning,
        "confidence": confidence,
        "scores": scores,
        "ranked_options": [{"option": opt, "score": sc, "rank": i + 1} for i, (opt, sc) in enumerate(ranked)]
    }
```

---

## Anti-Patterns & Guardrails

- **Empty Option List Handlers** — Throwing unhandled exceptions on empty option lists instead of returning structured empty result records.
- **Unbounded Confidence Metrics** — Emitting confidence scores $> 1.0$ or $< 0.0$.
- **Ignoring Secondary Runner-Up Margins** — Claiming 100% confidence when the top two candidate options differ by less than $10^{-4}$.
