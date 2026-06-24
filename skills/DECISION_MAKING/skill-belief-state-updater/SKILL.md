---
name: skill-belief-state-updater
domain: DECISION_MAKING
version: 1.0.0
surfaces:
- hy
- python
description: 'Continuous probability mass redistribution skill that consumes structural outputs from lattice-inclusion-exclusion-sum
  and re-allocates probability mass across surviving lattice configurations when hard solvers prune opponent strategies. Produces
  a normalized Bayesian belief-state density.

  '
purpose: 'Transition from hard binary strategy pruning to continuous belief-state weighting by re-allocating eliminated probability
  mass to surviving strategies using normalized Bayesian updates.

  '
dependencies:
- decision-making/lattice-inclusion-exclusion-sum
tags:
- belief-state
- bayesian-update
- probability-mass
- lattice
- jaynes
- hy
- python
- decision-making
inputs:
  active_strategies:
    type: array
    required: true
    description: List of strategy indices that survived elimination
  eliminated_strategies:
    type: array
    required: true
    description: List of strategy indices that were pruned by hard solver
  prior_weights:
    type: object
    required: true
    description: Prior probability weights dict[int, float] before elimination
outputs:
  updated_belief_state:
    type: object
    description: Updated density mapping dict[int, float] over surviving strategies
  normalization_factor:
    type: float
    description: Factor used to normalize remaining probability mass to 1.0
  eliminated_mass:
    type: float
    description: Total probability mass redistributed from eliminated strategies
  update_log:
    type: array
    description: Per-strategy record of weight transitions
---

# Skill Belief State Updater

Continuous probability mass redistribution for Bayesian belief-state
updates after hard solver elimination. Hy surface handles symbolic
bidirectional logic; Python surface handles numerical normalization.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | Python  | Parse `active_strategies`, `eliminated_strategies`, `prior_weights` |
| 2  | Python  | Compute total eliminated probability mass              |
| 3  | Hy      | Define symbolic Bayesian update rules via Hy Lisp      |
| 4  | Hy      | Verify lattice closure of surviving strategy set       |
| 5  | Python  | Re-allocate eliminated mass proportionally to active strategies |
| 6  | Python  | Normalize updated weights to sum to 1.0               |
| 7  | Python  | Return `updated_belief_state`, `normalization_factor`, `update_log` |

$$\hat{p}_i = \frac{p_i}{\sum_{j \in S_{active}} p_j} \quad \forall i \in S_{active}$$

## Surfaces

### Hy Surface

```hy
;; Symbolic Bayesian update rules
(defn redistribute-mass [active eliminated priors]
  "Re-allocate probability mass from eliminated to active strategies"
  (let [eliminated-mass (sum (list (get priors s) (for [s eliminated])))
        active-priors   (sum (list (get priors s) (for [s active])))
        norm-factor      (/ 1.0 active-priors)]
    {:normalization_factor norm-factor
     :eliminated_mass eliminated-mass
     :update_type "proportional_redistribution"}))

;; Lattice closure verification
(defn lattice-closed? [strategies]
  "Verify surviving strategies form a closed lattice subset"
  (all (list (has-upper-bound strategies)
             (has-lower-bound strategies)
             (meet-closed strategies)
             (join-closed strategies))))
```

### Python Surface

```python
surfaces.skill_belief_state_updater.update(
    active_strategies=[0, 2, 3],
    eliminated_strategies=[1],
    prior_weights={0: 0.25, 1: 0.15, 2: 0.35, 3: 0.25}
)
# Result: updated_belief_state = {0: 0.294, 2: 0.412, 3: 0.294}
#         normalization_factor = 1.176
#         eliminated_mass = 0.15
```

## Capability Contract

**Inputs:**

- `active_strategies` *(array, required)* — Strategy indices that survived elimination.
- `eliminated_strategies` *(array, required)* — Strategy indices pruned by hard solver.
- `prior_weights` *(object, required)* — Prior probability weights before elimination.

**Outputs:**

- `updated_belief_state` *(object)* — Updated density mapping over surviving strategies.
- `normalization_factor` *(float)* — Factor used to normalize remaining mass to 1.0.
- `eliminated_mass` *(float)* — Total probability mass redistributed.
- `update_log` *(array)* — Per-strategy record of weight transitions.

## Composition

- `lattice-inclusion-exclusion-sum` — Consumes its probability distribution as prior input.
- `iterated-dominance-solver` — Feeds `eliminated_strategies` from elimination history.
- `skill-expected-utility-maximizer` — Consumes `updated_belief_state` as opponent model.
- `skill-bounded-rationality-constraint` — Receives convergence metrics from update iterations.
