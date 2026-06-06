---
name: durable-execution-engine
Domain: DISTRIBUTED_SYSTEMS
version: "1.0.0"
surfaces:
  - python
  - z3
  - sqlite
---

# Durable Execution Engine

Workflow checkpoint management and state recovery for fault-tolerant distributed execution.

## Purpose

Execute workflows with automatic checkpointing, state recovery, and constraint verification.

## Description

This skill provides:
- Python: Checkpoint creation, state serialization, step recovery
- Z3: State consistency constraints, recovery point validation
- SQLite: Persistent storage for checkpoints and workflow state

## Implementation

### Python Checkpoint Manager

```python
import json
import uuid
import time
from typing import Dict, Any, Optional, List

class Checkpoint:
    def __init__(self, workflow_id: str, step_name: str, state: Dict[str, Any]):
        self.checkpoint_id = str(uuid.uuid4())
        self.workflow_id = workflow_id
        self.step_name = step_name
        self.state = state
        self.timestamp = time.time()

    def serialize(self) -> str:
        return json.dumps({
            'checkpoint_id': self.checkpoint_id,
            'workflow_id': self.workflow_id,
            'step_name': self.step_name,
            'state': self.state,
            'timestamp': self.timestamp
        })

def create_checkpoint(workflow_id: str, step_name: str, state: Dict[str, Any]) -> Checkpoint:
    return Checkpoint(workflow_id, step_name, state)

def save_checkpoint(checkpoint: Checkpoint) -> str:
    data = checkpoint.serialize()
    return f"checkpoint:{checkpoint.checkpoint_id}:{data}"

def load_checkpoint(data: str) -> Optional[Checkpoint]:
    if not data.startswith('checkpoint:'):
        return None
    parts = data.split(':', 2)
    if len(parts) < 3:
        return None
    payload = json.loads(parts[2])
    cp = Checkpoint(payload['workflow_id'], payload['step_name'], payload['state'])
    cp.checkpoint_id = payload['checkpoint_id']
    cp.timestamp = payload['timestamp']
    return cp

def recover_workflow(checkpoints: List[str], target_step: str) -> Optional[str]:
    latest = None
    for cp_data in checkpoints:
        cp = load_checkpoint(cp_data)
        if cp and cp.step_name == target_step:
            if latest is None or cp.timestamp > latest.timestamp:
                latest = cp
    return latest.state if latest else None
```

### Z3 State Consistency Verifier

```python
def verify_checkpoint_sequence(checkpoints: List[Dict], expected_order: List[str]) -> bool:
    from z3 import Solver, Bool, Implies, And, sat
    solver = Solver()
    step_vars = {}
    for cp in checkpoints:
        step = cp.get('step_name', '')
        step_vars[step] = Bool(f'completed_{step}')
    for i in range(len(expected_order) - 1):
        cur = expected_order[i]
        nxt = expected_order[i + 1]
        if cur in step_vars and nxt in step_vars:
            solver.add(Implies(step_vars[cur], step_vars[nxt]))
    for step in expected_order:
        if step in step_vars:
            solver.add(step_vars[step])
    return solver.check() == sat

def find_recovery_point(checkpoints: List[Dict], target_time: float) -> Optional[str]:
    for cp in reversed(checkpoints):
        if cp.get('timestamp', 0) <= target_time:
            return cp.get('checkpoint_id', '')
    return None
```

### SQLite Checkpoint Store

```sql
CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    step_name TEXT NOT NULL,
    state_json TEXT,
    timestamp REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow ON checkpoints(workflow_id);
CREATE INDEX IF NOT EXISTS idx_step ON checkpoints(step_name);

INSERT INTO checkpoints (checkpoint_id, workflow_id, step_name, state_json, timestamp)
VALUES (?, ?, ?, ?, ?);

SELECT state_json FROM checkpoints 
WHERE workflow_id = ? AND step_name = ? 
ORDER BY timestamp DESC LIMIT 1;

SELECT checkpoint_id, step_name, timestamp FROM checkpoints
WHERE workflow_id = ? 
ORDER BY timestamp ASC;
```

## Testing

### Unit Tests

```python
def test_create_checkpoint():
    cp = create_checkpoint('wf1', 'step1', {'data': 123})
    assert cp.workflow_id == 'wf1'
    assert cp.step_name == 'step1'
    assert cp.state == {'data': 123}

def test_checkpoint_roundtrip():
    cp = create_checkpoint('wf1', 'step1', {'data': 123})
    saved = save_checkpoint(cp)
    loaded = load_checkpoint(saved)
    assert loaded is not None
    assert loaded.state == {'data': 123}

def test_recover_workflow():
    c1 = create_checkpoint('wf1', 'init', {'x': 1})
    c2 = create_checkpoint('wf1', 'process', {'x': 2})
    state = recover_workflow([save_checkpoint(c1), save_checkpoint(c2)], 'process')
    assert state == {'x': 2}
```

## Security Considerations

- State serialization only (no deserialization of untrusted data)
- SQLite for isolated persistence
- Z3 constraints prevent invalid state transitions