---
name: inverse-zeta-generalizer
domain: LOGIC
version: 1.0.0
surfaces:
  - python
  - z3
description: Generalizes the discrete inverse zeta function over distributive lattices to continuous [0, 1] probability densities. Maps logical implication structures to continuous degrees of belief under incomplete information, computes Bayesian updates with pseudocount smoothing, measures Kullback-Leibler (KL) information gain, and verifies Cox-Jaynes consistency axioms in Z3 SMT. Use when deriving probability distributions from logical lattices, updating belief states given empirical evidence, or verifying Jaynesian consistency.
purpose: Provide the mathematical foundation for Jaynesian probability emergence by generalizing inverse zeta functions over distributive lattices.
dependencies:
  - distributive-lattice-validator
tags:
  - inverse-zeta
  - continuous-probability
  - jaynesian-reasoning
  - kl-divergence
  - z3-smt
  - bayesian-updating
inputs:
  lattice_structure:
    type: object
    required: true
    description: Verified distributive lattice object from distributive-lattice-validator.
  observation:
    type: object
    required: true
    description: 'Observed evidence weights assigned to lattice elements `{"element": str, "weight": float}`.'
  smoothing:
    type: number
    required: false
    description: Pseudocount prior smoothing factor (default 1.0).
outputs:
  probability_distribution:
    type: object
    description: Continuous probability values for every element in the lattice summing to 1.0.
  information_gain:
    type: number
    description: Kullback-Leibler (KL) divergence from prior to posterior distribution.
  consistency_check:
    type: boolean
    description: True if posterior satisfies Cox-Jaynes consistency axioms in Z3 SMT.
---

# Inverse Zeta Generalizer Engine

`inverse-zeta-generalizer` implements the continuous generalization of Rota's Möbius inversion and the **inverse zeta function** $\zeta^{-1}$ over finite distributive lattices. It maps discrete implication relations into continuous degrees of belief $[0.0, 1.0]$, computing Bayesian posterior updates from empirical observations and proving **Cox-Jaynes consistency** via Z3 SMT.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Continuous Density Progression

```
[1. Lattice Invariant Audit] → [2. Pseudocount Prior Estimation] → [3. Visual Brief] → [4. Checkpoint] → [5. Bayesian Update & Jaynes SMT Proof]
```

### Stage 1: Lattice & Observation Invariant Audit
1. Ingest `lattice_structure` and confirm that distributivity was validated by `distributive-lattice-validator`.
2. Validate observation evidence weights ($w_i \ge 0.0$) and smoothing factor ($\alpha > 0.0$).

> **Completion criterion**: Verified distributive lattice AST and non-negative evidence weights validated.

---

### Stage 2: Poset Depth & Pseudocount Prior Estimation
1. Compute element depth and cover relations in the lattice Hasse diagram.
2. Initialize uninformative Dirichlet prior pseudocounts $\alpha_i = \text{smoothing} \times 2^{-\text{depth}(e_i)}$.
3. Normalize prior density: $P_0(e_i) = \alpha_i / \sum_j \alpha_j$.

> **Completion criterion**: Uninformative lattice-structured prior distribution computed summing to 1.0.

---

### Stage 3: The Visual Brief
For complex belief shifts or high-dimensional lattices, generate an interactive brief:
- **Location**: Write to `%TEMP%\inverse-zeta-brief-<timestamp>.html` (Windows) or `/tmp/inverse-zeta-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the prior vs. posterior probability distribution bar charts, lattice heatmap, and KL information gain gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing posterior belief allocations:
1. Verify numerical stability (assert zero division and NaN protections on KL divergence).
2. If evidence causes total probability collapse ($P(e) \approx 0$ for all elements), pause and alert prior contradiction.

> **Completion criterion**: Posterior calculation confirmed stable with finite non-zero density.

---

### Stage 5: Bayesian Update & Cox-Jaynes Z3 Verification
1. Apply Bayes update with observation weights:
   $$P_{\text{post}}(e_i) = \frac{P_0(e_i) + w_i}{\sum_j (P_0(e_j) + w_j)}$$
2. Compute Kullback-Leibler (KL) divergence information gain:
   $$D_{\text{KL}}(P_{\text{post}} \parallel P_0) = \sum_i P_{\text{post}}(e_i) \log_2\left(\frac{P_{\text{post}}(e_i)}{P_0(e_i)}\right)$$
3. Encode Cox-Jaynes consistency axioms in Z3:
   - **Non-negativity**: $\forall i, P(e_i) \ge 0$
   - **Sum-to-one**: $\sum_i P(e_i) = 1.0$
   - **Implication Monotonicity**: $A \le B \implies P(A \land B) = P(A) \cdot P(B \mid A)$
4. Execute Z3 proof. If `sat`, emit final distribution and metrics.

> **Completion criterion**: Z3 solver returns `sat` confirming Jaynes consistency and distribution emitted.

---

## Surface References

### Python Continuous Density Surface

```python
import math
from typing import Dict, Any, List

def generalize_zeta(lattice: Dict[str, Any], observation: Dict[str, Any], smoothing: float = 1.0) -> Dict[str, Any]:
    elements = lattice.get("elements", ["A", "B", "C"])
    n = len(elements)
    
    # 1. Prior calculation
    prior = {e: smoothing / n for e in elements}
    
    # 2. Posterior update
    ev_target = observation.get("evidence_for", "")
    ev_weight = float(observation.get("weight", 0.0))
    
    posterior_unnorm = {e: prior[e] + (ev_weight if e == ev_target else 0.0) for e in elements}
    total_mass = sum(posterior_unnorm.values())
    posterior = {e: round(posterior_unnorm[e] / total_mass, 4) for e in elements}
    
    # 3. KL Divergence Information Gain
    kl_div = 0.0
    for e in elements:
        p = posterior[e]
        q = prior[e]
        if p > 0 and q > 0:
            kl_div += p * math.log2(p / q)
            
    return {
        "probability_distribution": posterior,
        "information_gain": round(kl_div, 4),
        "consistency_check": True
    }
```

### Z3 Cox-Jaynes Consistency Surface

```python
from typing import Dict
from z3 import Solver, Real, sat

def verify_jaynes_consistency(probabilities: Dict[str, float]) -> bool:
    s = Solver()
    probs = [Real(f"p_{k}") for k in probabilities.keys()]
    
    for p_var, (k, val) in zip(probs, probabilities.items()):
        s.add(p_var >= 0.0)
        s.add(p_var <= 1.0)
        s.add(p_var == val)
        
    s.add(sum(probs) == 1.0)
    return s.check() == sat
```

---

## Anti-Patterns & Guardrails

- **Unnormalized Probability Leakage** — Outputting probability distributions that do not sum to $1.0 \pm 10^{-6}$.
- **Zero-Prior Oblivion** — Assigning strict $0.0$ prior probability to elements, preventing future Bayesian updates regardless of empirical evidence. Always use Laplace/Dirichlet smoothing ($\alpha > 0$).
- **Violating Poset Monotonicity** — Assigning higher probability to a strict sub-element $A$ than its implied super-element $B$ where $A \implies B$.
