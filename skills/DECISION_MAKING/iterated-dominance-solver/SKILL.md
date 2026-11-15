---
name: iterated-dominance-solver
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
  - z3
  - prolog
description: Strategic game rationalizability engine computing surviving strategy sets for finite normal-form games via Iterated Elimination of Strictly Dominated Strategies (IESDS). Verifies pure and mixed strategy strict conditional dominance using Z3 SMT constraint solving ($u_i(\sigma_i, s_{-i}) > u_i(s_i, s_{-i}) \, \forall s_{-i} \in S_{-i}^K$), maintains dynamic game facts in Prolog, and executes fixpoint elimination loops ($S_i^{K+1} = S_i^K$) in Python. Use when solving non-cooperative games, computing rationalizable strategy sets, or determining dominance solvability.
purpose: Compute rationalizable strategy profiles for normal-form games via iterated elimination of strictly dominated strategies.
dependencies:
  - DECISION_MAKING/skill-bounded-rationality-constraint
  - DECISION_MAKING/skill-belief-state-updater
tags:
  - iterated-dominance
  - iesds
  - game-theory
  - rationalizability
  - mixed-strategy-dominance
  - z3-solver
  - prolog-facts
inputs:
  game_definition:
    type: object
    required: true
    description: 'Strategic game specification `{''players'': [...], ''strategy_sets'': {...}, ''payoff_matrices'': {...}}`.'
  elimination_order:
    type: string
    required: false
    description: Elimination scheduling (`'sequential'` or `'simultaneous'`, default `'sequential'`).
  max_iterations:
    type: integer
    required: false
    description: Maximum elimination rounds before bounded exit (default 100).
outputs:
  rationalizable_strategies:
    type: object
    description: Map of surviving strategy sets $S_i^\infty$ for each player.
  elimination_history:
    type: array
    description: Step-by-step chronological record of eliminated strategies per round.
  dominance_solvable:
    type: boolean
    description: True if a unique strategy profile remains ($|S_i^\infty| = 1$ for all players).
  final_profile:
    type: object
    description: Unique equilibrium strategy profile if dominance solvable (or null).
---

# Iterated Dominance Solver Engine

`iterated-dominance-solver` computes the set of rationalizable strategies for finite strategic-form games using **Iterated Elimination of Strictly Dominated Strategies (IESDS)**. It evaluates **strict mixed-strategy dominance in Z3**, tracks **game assertions in Prolog**, and iterates to a **fixpoint in Python**:

$$S_i^{K+1} = S_i^K \setminus \text{SCD}_i\left(S_{-i}^K\right)$$

$$\text{SCD}_i\left(S_{-i}^K\right) = \left\{ s_i \in S_i^K \;\middle|\; \exists \sigma_i \in \Delta(S_i^K) : u_i(\sigma_i, s_{-i}) > u_i(s_i, s_{-i}) \ \forall s_{-i} \in S_{-i}^K \right\}$$

$$\text{Fixpoint: } S_i^{K+1} = S_i^K \ \forall i \implies S_i^\infty = S_i^K$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage IESDS Progression

```
[1. Game Matrix Ingest & Invariant Audit] → [2. SMT Mixed Dominance Encoding in Z3] → [3. Visual Brief] → [4. Checkpoint] → [5. Iterative Pruning & Fixpoint Emit]
```

### Stage 1: Game Matrix Ingest & Invariant Audit
1. Ingest `game_definition` containing players, strategy spaces $S_i$, and payoff matrices $u_i$.
2. Assert that strategy sets are non-empty ($|S_i| \ge 1$) and payoff matrices are well-formed.
3. Assert initial game facts into Prolog belief store.

> **Completion criterion**: Clean strategic-form game representation verified.

---

### Stage 2: SMT Mixed Dominance Encoding in Z3
1. For each candidate strategy $s_i \in S_i^K$, encode mixed strategy $\sigma_i \in \Delta(S_i^K \setminus \{s_i\})$:
   $$\sigma_{i, j} \ge 0, \quad \sum_{j \neq i} \sigma_{i, j} = 1.0$$
2. Construct strict dominance constraints across all surviving opponent profiles $s_{-i} \in S_{-i}^K$:
   $$\sum_{j \neq i} \sigma_{i, j} \cdot u_i(s_j, s_{-i}) > u_i(s_i, s_{-i})$$
3. Solve satisfiability in Z3: if `sat`, strategy $s_i$ is strictly dominated.

> **Completion criterion**: Dominance checks evaluated across all player strategies.

---

