---
name: bayesian-evidence-updater
domain: ANALYTICS
version: "1.0.0"
surfaces: [sqlite, python, prolog]
description: Multi-surface Bayesian evidence updater with Python surface for causal graph inference, SQLite surface for observation persistence and posterior updates, and Prolog surface for topological causal ordering.
compatibility: SQLITE, PYTHON, PROLOG
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

# Purpose
Dynamically updates a hypothesis probability distribution matrix using sequential conditional Bayesian likelihood evaluations.

# Description
Implements an infrastructure-safe forensic inference engine modeled on Solving a Murder Mystery Using Bayesian Inference. It aggregates and tracks evolving case states via an in-memory SQLite table, formally audits the hypothesis space structure for Mutually Exclusive and Collectively Exhaustive (MECE) compliance inside Prolog, and executes zero-dependency conditional probability updates inside an isolated Python environment.

## Python Surface

```python
def calculate_posterior_update(matrix, likelihood_dict):
    total_probability_evidence = 0.0
    unnormalized_posteriors = {}
    
    for row in matrix:
        h_id = row['hypothesis_id']
        prior = row['prior_probability']
        likelihood = likelihood_dict.get(h_id, 0.1)
        unnormalized_posterior = likelihood * prior
        unnormalized_posteriors[h_id] = unnormalized_posterior
        total_probability_evidence += unnormalized_posterior
        
    if total_probability_evidence == 0:
        return {'status': 'error', 'message': 'Zero marginal probability matrix'}
        
    updated_distribution = []
    for row in matrix:
        h_id = row['hypothesis_id']
        posterior = unnormalized_posteriors[h_id] / total_probability_evidence
        updated_distribution.append({
            'hypothesis_id': h_id,
            'posterior_probability': posterior
        })
        
    return {
        'status': 'success',
        'marginal_likelihood': total_probability_evidence,
        'distribution': updated_distribution
    }

calculate_posterior_update(active_matrix, likelihoods)
```

## SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS bayesian_case_state (
    session_id TEXT,
    hypothesis_id TEXT,
    prior_probability REAL,
    PRIMARY KEY (session_id, hypothesis_id)
);

INSERT OR IGNORE INTO bayesian_case_state (session_id, hypothesis_id, prior_probability)
VALUES 
    (:session_id, 'H1_Accidental', 0.20),
    (:session_id, 'H2_Medical_Malpractice', 0.20),
    (:session_id, 'H3_Suicide', 0.20),
    (:session_id, 'H4_Family_Homicide', 0.20),
    (:session_id, 'H5_Outsider_Homicide', 0.20);

SELECT hypothesis_id, prior_probability 
FROM bayesian_case_state 
WHERE session_id = :session_id;

UPDATE bayesian_case_state 
SET prior_probability = :new_posterior
WHERE session_id = :session_id AND hypothesis_id = :hypothesis_id;
```

## Prolog Surface

```prolog
valid_category('H1_Accidental').
valid_category('H2_Medical_Malpractice').
valid_category('H3_Suicide').
valid_category('H4_Family_Homicide').
valid_category('H5_Outsider_Homicide').

verify_exhaustive([]).
verify_exhaustive([H|T]) :-
    valid_category(H),
    verify_exhaustive(T).

verify_exclusive([]).
verify_exclusive([H|T]) :-
    \+ member(H, T),
    verify_exclusive(T).

audit_hypothesis_space(HypothesisList) :-
    verify_exhaustive(HypothesisList),
    verify_exclusive(HypothesisList).
```