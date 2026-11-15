---
name: skill-belief-state-updater
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - hy
  - python
description: Continuous probability mass redistribution engine for Bayesian belief-state updates after discrete strategy elimination. Re-allocates probability mass from pruned opponent strategies proportionally across surviving strategy configurations ($\hat{p}_i = p_i / \sum_{j \in S_{\text{active}}} p_j$), verifies lattice closure over surviving subsets in Hy, and computes normalization factors and per-strategy transition logs in Python. Use when transitioning from hard solver pruning to continuous probabilistic opponent models.
purpose: Re-allocate eliminated probability mass to surviving strategies using normalized Bayesian belief-state updates.
dependencies:
  - DECISION_MAKING/lattice-inclusion-exclusion-sum
  - DECISION_MAKING/iterated-dominance-solver
tags:
  - belief-state-updater
  - bayesian-update
  - mass-redistribution
  - lattice-closure
  - hy-symbolic
  - probabilistic-modelling
inputs:
  active_strategies:
    type: array
    required: true
    description: List of strategy identifiers that survived elimination (e.g. `[0, 2, 3]`).
  eliminated_strategies:
    type: array
    required: true
    description: List of strategy identifiers pruned by hard dominance solver (e.g. `[1]`).
  prior_weights:
    type: object
    required: true
    description: 'Prior probability weights dictionary `{strategy_id: weight}` before elimination.'
outputs:
  updated_belief_state:
    type: object
    description: 'Normalized probability density mapping `{strategy_id: weight}` over surviving strategies.'
  normalization_factor:
    type: number
    description: Multiplicative constant $Z = 1 / \sum_{j \in S_{\text{active}}} p_j$ used to re-normalize surviving mass to 1.0.
  eliminated_mass:
    type: number
    description: Total probability mass $\sum_{k \in S_{\text{elim}}} p_k$ redistributed from pruned strategies.
  update_log:
    type: array
    description: Per-strategy transition records detailing prior weight, delta, and updated posterior weight.
---

# Skill Belief State Updater Engine

`skill-belief-state-updater` bridges hard discrete strategy pruning with **continuous Bayesian belief-state modelling**. It uses **Hy symbolic Lisp rules** to verify lattice closure and **Python numerical normalization** to re-distribute eliminated probability mass:

$$\hat{p}_i = \frac{p_i}{\sum_{j \in S_{\text{active}}} p_j} \quad \forall i \in S_{\text{active}}, \quad \sum_{i \in S_{\text{active}}} \hat{p}_i = 1.0$$

$$M_{\text{elim}} = \sum_{k \in S_{\text{elim}}} p_k, \quad Z = \frac{1}{1 - M_{\text{elim}}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Belief Update Progression

```
[1. Active & Eliminated Strategy Ingest] → [2. Hy Lattice Closure & Mass Accounting] → [3. Visual Brief] → [4. Checkpoint] → [5. Bayesian Normalization & Emit]
```

### Stage 1: Active & Eliminated Strategy Ingest
1. Ingest `active_strategies`, `eliminated_strategies`, and `prior_weights`.
2. Verify that active set is non-empty ($|S_{\text{active}}| \ge 1$) and disjoint from eliminated set ($S_{\text{active}} \cap S_{\text{elim}} = \emptyset$).
3. Validate prior probability sum: $\sum p_i = 1.0 \pm 10^{-5}$.

> **Completion criterion**: Clean strategy partition and prior weights verified.

---

### Stage 2: Hy Lattice Closure & Mass Accounting
1. Compute eliminated probability mass: $M_{\text{elim}} = \sum_{k \in S_{\text{elim}}} p_k$.
2. Compute active mass denominator: $M_{\text{active}} = \sum_{j \in S_{\text{active}}} p_j$.
3. In Hy, verify that active strategies form a valid closed subset over the lattice domain.

> **Completion criterion**: Mass partition and lattice closure evaluated.

---

### Stage 3: The Visual Brief
For Bayesian belief updating and probability mass transitions, generate an interactive brief:
- **Location**: Write to `%TEMP%\belief-state-brief-<timestamp>.html` (Windows) or `/tmp/belief-state-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render before vs. after probability density bar charts, mass redistribution flow diagram (Sankey-style), and normalization diagnostic card.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing updated density:
1. Verify non-zero active mass: $M_{\text{active}} > 0$. If $M_{\text{active}} = 0$, distribute mass uniformly ($1/|S_{\text{active}}|$).
2. Calculate normalization factor $Z = 1 / M_{\text{active}}$.

> **Completion criterion**: Normalization factor $Z$ computed safely.

---

### Stage 5: Bayesian Normalization & Output Emission
1. Compute posterior weights $\hat{p}_i = p_i \cdot Z$ for each active strategy $i \in S_{\text{active}}$.
2. Generate detailed update audit log.
3. Emit complete `BeliefStateResult` record.

> **Completion criterion**: Full updated belief-state payload emitted.

---

## Surface References

### Hy Symbolic Surface

```hy
(defn redistribute-mass [active eliminated priors]
  "Re-allocate probability mass from eliminated to active strategies"
  (let [eliminated-mass (sum (list (get priors s) (for [s eliminated])))
        active-priors   (sum (list (get priors s) (for [s active])))
        norm-factor     (if (> active-priors 0) (/ 1.0 active-priors) 0)]
    {:normalization_factor norm-factor
     :eliminated_mass eliminated-mass
     :update_type "proportional_redistribution"}))
```

### Python Calculation Surface

```python
from typing import Dict, List, Any, Union

def update_belief_state(
    active_strategies: List[Union[int, str]],
    eliminated_strategies: List[Union[int, str]],
    prior_weights: Dict[Union[int, str], float]
) -> Dict[str, Any]:
    if not active_strategies:
        raise ValueError("empty_active_set: Active strategies list cannot be empty.")
        
    elim_mass = sum(prior_weights.get(s, 0.0) for s in eliminated_strategies)
    active_mass = sum(prior_weights.get(s, 0.0) for s in active_strategies)
    
    if active_mass <= 1e-12:
        # Uniform fallback if all active strategies had 0 prior weight
        n = len(active_strategies)
        updated = {s: round(1.0 / n, 6) for s in active_strategies}
        norm_factor = 1.0
    else:
        norm_factor = 1.0 / active_mass
        updated = {s: round(prior_weights.get(s, 0.0) * norm_factor, 6) for s in active_strategies}
        
    update_log = []
    for s in active_strategies:
        prior = prior_weights.get(s, 0.0)
        post = updated[s]
        update_log.append({
            "strategy": s,
            "prior_weight": prior,
            "posterior_weight": post,
            "delta": round(post - prior, 6)
        })
        
    return {
        "updated_belief_state": updated,
        "normalization_factor": round(norm_factor, 6),
        "eliminated_mass": round(elim_mass, 6),
        "update_log": update_log
    }
```

---

## Anti-Patterns & Guardrails

- **Division by Zero on Empty Active Mass** — Attempting $1 / M_{\text{active}}$ when all surviving strategies had 0 prior weight; must fall back to uniform distribution ($1/|S|$).
- **Leaking Eliminated Strategies** — Retaining non-zero probability weights for pruned strategies in the updated belief state dictionary.
- **Unnormalized Density Drift** — Emitting posterior distributions where $\sum \hat{p}_i \neq 1.0$.
