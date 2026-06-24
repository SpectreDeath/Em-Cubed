---
name: validate_measurement_level
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog]
description: |
  Guardrail skill enforcing Stevens' measurement hierarchy
  (nominal < ordinal < interval < ratio).  The Prolog layer
  routes deterministic test-selection decisions without any
  numerical computation.
compatibility: PROLOG
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

# Validate Measurement Level

## Purpose
Enforce Stevens' measurement hierarchy and resolve data-typing questions using pure first-order logic.

## Description
This skill is entirely symbolic: no numerical computation is performed. It routes test decisions by examining declared or inferred data properties:
- nominal: categorical labels with no inherent order
- ordinal: ranked categories with meaningful order but unequal intervals
- interval: numeric with meaningful differences but no true zero
- ratio: numeric with meaningful differences AND a true zero

## Prolog Surface (prelude.pl)

```prolog
:- module(measurement_validator, [
    validate_level/4,
    dominates/2,
    routing_permission/2,
    assert_level/3
]).

% ============================================================
% 1. Measurement hierarchy (transitive dominance)
% ============================================================
dominates(ratio,    interval).
dominates(interval, ordinal).
dominates(ordinal,  nominal).

% ============================================================
% 2. Semantic-hint → level resolution
%    Hint atoms are asserted by the Python layer when a column
%    is first declared or loaded.  The Prolog layer resolves the
%    final measurement level.
% ============================================================
validate_level(_D, _C, hint(ratio),     ratio).
validate_level(_D, _C, hint(interval),  interval).
validate_level(_D, _C, hint(ordinal),   ordinal).
validate_level(_D, _C, hint(nominal),   nominal).

% Fallback: previously asserted level takes precedence if hint is absent
validate_level(D, C, _Hint, Level) :-
    known_level(D, C, Level).

% ============================================================
% 3. Asserting a known level into the belief store
%    Called by Python after semantic inference (e.g., dtype, domain
%    knowledge).  The assertion is a side-effect stored in agent state.
% ============================================================
assert_level(Dataset, Column, Level) :-
    ( dominates(Level, _) ; Level = nominal ),
    !,
    retractall(known_level(Dataset, Column, _)),
    asserta(known_level(Dataset, Column, Level)).

% ============================================================
% 4. Test families and their permitted measurement levels
% ============================================================
valid_measurement_for(Test, Level) :-
    parametric_test(Test), !,
    (Level = interval ; Level = ratio).

valid_measurement_for(Test, Level) :-
    non_parametric_test(Test), !,
    (Level = ordinal  ; Level = interval ; Level = ratio).

valid_measurement_for(chi_square, nominal).

valid_measurement_for(correlation_pearson, Level) :-
    (Level = interval ; Level = ratio).

valid_measurement_for(correlation_spearman, Level) :-
    (Level = ordinal  ; Level = interval ; Level = ratio).

% ============================================================
% 5. Test family membership (for documentation / routing)
% ============================================================
parametric_test(t_test_independent).
parametric_test(t_test_paired).
parametric_test(pearson_r).
parametric_test(one_way_anova).
parametric_test(linear_regression).

non_parametric_test(mann_whitney_u).
non_parametric_test(wilcoxon_signed_rank).
non_parametric_test(spearman_rho).
non_parametric_test(kruskal_wallis).
non_parametric_test(friedman).
non_parametric_test(chi_square).

% ============================================================
% 6. Routing permission
% ============================================================
routing_permission(Test, allowed) :-
    validate_level(_, _, _, Level),
    valid_measurement_for(Test, Level).

routing_permission(Test, blocked) :-
    validate_level(_, _, _, Level),
    \+ valid_measurement_for(Test, Level).
```

## Inputs / Outputs

### Inputs

| parameter | type | description |
|---|---|---|
| dataset_id | atom | Identifier for the dataset (used as Prolog variable) |
| column | atom | The column/variable name being assessed |
| semantic_hint | atom or None | Optional hint: `ratio`, `interval`, `ordinal`, `nominal` |

### Outputs

| return | type | description |
|---|---|---|
| measurement_level | atom | One of: `ratio`, `interval`, `ordinal`, `nominal`, `unknown` |
| routing_permission | tuple | `(Test, allowed)` or `(Test, blocked)` |

## Error Handling
| Error | Condition | Behavior |
|---|---|---|
| hint_contradiction | Two conflicting hints asserted for same column | Last assertion wins; warning emitted |
| unbound_variable | Column never declared in dataset | Returns `measurement_level(unknown)` |
| invalid_level | Attempt to assert unsupported level atom | Fails silently; valid levels are ratio/interval/ordinal/nominal |

## State Updates
- `belief_add(known_level(DatasetId, ColumnName, Level))`
- `belief_add(routing_permission(TestName, Status))`

## Example Prolog Queries

```text
% Assert a column as ratio
?- assert_level('sales_data', 'revenue', ratio).
true.

% Query: is pearson_r allowed for this column?
?- validate_level('sales_data', 'revenue', _, Level),
   routing_permission(pearson_r, Status).
Level = ratio,
Status = allowed.

% Query: is chi_square allowed (requires nominal)?
?- validate_level('sales_data', 'revenue', _, Level),
   routing_permission(chi_square, Status).
Level = ratio,
Status = blocked.

% Query: check dominance
?- dominates(ratio, X).
X = interval.
?- dominates(interval, X).
X = ordinal.
?- dominates(ordinal, X).
X = nominal.
```

## Security Considerations
- Pure declarative reasoning; no I/O, no external calls.
- Assertions modify the in-memory belief store; the runtime is responsible for scoping/cleanup.
