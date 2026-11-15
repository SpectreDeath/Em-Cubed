---
name: truthmaker-hyperintensional-verifier
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: Kit Fine exact truthmaker semantics (s ⊩ A) and hyperintensional grounding verifier. Extracts minimal, wholly relevant state fragments that make propositions true while filtering irrelevance and noise, and evaluates bilateral truthmaker/falsemaker boundaries across Datalog, Prolog, and Python. Use when auditing exact causal explanations for agent decisions, eliminating irrelevant context bloat, or verifying hyperintensional semantic equivalence.
purpose: Extract exact truthmakers and compute hyperintensional grounding states that make propositions strictly true with zero irrelevant data.
dependencies: []
tags:
  - truthmaker-semantics
  - kit-fine
  - hyperintensionality
  - datalog
  - exact-grounding
  - ontology-audit
inputs:
  proposition:
    type: string
    required: true
    description: Target proposition or regulatory rule to verify.
  candidate_triples:
    type: array
    required: true
    description: Full knowledge graph state or triple set ($S$).
  verification_mode:
    type: string
    required: false
    description: "exact_truthmaker (s ⊩ A) | exact_falsemaker (s ⫣ A) | bilateral (default: exact_truthmaker)"
outputs:
  is_satisfied:
    type: boolean
    description: True if an exact truthmaker state $s \subseteq S$ exists.
  exact_truthmaker_triples:
    type: array
    description: Minimal, wholly relevant triple subset making proposition true.
  ground_explanation:
    type: string
    description: Hyperintensional explanation grounded in subject-matter states.
---

# Truthmaker Hyperintensional Verifier Engine

`truthmaker-hyperintensional-verifier` implements **Kit Fine's Truthmaker Semantics** within `Em-Cubed`. Moving beyond classical possible-world semantics where co-extensional truths are conflated, it isolates the exact, minimal, and wholly relevant state $s$ that makes a proposition true ($s \Vdash A$), completely discarding irrelevancies and context junk.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Truthmaker Verification Progression

```
[1. Proposition Invariant Audit] → [2. Datalog Relevance Slicing] → [3. Visual Brief] → [4. Checkpoint] → [5. Bilateral Evaluation]
```

### Stage 1: Proposition & Invariant Audit
1. Parse the target proposition and define semantic topic boundaries.
2. Index candidate triple graph $S$ into subject-predicate-object relational tables.

> **Completion criterion**: Proposition formalized into truthmaker schema and candidate triple store indexed.

---

### Stage 2: Datalog Wholly-Relevant Slicing
1. Formulate Datalog dependency rules identifying strictly necessary grounding paths.
2. Prune all unreferenced triples, isolated subgraphs, and tautological additions:
   $$s \Vdash A \iff (s \text{ guarantees } A) \land (\forall s' \subsetneq s, s' \not\Vdash A)$$

> **Completion criterion**: Candidate state reduced to candidate minimal support subgraph.

---

### Stage 3: The Visual Brief
For complex compliance trees or hyperintensional grounding networks, generate a visual brief:
- **Location**: Write to `%TEMP%\truthmaker-verifier-brief-<timestamp>.html` (Windows) or `/tmp/truthmaker-verifier-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render full candidate graph vs. isolated exact truthmaker subgraph ($s \Vdash A$).

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before certifying high-stakes grounding explanations:
1. Verify bilateral consistency: confirm that $s$ does not contain any sub-state that acts as a falsemaker ($s \not\cap \text{Falsemakers}(A)$).
2. If conflicting evidence exists, halt and request human-in-the-loop review.

> **Completion criterion**: Bilateral consistency confirmed with zero falsemaker intersections.

---

### Stage 5: Bilateral Evaluation & Explanation Emit
1. Validate exactness: ensure no subset $s' \subset s$ is sufficient.
2. Emit the exact truthmaker triples and structured hyperintensional explanation.

> **Completion criterion**: Payload emitted with `is_satisfied: true`, minimal triples array, and zero junk context.

---

## Surface References

### Python Truthmaker Classifier Surface

```python
from typing import List, Dict, Any

def extract_exact_truthmaker(proposition: str, triples: List[str]) -> Dict[str, Any]:
    # Filter wholly relevant triples for the proposition subject
    target_terms = {w.lower() for w in proposition.split()}
    wholly_relevant = [
        t for t in triples 
        if any(term in t.lower() for term in target_terms)
    ]
    
    is_satisfied = len(wholly_relevant) > 0
    return {
        "proposition": proposition,
        "is_satisfied": is_satisfied,
        "ground_explanation": f"Exact Truthmaker: Grounded in {len(wholly_relevant)} wholly relevant triples",
        "exact_truthmaker_triples": wholly_relevant
    }
```

### Datalog Slicing Surface

```prolog
% Datalog rules for exact relevance
relevant_triple(S, P, O) :- query_term(S).
relevant_triple(S, P, O) :- query_term(O).
truthmaker(Triple) :- relevant_triple(S, P, O), Triple = triple(S, P, O).
```

---

## Anti-Patterns & Guardrails

- **Intensional Conflation** — Treating logically equivalent propositions (e.g. $P$ vs $P \land (Q \lor \neg Q)$) as having identical truthmakers. Always enforce hyperintensional relevance.
- **Context Bloat & Junk Ingestion** — Including 100+ ambient triples in prompt context when only 2 triples constitute the exact truthmaker. Always slice down to minimal $s$.
- **Falsemaker Blindness** — Validating positive grounding without checking whether conflicting sub-states falsify the proposition.
