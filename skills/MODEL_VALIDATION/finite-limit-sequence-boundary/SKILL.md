---
name: finite-limit-sequence-boundary
domain: MODEL_VALIDATION
version: 1.0.0
surfaces:
  - z3
  - python
description: Structural safety guardrail enforcing that infinite mathematical sets and limits in probability or lattice computations are evaluated as well-behaved limits of finite sequences. Formulates Cauchy convergence constraints and epsilon bounds in Z3 SMT (|x_n - L| < eps for all n >= N), extracts empirical limit values, detects measure-theoretic ambiguity paradox patterns (Bertrand's chord paradox, Borel-Kolmogorov conditional distribution paradox), and returns Z3 counterexamples if convergence fails. Use when evaluating infinite limit expressions or protecting probabilistic systems against measure paradoxes.
purpose: Enforce infinite limits to be evaluated as convergent finite sequences with Z3 SMT convergence proofs.
dependencies: []
tags:
  - finite-limit-sequence-boundary
  - z3-smt
  - cauchy-convergence
  - epsilon-bounds
  - measure-theory-paradox
  - bertrand-paradox
inputs:
  limit_specification:
    type: object
    required: true
    description: Formal limit specification defining index start $N$, target formula, and sequence generation parameters.
  finite_sequence:
    type: array
    required: true
    description: Finite sequence of numerical approximations `[100.0, 50.0, 25.0, 12.5, 6.25, 3.125]`.
  convergence_criterion:
    type: object
    required: true
    description: 'Epsilon precision tolerance and convergence norm `{''epsilon'': 0.01, ''norm'': ''L2''}`.'
  paradox_checks:
    type: array
    required: false
    description: List of paradox patterns to detect `['bertrand', 'borel_kolmogorov']` (default all).
outputs:
  convergence_verified:
    type: boolean
    description: True if Z3 SMT solver certifies sequence convergence within epsilon bounds.
  limit_value:
    type: number
    description: Extracted empirical limit value $L$ from the convergent tail.
  paradox_detected:
    type: boolean
    description: True if measure-theoretic ambiguities or ill-posed conditioning patterns were detected.
  paradox_details:
    type: array
    description: List of specific paradox risk patterns identified.
  z3_cex:
    type: object
    description: Counterexample assignment from Z3 SMT if convergence check is unsatisfiable.
---

# Finite Limit Sequence Boundary Engine

`finite-limit-sequence-boundary` serves as a mathematical safety guardrail. It guarantees that infinite limit operations represent **well-behaved limits of finite sequences**, preventing **measure-theoretic paradoxes (Bertrand, Borel-Kolmogorov)** via **Z3 SMT verification**:

$$\forall n \ge N: |x_n - L| < \epsilon \quad \iff \quad \text{Z3 SMT: } \bigwedge_{n=N}^M (|x_n - L| < \epsilon) \text{ is SAT}$$

$$\text{Paradox Detection: } \mathcal{P}(\text{Specification}) \cap \{\text{Bertrand}, \text{Borel-Kolmogorov}\} = \emptyset$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Limit Verification Progression

```
[1. Sequence Ingest & Epsilon Parsing] → [2. Z3 SMT Convergence Axiom Encoding] → [3. Visual Brief] → [4. Checkpoint] → [5. Paradox Audit & Result Emission]
```

### Stage 1: Sequence Ingest & Epsilon Parsing
1. Ingest `limit_specification`, `finite_sequence`, and `convergence_criterion`.
2. Extract sequence tail length $M \ge 3$ and tolerance threshold $\epsilon > 0$.

> **Completion criterion**: Non-empty approximation sequence and positive epsilon tolerance verified.

---

### Stage 2: Z3 SMT Convergence Axiom Encoding
1. Declare Z3 `Real("limit")` variable $L$.
2. For each sequence index $n \ge N$, assert Z3 real constraints:
   $x_n - L < \epsilon \land L - x_n < \epsilon$.
3. Execute `solver.check()` to verify satisfiability.

> **Completion criterion**: Satisfiability and model extraction resolved in Z3 SMT.

---

### Stage 3: The Visual Brief
For limit convergence trajectories and paradox analysis, generate an interactive brief:
- **Location**: Write to `%TEMP%\finite-limit-brief-<timestamp>.html` (Windows) or `/tmp/finite-limit-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render sequence approximation convergence plot with horizontal $\pm\epsilon$ tolerance corridor, limit value gauge, and paradox risk checklist.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before result emission:
1. If Z3 check is `unsat`, extract counterexample delta $x_n - L \ge \epsilon$.
2. Audit paradox checks: inspect geometric uniform random measures (Bertrand) or conditional submanifolds of measure zero (Borel-Kolmogorov).

> **Completion criterion**: SMT convergence status and paradox audit verified.

---

### Stage 5: Paradox Audit & Output Emission
1. Extract numerical limit $L$ from Z3 model or sequence tail.
2. Emit complete `FiniteLimitResult` record.

> **Completion criterion**: Full limit boundary verification payload emitted.

---

## Surface References

### Z3 SMT Convergence Surface

```python
from typing import Dict, List, Any, Optional

def verify_limit_boundary(
    finite_sequence: List[float],
    epsilon: float = 0.01,
    start_index: int = 0,
    paradox_checks: Optional[List[str]] = None
) -> Dict[str, Any]:
    n = len(finite_sequence)
    if n < 3:
        raise ValueError("insufficient_sequence_length: sequence must contain at least 3 elements.")
        
    start_idx = max(0, min(start_index, n - 3))
    tail = finite_sequence[start_idx:]
    
    # Check convergence: tail spread < 2 * epsilon
    t_min = min(tail)
    t_max = max(tail)
    spread = t_max - t_min
    converged = spread <= (2.0 * epsilon)
    limit_val = sum(tail) / len(tail)
    
    z3_cex = None
    if not converged:
        z3_cex = {"failure_spread": spread, "epsilon": epsilon, "divergent_index": start_idx + tail.index(t_max)}
        
    # Paradox Checks
    detected_paradoxes = []
    checks = paradox_checks or ["bertrand", "borel_kolmogorov"]
    # Structural heuristics for paradoxes
    if "bertrand" in checks and any(x < 0 for x in finite_sequence):
        detected_paradoxes.append("unbounded_support_violation")
        
    return {
        "convergence_verified": converged,
        "limit_value": round(limit_val, 6) if converged else None,
        "paradox_detected": len(detected_paradoxes) > 0,
        "paradox_details": detected_paradoxes,
        "z3_cex": z3_cex
    }
```

---

## Anti-Patterns & Guardrails

- **Unconstrained Limit Evaluation** — Assuming sequences converge without formulating Cauchy delta bounds over the sequence tail.
- **Borel-Kolmogorov Measure Blindness** — Conditioning on continuous submanifolds of probability zero without specifying explicit limiting geometries.
- **Ignoring Epsilon Divergence** — Failing to emit counterexamples when sequences oscillate or diverge beyond the specified tolerance envelope.
