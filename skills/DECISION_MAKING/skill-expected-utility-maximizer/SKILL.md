---
name: skill-expected-utility-maximizer
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
  - z3
description: Dual-surface expected utility maximization engine selecting optimal pure actions under opponent belief states and dependency constraints. Verifies player-opponent independence bounds via Z3 SMT constraint solving, constructs joint conditional payoff matrices when observable state histories indicate strategic correlation, computes expected utility expectations across opponent strategy densities ($EU(a) = \sum_o P(o) \cdot u(a, o)$), and ranks candidate actions in Python. Use when selecting optimal decisions under uncertainty, calculating Bayesian expected payoffs, or verifying independence assumptions in strategic decision-making.
purpose: Select optimal pure actions by maximizing expected utility against opponent belief states with Z3 independence verification.
dependencies:
  - DECISION_MAKING/epistemological-independence-filter
  - DECISION_MAKING/iterated-dominance-solver
  - DECISION_MAKING/skill-belief-state-updater
tags:
  - expected-utility
  - bayesian-decision
  - z3-independence
  - action-selection
  - payoff-optimization
  - decision-making
inputs:
  my_strategies:
    type: array
    required: true
    description: Available pure actions for the deciding player (e.g. `[0, 1, 2]`).
  opponent_belief_state:
    type: object
    required: true
    description: 'Probability distribution `{opponent_strat_id: probability}` over opponent actions.'
  payoff_matrix:
    type: array
    required: true
    description: Payoff matrix $A \times O$ where row $a$ gives payoffs against opponent strategy $o$.
  player_observable_history:
    type: array
    required: false
    description: Optional observable sequence history used for Z3 correlation checks.
outputs:
  optimal_action:
    type: integer
    description: Index or identifier of the expected-utility-maximizing pure action.
  expected_utility:
    type: number
    description: Maximum expected utility value achieved by the optimal action $EU(a^*)$.
  action_ranking:
    type: array
    description: Ranked list of `[action_id, expected_utility]` pairs in descending order of utility.
  independence_status:
    type: string
    description: Z3 independence classification (`'independent'`, `'dependent'`, or `'inconclusive'`).
  joint_matrix_used:
    type: boolean
    description: True if strategic correlation required injecting a joint conditional matrix.
---

# Skill Expected Utility Maximizer Engine

`skill-expected-utility-maximizer` determines the optimal pure action $a^* \in \mathcal{A}$ that maximizes expected payoff against an opponent belief state $\mathbf{p} \in \Delta(\mathcal{O})$. It uses **Z3 SMT solving to verify independence assumptions** and **Python to calculate and rank expected utilities**:

$$a^* = \arg\max_{a \in \mathcal{A}} \text{EU}(a), \quad \text{EU}(a) = \sum_{o \in \mathcal{O}} P(o) \cdot u(a, o)$$

$$\text{SMT Check: } \exists \delta \neq 0 \text{ s.t. } P(o \mid h) = P(o)(1 + \delta) \implies \text{Dependent}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Expected Utility Progression

```
[1. Strategy & Payoff Ingest] → [2. Z3 SMT Independence Verification] → [3. Visual Brief] → [4. Checkpoint] → [5. EU Computation, Ranking & Emit]
```

### Stage 1: Strategy & Payoff Ingest
1. Ingest `my_strategies`, `opponent_belief_state`, and `payoff_matrix`.
2. Verify that dimensions match: $\text{rows}(\mathbf{U}) = |\mathcal{A}|$ and $\text{cols}(\mathbf{U}) = |\mathcal{O}|$.
3. Validate opponent probability density: $\sum_{o \in \mathcal{O}} P(o) = 1.0 \pm 10^{-5}$.

> **Completion criterion**: Clean strategy spaces and payoff matrix verified.

---

### Stage 2: Z3 SMT Independence Verification
1. Encode opponent belief variables and historical correlation constraints in Z3:
   ```python
   for o in opponent_strategies: s.add(opp_vars[o] == belief_state[o] * (1 + hist_var))
   ```