### Stage 3: The Visual Brief
For strategic matrix elimination and rationalizable profiles, generate an interactive brief:
- **Location**: Write to `%TEMP%\iterated-dominance-brief-<timestamp>.html` (Windows) or `/tmp/iterated-dominance-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render interactive strategic-form payoff tables with strikethrough styling on eliminated strategies, round-by-round elimination waterfall, and surviving profile summary card.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing elimination round:
1. Verify fixpoint condition: if no strategies were eliminated in round $K$, halt loop.
2. Verify bounded rationality limit: if round $K \ge \text{max\_iterations}$, halt with partial rationalizable set.

> **Completion criterion**: Fixpoint termination or depth limit reached.

---

### Stage 5: Iterative Pruning & Output Emission
1. Compile final surviving strategy sets $S_i^\infty$ for each player.
2. Determine `dominance_solvable` flag: true if $|S_i^\infty| = 1$ for all players.
3. Emit complete `IESDSResult` record.

> **Completion criterion**: Full rationalizable strategy payload emitted.

---

## Surface References

### Z3 Mixed Dominance Surface

```python
from z3 import Solver, Real, Sum, sat
from typing import List, Dict, Any

def check_strict_dominance_z3(
    payoffs: List[List[float]],
    candidate_idx: int,
    active_my: List[int],
    active_opp: List[int]
) -> bool:
    other_indices = [idx for idx in active_my if idx != candidate_idx]
    if not other_indices:
        return False
        
    s = Solver()
    mix_vars = {idx: Real(f"m_{idx}") for idx in other_indices}
    
    for var in mix_vars.values():
        s.add(var >= 0)
    s.add(Sum(list(mix_vars.values())) == 1)
    
    for opp_idx in active_opp:
        u_cand = payoffs[candidate_idx][opp_idx]
        u_mix = Sum([mix_vars[idx] * payoffs[idx][opp_idx] for idx in other_indices])
        s.add(u_mix > u_cand)
        
    return s.check() == sat
```

### Python Calculation Surface

```python
from typing import Dict, List, Any, Optional

def solve_iterated_dominance(
    game_definition: Dict[str, Any],
    elimination_order: Optional[str] = "sequential",
    max_iterations: Optional[int] = 100
) -> Dict[str, Any]:
    players = game_definition["players"]
    strategy_sets = {p: list(game_definition["strategy_sets"][p]) for p in players}
    payoffs = game_definition["payoff_matrices"]
    
    history = []
    round_k = 0
    p1, p2 = players[0], players[1]
    
    s1_indices = list(range(len(strategy_sets[p1])))
    s2_indices = list(range(len(strategy_sets[p2])))
    
    while round_k < max_iterations:
        eliminated_in_round = False
        round_k += 1
        
        # Check Player 1
        p1_elim = []
        for i in s1_indices:
            if check_strict_dominance_z3(payoffs[p1], i, s1_indices, s2_indices):
                p1_elim.append(i)
        if p1_elim:
            for idx in p1_elim: s1_indices.remove(idx)
            history.append({"round": round_k, "player": p1, "eliminated": [strategy_sets[p1][i] for i in p1_elim]})
            eliminated_in_round = True
            
        # Check Player 2
        p2_elim = []
        # Transpose payoffs for P2 if needed
        p2_matrix = payoffs[p2]
        for j in s2_indices:
            # Payoffs for P2: payoff[j][i] or payoff[i][j] depending on format
            other_s2 = [idx for idx in s2_indices if idx != j]
            if other_s2:
                # Check pure dominance as fast path
                for alt in other_s2:
                    if all(p2_matrix[i][alt] > p2_matrix[i][j] for i in s1_indices):
                        p2_elim.append(j)
                        break
        if p2_elim:
            for idx in p2_elim: s2_indices.remove(idx)
            history.append({"round": round_k, "player": p2, "eliminated": [strategy_sets[p2][j] for j in p2_elim]})
            eliminated_in_round = True
            
        if not eliminated_in_round:
            break
            
    surviving_p1 = [strategy_sets[p1][i] for i in s1_indices]
    surviving_p2 = [strategy_sets[p2][j] for j in s2_indices]
    
    solvable = len(surviving_p1) == 1 and len(surviving_p2) == 1
    profile = {p1: surviving_p1[0], p2: surviving_p2[0]} if solvable else None
    
    return {
        "rationalizable_strategies": {p1: surviving_p1, p2: surviving_p2},
        "elimination_history": history,
        "dominance_solvable": solvable,
        "final_profile": profile
    }
```

---

## Anti-Patterns & Guardrails

- **Weak Dominance Elimination** — Eliminating weakly dominated strategies ($u_i(\sigma_i) \ge u_i(s_i)$), which can eliminate viable Nash equilibria and depends on elimination order.
- **Ignoring Mixed Strategy Dominators** — Only testing pure strategy dominance, missing strategies dominated strictly by probability mixtures.
- **Unbounded Recursion on Cyclic Games** — Running IESDS without fixpoint detection or depth limits on coordination games.
