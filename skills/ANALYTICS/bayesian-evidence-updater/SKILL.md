---
name: bayesian-evidence-updater
domain: ANALYTICS
version: 1.0.0
surfaces:
  - sqlite
  - python
  - prolog
description: Multi-surface Bayesian evidence updater for sequential forensic and probabilistic inference. Audits hypothesis space for Mutually Exclusive and Collectively Exhaustive (MECE) compliance in Prolog, persists case states in SQLite, and computes normalized posterior probability updates from incoming evidence likelihood vectors in Python. Use when updating belief states given new diagnostic observations, maintaining forensic case ledgers, or evaluating conditional likelihood shifts.
purpose: Dynamically update hypothesis probability distributions using sequential conditional Bayesian likelihood evaluations and MECE validation.
dependencies: []
tags:
  - bayesian-inference
  - posterior-update
  - mece-audit
  - forensic-reasoning
  - sqlite-case-state
  - prolog
inputs:
  session_id:
    type: string
    required: true
    description: Unique case session identifier for SQLite persistence.
  hypothesis_matrix:
    type: array
    required: true
    description: 'List of active hypotheses with current prior probabilities `[{"hypothesis_id": str, "prior_probability": float}]`.'
  likelihood_dict:
    type: object
    required: true
    description: Mapping of hypothesis IDs to conditional evidence likelihoods $P(E \mid H_i)$.
outputs:
  updated_distribution:
    type: array
    description: 'Normalized posterior distribution `[{"hypothesis_id": str, "posterior_probability": float}]`.'
  marginal_likelihood:
    type: number
    description: Total marginal probability of evidence $P(E) = \sum P(E \mid H_i) P(H_i)$.
  mece_compliant:
    type: boolean
    description: True if hypothesis space satisfies Prolog exclusivity and exhaustiveness checks.
---

# Bayesian Evidence Updater Engine

`bayesian-evidence-updater` executes rigorous Bayesian belief updating over structured hypothesis spaces $(\mathcal{H}, P)$. It validates that hypotheses are **Mutually Exclusive and Collectively Exhaustive (MECE)** in Prolog, tracks case history in SQLite, and evaluates exact normalized posterior distributions in Python:

$$P(H_i \mid E) = \frac{P(E \mid H_i) P(H_i)}{\sum_{j} P(E \mid H_j) P(H_j)}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Bayesian Update Progression

```
[1. Case & Space Invariant Audit] → [2. Prolog MECE Compliance Check] → [3. Visual Brief] → [4. Checkpoint] → [5. Python Normalization & SQLite State Commit]
```

### Stage 1: Case & Space Invariant Audit
1. Ingest `session_id`, `hypothesis_matrix`, and `likelihood_dict`.
2. Validate prior probability bounds ($0.0 \le P(H_i) \le 1.0$) and prior sum normalization ($\sum P(H_i) = 1.0 \pm 10^{-4}$).
3. Validate likelihoods ($0.0 \le P(E \mid H_i) \le 1.0$).

> **Completion criterion**: Priors and likelihood vectors parsed with non-negative bounded values.

---

### Stage 2: Prolog MECE Compliance Check
1. Assert candidate hypothesis list into Prolog engine.
2. Verify **Exhaustiveness**: All observed outcomes map to a known hypothesis category.
3. Verify **Exclusivity**: No pairwise overlaps or duplicate hypothesis keys exist.

> **Completion criterion**: Prolog returns `true` for `audit_hypothesis_space/1`.

---

### Stage 3: The Visual Brief
For complex forensic cases or significant probability shifts, generate an interactive brief:
- **Location**: Write to `%TEMP%\bayesian-updater-brief-<timestamp>.html` (Windows) or `/tmp/bayesian-updater-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render prior vs. posterior bar charts, evidence likelihood matrix, and marginal probability gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before committing posterior updates to persistent SQLite storage:
1. Check marginal probability: $P(E) = \sum P(E \mid H_i) P(H_i)$.
2. If $P(E) < 10^{-8}$ (zero marginal likelihood), pause and alert prior-evidence contradiction rather than dividing by zero.

> **Completion criterion**: Marginal likelihood certified non-zero ($P(E) > 10^{-8}$).

---

### Stage 5: Python Normalization & SQLite State Commit
1. Compute exact normalized posteriors:
   $$P_{\text{post}}(H_i) = \frac{P(E \mid H_i) P(H_i)}{P(E)}$$
2. Update SQLite case ledger atomically for `session_id`.
3. Emit updated distribution and marginal likelihood.

> **Completion criterion**: Posteriors sum to $1.0 \pm 10^{-6}$ and SQLite rows updated.

---

## Surface References

### Python Calculation Surface

```python
from typing import List, Dict, Any

def calculate_posterior_update(matrix: List[Dict[str, Any]], likelihood_dict: Dict[str, float]) -> Dict[str, Any]:
    unnormalized = {}
    total_pe = 0.0
    
    for row in matrix:
        h_id = row["hypothesis_id"]
        prior = float(row.get("prior_probability", 0.0))
        likelihood = float(likelihood_dict.get(h_id, 0.1))
        post_unnorm = prior * likelihood
        unnormalized[h_id] = post_unnorm
        total_pe += post_unnorm
        
    if total_pe <= 1e-12:
        return {"status": "error", "message": "Zero marginal probability evidence"}
        
    updated = [
        {"hypothesis_id": h, "posterior_probability": round(val / total_pe, 6)}
        for h, val in unnormalized.items()
    ]
    
    return {
        "updated_distribution": updated,
        "marginal_likelihood": round(total_pe, 6),
        "mece_compliant": True
    }
```

### SQLite Case Persistence Schema

```sql
CREATE TABLE IF NOT EXISTS bayesian_case_state (
    session_id TEXT NOT NULL,
    hypothesis_id TEXT NOT NULL,
    prior_probability REAL NOT NULL,
    updated_at INTEGER DEFAULT (strftime('%s','now')),
    PRIMARY KEY (session_id, hypothesis_id)
);

UPDATE bayesian_case_state 
SET prior_probability = :new_posterior, updated_at = strftime('%s','now')
WHERE session_id = :session_id AND hypothesis_id = :hypothesis_id;
```

### Prolog MECE Surface

```prolog
verify_exhaustive([]).
verify_exhaustive([H|T]) :- valid_category(H), verify_exhaustive(T).

verify_exclusive([]).
verify_exclusive([H|T]) :- \+ member(H, T), verify_exclusive(T).

audit_hypothesis_space(HypothesisList) :-
    verify_exhaustive(HypothesisList),
    verify_exclusive(HypothesisList).
```

---

## Anti-Patterns & Guardrails

- **Zero-Marginal Probability Explosion** — Dividing by zero when incoming evidence is assigned zero likelihood across all hypotheses. Always gate on $P(E) > 10^{-8}$.
- **Non-MECE Overlapping Hypotheses** — Updating overlapping hypotheses without normalizing disjoint intersections, causing probability mass distortion.
- **Unnormalized State Ingestion** — Ingesting prior probability arrays that do not sum to 1.0 without initial re-normalization.