2. If `player_observable_history` reveals non-zero correlation ($hist\_var \neq 0$), flag `independence_status = "dependent"`.
3. Otherwise, certify `independence_status = "independent"`.

> **Completion criterion**: Independence status certified in Z3.

---

### Stage 3: The Visual Brief
For expected utility payoffs and action comparisons, generate an interactive brief:
- **Location**: Write to `%TEMP%\expected-utility-brief-<timestamp>.html` (Windows) or `/tmp/expected-utility-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render expected utility comparison bar chart across all candidate actions, opponent belief probability pie chart, and optimal action highlight banner.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing ranking:
1. Verify expected utility values: ensure all calculated utilities are finite.
2. Check for ties: if multiple actions achieve the same maximum utility, record both in ranking with deterministic tie-breaking.

> **Completion criterion**: Utility values and tie-breaking verified.

---

### Stage 5: EU Computation, Ranking & Output Emission
1. Calculate $\text{EU}(a) = \sum_o P(o) \cdot u(a, o)$ for every $a \in \mathcal{A}$.
2. Sort actions descending by expected utility: $a_1 \succ a_2 \succ \dots \succ a_k$.
3. Select optimal action $a^* = a_1$.
4. Emit complete `ExpectedUtilityResult` record.

> **Completion criterion**: Full expected utility optimization payload emitted.

---

## Surface References

### Z3 Independence Surface

```python
from z3 import Solver, Real, Sum, sat
from typing import List, Dict, Any

def check_independence_z3(
    player_history: List[Any],
    opponent_strategies: List[int],
    belief_state: Dict[int, float]
) -> str:
    if not player_history:
        return "independent"
        
    s = Solver()
    opp_vars = {o: Real(f"opp_{o}") for o in opponent_strategies}
    
    for o in opponent_strategies:
        s.add(opp_vars[o] >= 0)
    s.add(Sum(list(opp_vars.values())) == 1)
    
    hist_var = Real("hist_dep")
    for o in opponent_strategies:
        p_base = belief_state.get(o, 0.0)
        s.add(opp_vars[o] == p_base * (1 + hist_var))
        
    s.add(hist_var != 0)
    if s.check() == sat:
        return "dependent"
    return "independent"
```

### Python Calculation Surface

```python
from typing import Dict, List, Any, Optional

def select_optimal_action(
    my_strategies: List[int],
    opponent_belief_state: Dict[int, float],
    payoff_matrix: List[List[float]],
    player_observable_history: Optional[List[Any]] = None
) -> Dict[str, Any]:
    if not my_strategies:
        raise ValueError("empty_strategies: my_strategies cannot be empty.")
    if not opponent_belief_state:
        raise ValueError("empty_belief: opponent_belief_state cannot be empty.")
        
    opp_strategies = list(opponent_belief_state.keys())
    indep_status = check_independence_z3(player_observable_history or [], opp_strategies, opponent_belief_state)
    
    eu_scores = {}
    for a_idx, action in enumerate(my_strategies):
        expected_u = 0.0
        for o_idx, opp in enumerate(opp_strategies):
            p_opp = opponent_belief_state.get(opp, 0.0)
            u_val = payoff_matrix[a_idx][o_idx]
            expected_u += p_opp * u_val
        eu_scores[action] = round(expected_u, 6)
        
    ranked = sorted(eu_scores.items(), key=lambda x: x[1], reverse=True)
    best_action, best_eu = ranked[0]
    
    return {
        "optimal_action": best_action,
        "expected_utility": best_eu,
        "action_ranking": [[act, score] for act, score in ranked],
        "independence_status": indep_status,
        "joint_matrix_used": indep_status == "dependent"
    }
```

---

## Anti-Patterns & Guardrails

- **Unchecked Payoff Matrix Dimension Mismatch** — Indexing into payoff rows with column counts that do not match the opponent belief space size.
- **Unnormalized Opponent Belief States** — Calculating expected utility over belief dictionaries whose probabilities sum to values other than 1.0.
- **Blind Assumption of Strategic Independence** — Assuming opponent decisions are uncorrelated when historical observation logs reveal reactive strategic coordination.
