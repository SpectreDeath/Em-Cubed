---
name: associative-chaining-product
domain: DECISION_MAKING
version: 1.0.0
surfaces:
  - python
  - prolog
description: Chains conditional probability distributions along directed implication paths in a logical lattice using the Bayesian product rule. Verifies transitive implication chains ($A \implies B \implies C$) in Prolog, extracts intermediate conditional probabilities $P(X_{i} \mid X_{i+1})$, and computes the chained conditional product $P(A \mid C) = \prod_{i=1}^{k-1} P(X_i \mid X_{i+1})$ in Python. Use when performing multi-step Bayesian inference over structured posets, hierarchical taxonomy lattices, or deductive implication chains.
purpose: Compute chained conditional probabilities along lattice implication paths with Prolog topology validation.
dependencies:
  - DECISION_MAKING/lattice-inclusion-exclusion-sum
  - DECISION_MAKING/epistemological-independence-filter
tags:
  - associative-chaining
  - product-rule
  - lattice-path
  - conditional-probability
  - bayesian-inference
  - prolog-validation
inputs:
  probability_distribution:
    type: object
    required: true
    description: 'Map of conditional and marginal probabilities over lattice elements (e.g. `{''P(A|B)'': 0.8, ''P(B|C)'': 0.6}`).'
  chain_elements:
    type: array
    required: true
    description: Ordered implication path sequence `['A', 'B', 'C']` where $A \implies B \implies C$.
  target_conditional:
    type: object
    required: true
    description: 'Target conditional specification `{''given'': ''C'', ''target'': ''A''}`.'
outputs:
  chained_probability:
    type: number
    description: Evaluated conditional probability $P(\text{target} \mid \text{given})$ computed via the product rule.
  chain_validation:
    type: object
    description: Diagnostic record confirming validity of each implication link in the chain.
  decomposition:
    type: object
    description: Detailed breakdown of each individual conditional probability factor.
---

# Associative Chaining Product Engine

`associative-chaining-product` evaluates multi-step conditional probabilities along directed implication paths in a deductive lattice poset. It proves **transitive implication in Prolog** and computes the **Bayesian product rule decomposition** in **Python**:

$$P(A \mid C) = P(A \mid B) \cdot P(B \mid C) \quad \text{when } A \implies B \implies C$$

$$P(X_1 \mid X_k) = \prod_{i=1}^{k-1} P(X_i \mid X_{i+1})$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Chaining Progression

```
[1. Path Ingest & Target Invariant Audit] → [2. Prolog Implication Chain Proof] → [3. Visual Brief] → [4. Checkpoint] → [5. Product Rule Evaluation & Emit]
```

### Stage 1: Path Ingest & Target Invariant Audit
1. Ingest `probability_distribution`, `chain_elements` array ($k \ge 2$), and `target_conditional`.
2. Verify that start element matches `target_conditional.target` and terminal element matches `target_conditional.given`.

> **Completion criterion**: Clean implication path payload verified.

---

### Stage 2: Prolog Implication Chain Proof
1. Prove pairwise implication for every consecutive link $(X_i, X_{i+1})$ in Prolog:
   ```prolog
   chain_valid([X, Y|Rest]) :- implies(X, Y), chain_valid([Y|Rest]).
   ```
2. Verify that intermediate conditional probabilities $P(X_i \mid X_{i+1})$ exist in the distribution map.

> **Completion criterion**: Implication chain validity certified in Prolog.

---

### Stage 3: The Visual Brief
For chained Bayesian inference and implication trees, generate an interactive brief:
- **Location**: Write to `%TEMP%\associative-chaining-brief-<timestamp>.html` (Windows) or `/tmp/associative-chaining-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render directed implication chain graph with link conditional probabilities, term-by-term product waterfall chart, and target probability result card.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before computing product:
1. Verify that all intermediate factors satisfy $0.0 \le P(X_i \mid X_{i+1}) \le 1.0$.
2. Check for zero-probability links: if any link is 0, the entire chained probability collapses to 0.0.

> **Completion criterion**: Probability bound invariants certified.

---

### Stage 5: Product Rule Evaluation & Output Emission
1. Compute multiplicative product: $P_{\text{chained}} = \prod_{i=1}^{k-1} P(X_i \mid X_{i+1})$.
2. If direct $P(A \mid C)$ is supplied, compute consistency residual $\Delta = |P_{\text{chained}} - P_{\text{direct}}|$.
3. Emit complete `ChainingResult` record.

> **Completion criterion**: Full associative chaining product payload emitted.

---

## Surface References

### Prolog Verification Surface

```prolog
:- module(associative_chaining, [
    chain_valid/1,
    chain_probability/3
]).

implies(A, B) :- subconcept(A, B).
implies(A, A).

chain_valid([_]).
chain_valid([X, Y|Rest]) :-
    implies(X, Y),
    chain_valid([Y|Rest]).
```

### Python Calculation Surface

```python
from typing import Dict, List, Any

def chain_conditional_product(
    probability_distribution: Dict[str, float],
    chain_elements: List[str],
    target_conditional: Dict[str, str]
) -> Dict[str, Any]:
    if len(chain_elements) < 2:
        raise ValueError("invalid_chain: Chain must contain at least 2 elements.")
        
    target = target_conditional.get("target")
    given = target_conditional.get("given")
    
    if chain_elements[0] != target or chain_elements[-1] != given:
        raise ValueError(f"chain_endpoint_mismatch: Chain {chain_elements[0]}->{chain_elements[-1]} != target {target}|{given}.")
        
    product = 1.0
    decomposition = {}
    validations = []
    
    for i in range(len(chain_elements) - 1):
        src, dst = chain_elements[i], chain_elements[i + 1]
        key1 = f"P({src}|{dst})"
        key2 = f"{src}|{dst}"
        
        prob = probability_distribution.get(key1, probability_distribution.get(key2))
        if prob is None:
            raise KeyError(f"missing_conditional: No probability found for {key1}.")
            
        if not (0.0 <= prob <= 1.0):
            raise ValueError(f"invalid_probability: {key1} = {prob} outside [0, 1].")
            
        decomposition[key1] = prob
        validations.append({"link": f"{src}->{dst}", "probability": prob, "valid": True})
        product *= prob
        
    return {
        "chained_probability": round(product, 6),
        "chain_validation": {
            "is_valid": True,
            "links": validations,
            "chain_length": len(chain_elements)
        },
        "decomposition": decomposition
    }
```

---

## Anti-Patterns & Guardrails

- **Broken Implication Links** — Chaining across non-implicative lattice elements without monotonic containment ($A \not\implies B$).
- **Reversed Conditional Ordering** — Conflating $P(A \mid B)$ with $P(B \mid A)$ during forward implication path traversal.
- **Unbounded Multiplicative Drift** — Long chains of probability products leading to underflow without log-sum-exp checks.
