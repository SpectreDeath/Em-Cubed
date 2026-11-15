---
name: skill-bounded-rationality-constraint
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
description: Active circuit-breaker and convergence middleware enforcing Herbert Simon's bounded rationality constraints over recursive game-theoretic elimination loops (such as IESDS in iterated-dominance-solver). Evaluates maximum iteration recursion depth ($K \ge K_{\text{max}}$) and probability weight delta convergence ($\max_i |w_i^{(K+1)} - w_i^{(K)}| < \delta$), preventing infinite recursion loops, SMT solver hangs, and excessive computation in game-theoretic fixed-point search. Use when wrapping recursive game solvers, bounding elimination depth, or halting iterative belief updates.
purpose: Enforce bounded rationality guardrails and circuit-breaker termination for recursive game-theoretic elimination loops.
dependencies:
  - DECISION_MAKING/iterated-dominance-solver
tags:
  - bounded-rationality
  - circuit-breaker
  - fixpoint-convergence
  - simon-rationality
  - recursion-guard
  - iesds-middleware
inputs:
  current_iteration_k:
    type: integer
    required: true
    description: Current iteration count of the recursive elimination loop.
  max_depth_threshold:
    type: integer
    required: true
    description: Maximum allowed iteration ceiling before forced termination.
  delta_convergence:
    type: number
    required: true
    description: Minimum weight change threshold $\delta$ to consider converged.
  previous_weights:
    type: object
    required: false
    description: 'Strategy probability weights from previous iteration `{strategy_id: weight}`.'
  current_weights:
    type: object
    required: false
    description: 'Strategy probability weights from current iteration `{strategy_id: weight}`.'
outputs:
  should_terminate:
    type: boolean
    description: True if the recursive elimination loop should terminate immediately.
  termination_reason:
    type: string
    description: Qualitative verdict (`'fixpoint_reached'`, `'depth_exceeded'`, or `'continue'`).
  current_weights:
    type: object
    description: Echo of current strategy weights for passing to next iteration.
  iterations_performed:
    type: integer
    description: Total elimination iterations executed so far.
---

# Skill Bounded Rationality Constraint Engine

`skill-bounded-rationality-constraint` implements **Herbert Simon's (1957) bounded rationality framework** as active circuit-breaker middleware for recursive game solvers. It guards **iterative elimination loops** against computational exhaustion and detects **stable fixpoint convergence** in **Python**:

$$\text{Termination}(K) = \begin{cases} \text{True (fixpoint\_reached)} & \text{if } \max_{i} \left| w_i^{(K+1)} - w_i^{(K)} \right| < \delta \\ \text{True (depth\_exceeded)} & \text{if } K \ge K_{\text{max}} \\ \text{False (continue)} & \text{otherwise} \end{cases}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Bounded Rationality Progression

```
[1. Recursion Parameters Ingest] → [2. Weight Delta & Residual Evaluation] → [3. Visual Brief] → [4. Checkpoint] → [5. Circuit-Breaker Verdict & Emit]
```

### Stage 1: Recursion Parameters Ingest
1. Ingest `current_iteration_k`, `max_depth_threshold` ($K_{\text{max}} \ge 1$), and `delta_convergence` ($\delta > 0$).
2. Ingest optional `previous_weights` and `current_weights` dictionaries.

> **Completion criterion**: Valid recursion metrics and thresholds verified.

---

### Stage 2: Weight Delta & Residual Evaluation
1. If weights are provided, compute maximum $L_\infty$ absolute weight difference across all shared strategies:
   $$\Delta_{\text{max}} = \max_{i} \left| w_i^{(K)} - w_i^{(K-1)} \right|$$
2. Identify missing or newly added strategies in weight dictionaries.

> **Completion criterion**: Weight change residual $\Delta_{\text{max}}$ computed.

---

### Stage 3: The Visual Brief
For recursive elimination monitoring and computational budget tracking, generate an interactive brief:
- **Location**: Write to `%TEMP%\bounded-rationality-brief-<timestamp>.html` (Windows) or `/tmp/bounded-rationality-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render iteration step progress gauge vs. $K_{\text{max}}$, weight delta convergence curve ($\Delta_{\text{max}}$ vs $K$), and circuit breaker status banner.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before emitting verdict:
1. Priority 1 (Depth limit): If $K \ge K_{\text{max}}$, set `should_terminate = True`, `reason = "depth_exceeded"`.
2. Priority 2 (Fixpoint reached): If `previous_weights` provided and $\Delta_{\text{max}} < \delta$, set `should_terminate = True`, `reason = "fixpoint_reached"`.
3. Otherwise: set `should_terminate = False`, `reason = "continue"`.

> **Completion criterion**: Termination status and reasoning determined.

---

### Stage 5: Circuit-Breaker Verdict & Output Emission
1. Package termination verdict boolean, reason code, and iteration counter.
2. Emit complete `BoundedRationalityResult` record.

> **Completion criterion**: Full circuit-breaker verdict payload emitted.

---

## Surface References

### Python Calculation Surface

```python
from typing import Dict, Any, Optional, Union

def check_bounded_rationality(
    current_iteration_k: int,
    max_depth_threshold: int,
    delta_convergence: float,
    previous_weights: Optional[Dict[Union[int, str], float]] = None,
    current_weights: Optional[Dict[Union[int, str], float]] = None
) -> Dict[str, Any]:
    if max_depth_threshold < 1:
        raise ValueError("invalid_max_depth: max_depth_threshold must be >= 1.")
    if delta_convergence <= 0:
        raise ValueError("invalid_delta: delta_convergence must be > 0.")
        
    # Check 1: Maximum depth threshold
    if current_iteration_k >= max_depth_threshold:
        return {
            "should_terminate": True,
            "termination_reason": "depth_exceeded",
            "current_weights": current_weights,
            "iterations_performed": current_iteration_k
        }
        
    # Check 2: Weight delta convergence
    if previous_weights is not None and current_weights is not None:
        all_keys = set(previous_weights.keys()).union(set(current_weights.keys()))
        max_delta = 0.0
        for k in all_keys:
            w_prev = previous_weights.get(k, 0.0)
            w_curr = current_weights.get(k, 0.0)
            delta = abs(w_curr - w_prev)
            if delta > max_delta:
                max_delta = delta
                
        if max_delta < delta_convergence:
            return {
                "should_terminate": True,
                "termination_reason": "fixpoint_reached",
                "current_weights": current_weights,
                "iterations_performed": current_iteration_k
            }
            
    return {
        "should_terminate": False,
        "termination_reason": "continue",
        "current_weights": current_weights,
        "iterations_performed": current_iteration_k
    }
```

---

## Anti-Patterns & Guardrails

- **Zero Depth Threshold** — Setting $K_{\text{max}} = 0$, terminating before even a single round of elimination executes.
- **Negative Convergence Delta** — Passing $\delta \le 0$, making convergence mathematically impossible and forcing execution until depth exhaustion.
- **Ignoring Partial Weight Maps** — Calculating weight deltas only over shared keys, ignoring newly created or dropped strategies.
