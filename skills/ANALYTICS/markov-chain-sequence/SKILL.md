---
name: markov-chain-sequence
domain: ANALYTICS
version: "1.0.0"
surfaces: [prolog, python]
description: Multi-surface Markov chain sequence generator with Python surface for state transition simulation and Prolog surface for transition probability verification.
compatibility: PROLOG, PYTHON
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

## Purpose
Generates dependent state transitions using a zero-dependency probabilistic transition matrix.

## Description
Implements an infrastructure-safe, memoryless sequence generator based on Andre Markov's text sequence derivations. It checks transition probability constraints within Prolog to ensure strict stochastic normalization, and processes safe sequential state transitions inside an isolated Python loop.

## Python Surface

```python
def step_chain(matrix, current_state, rand_val):
    if current_state not in matrix:
        return {"status": "error", "message": "Unknown active state context"}

    branches = matrix[current_state]
    cumulative = 0.0

    for next_state, probability in branches.items():
        cumulative += probability
        if rand_val <= cumulative:
            return {
                "status": "success",
                "previous_state": current_state,
                "next_state": next_state
            }

    return {
        "status": "success",
        "previous_state": current_state,
        "next_state": list(branches.keys())[-1]
    }

# Execute step
step_chain(transition_matrix, current_state, random_float)
```

## Prolog Surface

```prolog
sum_list([], 0.0).
sum_list([H|T], Sum) :-
    sum_list(T, Rest),
    Sum is H + Rest.

validate_state_weights(StateName, WeightsList) :-
    sum_list(WeightsList, Total),
    abs(Total - 1.0) < 0.0001, !.
validate_state_weights(StateName, _) :-
    throw(error(sub_stochastic_row(StateName))).
```

## Testing

### Unit Tests

```python
import random

def test_markov_step():
    matrix = {
        'Vowel': {'Vowel': 0.13, 'Consonant': 0.87},
        'Consonant': {'Vowel': 0.66, 'Consonant': 0.34}
    }

    result = step_chain(matrix, 'Vowel', 0.05)
    assert result['status'] == 'success'
    assert result['previous_state'] == 'Vowel'
    assert result['next_state'] == 'Vowel'

    result = step_chain(matrix, 'Vowel', 0.20)
    assert result['status'] == 'success'
    assert result['next_state'] == 'Consonant'

def test_unknown_state():
    matrix = {'A': {'B': 1.0}}
    result = step_chain(matrix, 'Z', 0.5)
    assert result['status'] == 'error'
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_markov_chain_skill_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "ANALYTICS" / "markov-chain-sequence"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: markov-chain-sequence\ndomain: ANALYTICS')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("markov", registry_file)
        assert len(results) >= 1
```

## Security Considerations
- Pure numerical operations only; no file system, network, or OS access.
- All state transitions bounded by probability distribution constraints.
- No external dependencies; safe for sandboxed execution.

## Dependencies
- `em_cubed` framework (zero external dependencies)
