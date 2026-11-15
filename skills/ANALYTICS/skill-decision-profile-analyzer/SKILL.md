---
name: skill-decision-profile-analyzer
domain: ANALYTICS
version: 1.0.0
surfaces:
  - python
  - prolog
  - sqlite
description: Dual-surface decision-profile analyzer that ingests elimination trace history from SQLite and computes a solver behavioral personality profile. Computes the logical-pruning versus probabilistic-decay ratio in Python and asserts static relational facts (solver_profile/3) into Prolog for downstream strategic query routing. Use when diagnosing solver cognitive bias, evaluating hard-constraint vs soft-decay behavior, or tuning adaptive expected utility weightings.
purpose: Quantify solver behavioral personality by computing hard-pruning versus probabilistic-decay ratios and asserting Prolog profile facts.
dependencies: []
tags:
  - solver-personality
  - decision-profile
  - prune-ratio
  - elimination-trace
  - sqlite
  - prolog
inputs:
  trace_history_session:
    type: string
    required: true
    description: Unique session ID whose elimination trace history in SQLite to analyze.
  game_type:
    type: string
    required: true
    description: "Game classification label (e.g. 'pd', 'coordination', 'general_sum')."
outputs:
  solver_profile:
    type: object
    description: Profile record containing prune_ratio, bias_direction, and confidence.
  hard_logic_count:
    type: integer
    description: Total HARD_LOGIC tagged elimination steps in session.
  probabilistic_decay_count:
    type: integer
    description: Total PROBABILISTIC_DECAY and EARLY_TERMINATION steps.
  total_steps:
    type: integer
    description: Total elimination steps evaluated.
  prolog_fact_asserted:
    type: boolean
    description: True if solver_profile/3 fact was successfully asserted into Prolog.
---

# Skill Decision Profile Analyzer Engine

`skill-decision-profile-analyzer` quantifies the operational cognitive personality of strategic solvers. By inspecting SQLite elimination trace logs, it computes the ratio of deductive constraint pruning ($\text{HARD\_LOGIC}$) to continuous entropy reduction ($\text{PROBABILISTIC\_DECAY}$), asserting queryable `solver_profile/3` relational facts into Prolog:

$$\text{prune\_ratio} = \frac{|S_{\text{hard\_logic}}|}{|S_{\text{total}}|}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Decision Profiling Progression

```
[1. Trace Ingest & Session Audit] → [2. Prune Ratio & Bias Calculation] → [3. Visual Brief] → [4. Checkpoint] → [5. Prolog Fact Assertion & Session Close]
```

### Stage 1: Trace Ingest & Session Invariant Audit (SQLite)
1. Query SQLite `elimination_trace` table for `trace_history_session`.
2. Ensure session exists and contains at least 1 recorded elimination step.

> **Completion criterion**: Trace step records loaded and grouped by metadata tags.

---

### Stage 2: Prune Ratio & Personality Bias Calculation (Python)
1. Aggregate step counts:
   - $N_{\text{hard}} = \text{COUNT}(\text{HARD\_LOGIC})$
   - $N_{\text{decay}} = \text{COUNT}(\text{PROBABILISTIC\_DECAY} + \text{EARLY\_TERMINATION})$
   - $N_{\text{total}} = N_{\text{hard}} + N_{\text{decay}}$
2. Compute $\text{prune\_ratio} = N_{\text{hard}} / N_{\text{total}}$.
3. Determine `bias_direction`:
   - **`constraint_heavy`**: $\text{prune\_ratio} > 0.60$
   - **`prior_heavy`**: $\text{prune\_ratio} < 0.40$
   - **`balanced`**: $0.40 \le \text{prune\_ratio} \le 0.60$

> **Completion criterion**: Prune ratio computed in $[0.0, 1.0]$ and bias direction classified.

---

### Stage 3: The Visual Brief
For solver diagnostic reviews, generate an interactive personality brief:
- **Location**: Write to `%TEMP%\decision-profile-brief-<timestamp>.html` (Windows) or `/tmp/decision-profile-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render solver personality radar chart, step breakdown pie chart, and bias distribution gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before asserting facts into the running Prolog knowledge base:
1. Verify that $N_{\text{total}} \ge 3$ for statistical confidence ($> 0.80$).
2. If session contains zero steps, halt and flag degenerate empty session.

> **Completion criterion**: Sample size verified sufficient for confident personality profiling.

---

### Stage 5: Prolog Fact Assertion & SQLite Session Close
1. Assert dynamic relational fact into Prolog:
   ```prolog
   assertz(solver_profile(SessionId, PruneRatio, BiasDirection)).
   ```
2. Update SQLite `elimination_sessions` table with timestamp and total eliminated count.
3. Emit full solver profile output.

> **Completion criterion**: Fact asserted in Prolog and SQLite session marked complete.

---

## Surface References

### Python Calculation Surface

```python
from typing import Dict, Any

def analyze_solver_profile(session_id: str, game_type: str, hard_count: int, decay_count: int) -> Dict[str, Any]:
    total = hard_count + decay_count
    if total == 0:
        return {"status": "error", "message": "Zero elimination steps in session"}
        
    ratio = round(hard_count / total, 4)
    if ratio > 0.60:
        bias = "constraint_heavy"
    elif ratio < 0.40:
        bias = "prior_heavy"
    else:
        bias = "balanced"
        
    confidence = min(1.0, 0.5 + (total * 0.05))
    
    return {
        "solver_profile": {
            "prune_ratio": ratio,
            "bias_direction": bias,
            "confidence": round(confidence, 2)
        },
        "hard_logic_count": hard_count,
        "probabilistic_decay_count": decay_count,
        "total_steps": total,
        "prolog_fact_asserted": True
    }
```

### SQLite Schema Surface

```sql
SELECT metadata_tag, COUNT(*) as tag_count
FROM elimination_trace
WHERE session_id = :session_id
GROUP BY metadata_tag;

UPDATE elimination_sessions
SET completed_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
    total_eliminated = :total_eliminated
WHERE session_id = :session_id;
```

### Prolog Profile Surface

```prolog
:- dynamic solver_profile/3.

solver_bias(Session, constraint_heavy) :-
    solver_profile(Session, Ratio, _),
    Ratio > 0.60.

solver_bias(Session, prior_heavy) :-
    solver_profile(Session, Ratio, _),
    Ratio < 0.40.
```

---

## Anti-Patterns & Guardrails

- **Zero-Step Division by Zero** — Running profile analysis on sessions with zero elimination events without guard checking.
- **Stale Prolog Assertions** — Re-analyzing a session without retracting prior `solver_profile(Session, _, _)` facts, resulting in duplicate facts.
- **Unbounded Confidence** — Assigning 100% confidence to personality profiles evaluated on fewer than 3 total elimination steps.
