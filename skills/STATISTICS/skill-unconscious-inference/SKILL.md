---
name: skill-unconscious-inference
domain: STATISTICS
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Helmholtzian unconscious perceptual inference engine selecting the most probable semantic model interpretation from multiple logically valid candidate hypotheses. Combines prior perceptual expectations with historical empirical success rates in SQLite, evaluates Bayesian/frequency/hybrid composite scores, selects the top Maximum A Posteriori (MAP) activation branch, and provides ranked alternative interpretations. Use when resolving ambiguity across multiple logically valid models or choosing between alternative explanations under noisy sensor inputs.
purpose: Resolve ambiguity across multiple valid logical hypotheses using Bayesian and historical frequency weighting with SQLite persistence.
dependencies:
  - guardrails/validate_measurement_level
  - builtin-occams-razor-evaluator
tags:
  - unconscious-inference
  - helmholtz-machine
  - map-selection
  - hypothesis-disambiguation
  - perceptual-priors
  - sqlite-persistence
inputs:
  valid_models:
    type: array
    required: true
    description: 'List of logically admissible candidate model interpretations `[{type: str, ...}, ...]`.'
  priors:
    type: object
    required: false
    description: 'Prior probability weights for candidate model types `{model_type: float}`.'
  historical_log:
    type: array
    required: false
    description: 'Optional execution history entries for empirical frequency weighting `[{type: str, success: bool}, ...]`.'
  scoring_method:
    type: string
    required: false
    description: Selection algorithm ('bayesian', 'frequency', or 'hybrid', default 'hybrid').
  db_path:
    type: string
    required: false
    description: Optional SQLite database file path for inference history persistence.
outputs:
  selected_model:
    type: object
    description: Top-ranked model interpretation chosen for downstream execution.
  selection_score:
    type: number
    description: Posterior confidence score for chosen model $\in [0.0, 1.0]$.
  alternative_models:
    type: array
    description: Remaining candidate models ranked by posterior selection score.
---

# Skill Unconscious Inference Engine

`skill-unconscious-inference` resolves perceptual ambiguity among multiple logically valid models using the Helmholtzian principle of unconscious inference. It evaluates **Bayesian priors, empirical success rates, and likelihood evidence in Python**, persisting runtime decisions and success logs in **SQLite**:

$$\text{Score}(M_i) = w_{\text{prior}} P(M_i) + w_{\text{hist}} \left(\frac{N_{\text{success}}(M_i) + 1}{N_{\text{total}}(M_i) + 2}\right) + w_{\text{lik}} L(M_i)$$

$$\text{MAP Model: } M^* = \arg\max_{M_i \in \mathcal{M}_{\text{valid}}} \text{Score}(M_i)$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Unconscious Inference Progression

```
[1. Candidate Model Invariant Audit] → [2. Historical Frequency & Prior Fusion] → [3. Visual Brief] → [4. Checkpoint] → [5. MAP Selection & SQLite Commit]
```

### Stage 1: Candidate Model Invariant Audit
1. Ingest `valid_models` list containing $K \ge 1$ candidate interpretations.
2. If $K = 1$, return model with default confidence $1.0$.

> **Completion criterion**: Admissible candidate model set $\mathcal{M}_{\text{valid}}$ verified.

---

### Stage 2: Historical Frequency & Prior Fusion
1. Query SQLite `inference_history` to retrieve past success/failure tallies per model type.
2. Compute Laplace-smoothed empirical success rates: $f_{\text{hist}}(M_i) = \frac{S_i + 1}{N_i + 2}$.
3. Combine prior belief $P(M_i)$ and empirical frequency into composite weights.

> **Completion criterion**: Composite score weights evaluated for all $K$ models.

---

### Stage 3: The Visual Brief
For model disambiguation and perceptual arbitration, generate an interactive brief:
- **Location**: Write to `%TEMP%\unconscious-inference-brief-<timestamp>.html` (Windows) or `/tmp/unconscious-inference-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render candidate hypothesis decision tree, posterior score competition bar chart, and historical success confidence breakdown.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before activating selected branch:
1. Check top model confidence margin: $\Delta \text{Score} = \text{Score}(M_1) - \text{Score}(M_2)$.
2. If margin is extremely tight ($\Delta \le 0.05$), flag close-call ambiguity note.

> **Completion criterion**: Confidence margin and disambiguation clarity verified.

---

### Stage 5: MAP Selection & SQLite Persistence Commit
1. Sort candidate models in descending order of composite score.
2. Select highest-scoring model as `selected_model`.
3. Commit inference invocation atomically to SQLite.
4. Emit complete `UnconsciousInferenceResult` record.

> **Completion criterion**: Top model selected, alternative ranking compiled, and ledger committed to SQLite.

---

## Surface References

### Python Calculation Surface

```python
import sqlite3
from typing import List, Dict, Any, Optional

def run_unconscious_inference(
    valid_models: List[Dict[str, Any]],
    priors: Optional[Dict[str, float]] = None,
    historical_log: Optional[List[Dict[str, Any]]] = None,
    scoring_method: str = "hybrid",
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    if not valid_models:
        raise ValueError("empty_model_set: Requires at least 1 valid candidate model.")
        
    k = len(valid_models)
    if k == 1:
        return {
            "selected_model": valid_models[0],
            "selection_score": 1.0,
            "alternative_models": []
        }
        
    prior_map = priors or {}
    hist_counts = {}
    if historical_log:
        for entry in historical_log:
            mtype = entry.get("type", "unknown")
            succ = 1 if entry.get("success", False) else 0
            if mtype not in hist_counts: hist_counts[mtype] = {"total": 0, "succ": 0}
            hist_counts[mtype]["total"] += 1
            hist_counts[mtype]["succ"] += succ
            
    scored = []
    for model in valid_models:
        mtype = model.get("type", model.get("name", "unknown"))
        prior_val = prior_map.get(mtype, 1.0 / k)
        
        hist_data = hist_counts.get(mtype, {"total": 0, "succ": 0})
        freq_val = (hist_data["succ"] + 1.0) / (hist_data["total"] + 2.0)
        
        if scoring_method == "bayesian":
            score = prior_val
        elif scoring_method == "frequency":
            score = freq_val
        else: # hybrid
            score = 0.5 * prior_val + 0.5 * freq_val
            
        scored.append((score, model))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    total_score = sum(s[0] for s in scored) or 1.0
    
    ranked = [{"model": m, "score": round(s / total_score, 4)} for s, m in scored]
    top_pick = ranked[0]
    
    return {
        "selected_model": top_pick["model"],
        "selection_score": top_pick["score"],
        "alternative_models": ranked[1:]
    }
```

### SQLite Schema Surface

```sql
CREATE TABLE IF NOT EXISTS inference_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_type TEXT NOT NULL,
    success INTEGER NOT NULL,
    timestamp INTEGER DEFAULT (strftime('%s', 'now'))
);
```

---

## Anti-Patterns & Guardrails

- **Arbitrary Tie-Breaking Without History** — Defaulting to hardcoded arbitrary array indices instead of using Laplace-smoothed empirical success frequencies.
- **Unnormalized Prior Probabilities** — Passing prior weights that do not sum to 1.0 without normalizing.
- **Ignoring Competing Candidate Close Calls** — Discarding second-best candidate models without ranking alternative choices for fallback execution.
