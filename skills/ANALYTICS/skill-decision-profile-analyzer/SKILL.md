---
name: skill-decision-profile-analyzer
version: 1.0.0
domain: ANALYTICS
surfaces:
  - python
  - prolog
  - sqlite
description: >
  Dual-surface decision-profile analyzer that ingests elimination trace
  history from skill-elimination-trace-logger and computes a solver
  personality profile. Python computes the logical-pruning versus
  probabilistic-decay ratio; Prolog asserts static relational facts
  (solver_profile/3) into the running knowledge base.
purpose: >
  Evaluate the active solver's behavioral bias by quantifying the ratio of
  hard-logic pruning to probabilistic mass adjustment across an elimination
  session, making the profile available as a queryable Prolog fact.
dependencies:
  - decision-making/skill-elimination-trace-logger
inputs:
  trace_history_session:
    type: string
    required: true
    description: "Session ID whose elimination trace history to analyze"
  game_type:
    type: string
    required: true
    description: "Game classification label (e.g., 'pd', 'coordination', 'general_sum')"
outputs:
  solver_profile:
    type: object
    description: "Profile with prune_ratio, bias_direction, and confidence"
  hard_logic_count:
    type: integer
    description: "Total HARD_LOGIC tagged eliminations in session"
  probabilistic_decay_count:
    type: integer
    description: "Total PROBABILISTIC_DECAY + EARLY_TERMINATION tags"
  total_steps:
    type: integer
    description: "Total elimination steps analyzed"
  prolog_fact_asserted:
    type: boolean
    description: "True if solver_profile fact was asserted into Prolog"
tags:
  - profile-analysis
  - elimination-trace
  - solver-personality
  - prolog
  - sqlite
  - python
  - analytics
  - diagnostics
---

# Skill Decision Profile Analyzer

Dual-surface analyzer that ingests elimination trace history and computes
solver personality profile. Python computes ratios; Prolog asserts
solver_profile facts for downstream querying.

## Tick Protocol

| Id | Surface | Action                                                |
|----|---------|-------------------------------------------------------|
| 1  | SQLite  | Query elimination_trace table for given `trace_history_session` |
| 2  | SQLite  | GROUP BY metadata_tag to count HARD_LOGIC vs PROBABILISTIC_DECAY |
| 3  | Python  | Compute `prune_ratio = hard_logic / total_steps`      |
| 4  | Python  | Determine `bias_direction`: 'constraint_heavy', 'prior_heavy', or 'balanced' |
| 5  | Prolog  | Assert `solver_profile(Session, Ratio, Bias)` fact    |
| 6  | Python  | Return `solver_profile`, counts, and assertion status |

$$\text{prune\_ratio} = \frac{|S_{hard}|}{|S_{total}|}$$

## Surfaces

### Python Surface

```python
surfaces.skill_decision_profile_analyzer.analyze(
    trace_history_session="session_abc123",
    game_type="general_sum"
)
# Result: solver_profile={"prune_ratio": 0.75, "bias_direction": "constraint_heavy", "confidence": 0.95}
```

### Prolog Surface

```prolog
% Asserted automatically after analysis
solver_profile("session_abc123", 0.75, constraint_heavy).

% Query for downstream use
solver_bias(Session, constraint_heavy) :-
    solver_profile(Session, Ratio, Bias),
    Ratio > 0.6,
    !.
```

### SQLite Surface

```sql
SELECT metadata_tag, COUNT(*) as count
FROM elimination_trace
WHERE session_id = :session_id
GROUP BY metadata_tag;

UPDATE elimination_sessions
SET completed_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
    total_eliminated = :total_eliminated
WHERE session_id = :session_id;
```

## Capability Contract

**Inputs:**

- `trace_history_session` *(string, required)* — Session ID whose elimination trace history to analyze.
- `game_type` *(string, required)* — Game classification label (e.g., `pd`, `coordination`, `general_sum`).

**Outputs:**

- `solver_profile` *(object)* — Profile with `prune_ratio`, `bias_direction`, and `confidence`.
- `hard_logic_count` *(integer)* — Total HARD_LOGIC tagged eliminations in session.
- `probabilistic_decay_count` *(integer)* — Total PROBABILISTIC_DECAY + EARLY_TERMINATION tags.
- `total_steps` *(integer)* — Total elimination steps analyzed.
- `prolog_fact_asserted` *(boolean)* — True if `solver_profile` fact was asserted into Prolog.

## Composition

- `skill-elimination-trace-logger` — Primary data source; consumes its trace table.
- `iterated-dominance-solver` — Indirect via trace logger instrumentation.
- `skill-bounded-rationality-constraint` — Provides EARLY_TERMINATION tag source.
- `skill-expected-utility-maximizer` — Receives `solver_profile` for adaptive EU weighting.
