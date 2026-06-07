---
name: monte-carlo-simulator
domain: OPTIMIZATION
version: "1.0.0"
surfaces: [python, sqlite]
---

## Purpose
Approximates complex boundary problems by aggregating thousands of random trials into a statistical distribution.

## Description
Runs a pure-loop execution engine that simulates N independent paths, records terminal results, and outputs a normalized summary matrix. SQLite manages trial distribution state to avoid in-memory exhaustion over millions of iterations.

## Python Surface

```python
import random

def run_monte_carlo(trial_function, n_trials, session_id):
    results = []
    for i in range(n_trials):
        outcome = trial_function()
        results.append(outcome)

    min_val = min(results)
    max_val = max(results)
    range_val = max_val - min_val if max_val != min_val else 1.0

    summary = {
        'trials': n_trials,
        'mean': sum(results) / n_trials,
        'min': min_val,
        'max': max_val,
        'std': (sum((x - sum(results) / n_trials) ** 2 for x in results) / n_trials) ** 0.5,
        'distribution': {}
    }

    for r in results:
        bin_key = int((r - min_val) / range_val * 10)
        summary['distribution'][bin_key] = summary['distribution'].get(bin_key, 0) + 1

    summary['distribution'] = dict(sorted(summary['distribution'].items()))
    return summary

def run_monte_carlo_batched(trial_function, n_trials, batch_size):
    batches = []
    for _ in range(0, n_trials, batch_size):
        current_batch = min(batch_size, n_trials - len(batches) * batch_size)
        result = run_monte_carlo(trial_function, current_batch, f"batch_{len(batches)}")
        batches.append(result)
    return merge_monte_carlo_results(batches)

def merge_monte_carlo_results(batches):
    total_trials = sum(b['trials'] for b in batches)
    all_means_weighted = sum(b['mean'] * b['trials'] for b in batches)
    global_min = min(b['min'] for b in batches)
    global_max = max(b['max'] for b in batches)

    return {
        'trials': total_trials,
        'mean': all_means_weighted / total_trials,
        'min': global_min,
        'max': global_max
    }
```

## SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS monte_carlo_sessions (
    session_id TEXT PRIMARY KEY,
    n_trials INTEGER,
    start_time TEXT,
    end_time TEXT,
    summary_json TEXT
);

CREATE TABLE IF NOT EXISTS monte_carlo_batches (
    batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    batch_index INTEGER,
    outcomes_json TEXT,
    FOREIGN KEY (session_id) REFERENCES monte_carlo_sessions(session_id)
);

INSERT INTO monte_carlo_sessions (session_id, n_trials, start_time, end_time, summary_json)
VALUES (:session_id, :n_trials, :start_time, :end_time, :summary_json);

INSERT INTO monte_carlo_batches (session_id, batch_index, outcomes_json)
VALUES (:session_id, :batch_index, :outcomes_json);

SELECT batch_index, outcomes_json
FROM monte_carlo_batches
WHERE session_id = :session_id
ORDER BY batch_index;
```

## Testing

### Unit Tests

```python
import random

def dice_roll():
    return random.randint(1, 6)

def test_monte_carlo_dice():
    random.seed(42)
    result = run_monte_carlo(dice_roll, 1000, "test_dice")
    assert result['trials'] == 1000
    assert 1.0 <= result['mean'] <= 6.0
    assert result['min'] >= 1
    assert result['max'] <= 6
    assert len(result['distribution']) > 0

def test_batched_monte_carlo():
    random.seed(42)
    result = run_monte_carlo_batched(dice_roll, 5000, 1000)
    assert result['trials'] == 5000
    assert 1.0 <= result['mean'] <= 6.0
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_monte_carlo_skill_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "OPTIMIZATION" / "monte-carlo-simulator"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text('name: monte-carlo-simulator\ndomain: OPTIMIZATION')
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        results = search_registry("monte carlo", registry_file)
        assert len(results) >= 1
```

## Security Considerations
- Pure numerical operations only; no file system, network, or OS access.
- SQLite queries use parameterized statements to prevent injection.
- Batched processing prevents memory exhaustion on large N.
- No external dependencies; safe for sandboxed execution.

## Dependencies
- `em_cubed` framework (zero external dependencies)
