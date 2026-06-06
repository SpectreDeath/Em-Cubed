---
name: dag-task-scheduler
Domain: DISTRIBUTED_SYSTEMS
version: "1.0.0"
surfaces:
  - python
  - z3
  - sqlite
---

# DAG Task Scheduler

Distributed DAG execution orchestrator for task dependency resolution, scheduling, and constraint verification.

## Purpose

Execute and verify distributed directed acyclic graph task workflows with zero-dependency Python and SQLite persistence.

## Description

This skill provides:
- Python: Topological sort, dependency resolution, critical path calculation
- Z3: Constraint verification for task ordering and resource allocation
- SQLite: Persistent task state storage and execution history

## Implementation

### Python DAG Executor

```python
def topological_sort(tasks, dependencies):
    """Sort tasks in topological order."""
    in_degree = {t: 0 for t in tasks}
    graph = {t: [] for t in tasks}
    for dep in dependencies:
        if dep[0] in graph:
            graph[dep[0]].append(dep[1])
            in_degree[dep[1]] = in_degree.get(dep[1], 0) + 1
    queue = [t for t in tasks if in_degree.get(t, 0) == 0]
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return result if len(result) == len(tasks) else []

def critical_path(tasks, durations, dependencies):
    """Calculate critical path for task scheduling."""
    earliest_start = {t: 0 for t in tasks}
    earliest_finish = {t: durations.get(t, 1) for t in tasks}
    for dep in dependencies:
        if dep[1] in earliest_start and dep[0] in earliest_finish:
            earliest_start[dep[1]] = max(earliest_start[dep[1]], earliest_finish[dep[0]])
            earliest_finish[dep[1]] = earliest_start[dep[1]] + durations.get(dep[1], 1)
    return max(earliest_finish.values()) if earliest_finish else 0

def get_ready_tasks(tasks, completed, dependencies):
    """Get tasks ready to execute (all dependencies satisfied)."""
    ready = []
    for task in tasks:
        deps_satisfied = all(d in completed for d, t in dependencies if t == task)
        if deps_satisfied and task not in completed:
            ready.append(task)
    return ready
```

### Z3 Constraint Verifier

```python
def verify_task_constraints(tasks, dependencies, resources, limits):
    """Verify task ordering and resource constraints with Z3."""
    from z3 import Int, Solver, And, Or, Implies, sat
    solver = Solver()
    start_times = {t: Int(f'start_{t}') for t in tasks}
    solver.add([s >= 0 for s in start_times.values()])
    for dep in dependencies:
        solver.add(start_times[dep[1]] > start_times[dep[0]])
    for task, req in resources.items():
        if task in start_times:
            solver.add(start_times[task] < limits.get(req, 100))
    return solver.check() == sat

def find_optimal_schedule(tasks, durations, dependencies, total_time):
    """Find optimal schedule within time constraint."""
    from z3 import Int, Solver, And, Optimize, sat
    solver = Optimize()
    start_times = {t: Int(f's_{t}') for t in tasks}
    end_times = {t: Int(f'e_{t}') for t in tasks}
    solver.add([end_times[t] == start_times[t] + durations.get(t, 1) for t in tasks])
    solver.add([s >= 0 for s in start_times.values()])
    solver.add([e < total_time for e in end_times.values()])
    for dep in dependencies:
        solver.add(start_times[dep[1]] >= end_times[dep[0]])
    solver.minimize(max(end_times.values()))
    return solver.check() == sat
```

### SQLite Task Persistence

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    duration INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    source_id TEXT,
    target_id TEXT,
    PRIMARY KEY (source_id, target_id)
);

CREATE TABLE IF NOT EXISTS task_executions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    started_at TEXT,
    completed_at TEXT,
    status TEXT
);

INSERT INTO tasks (id, name, status, duration) VALUES (?, ?, 'pending', ?);

SELECT t.id FROM tasks t WHERE t.status = 'pending' 
    AND NOT EXISTS (
        SELECT 1 FROM task_dependencies td 
        WHERE td.target_id = t.id 
        AND td.source_id NOT IN (SELECT id FROM tasks WHERE status = 'completed')
    );
```

## Testing

### Unit Tests

```python
def test_topological_sort():
    tasks = ['A', 'B', 'C', 'D']
    deps = [('A', 'B'), ('B', 'C'), ('A', 'D')]
    result = topological_sort(tasks, deps)
    assert result.index('A') < result.index('B')
    assert result.index('B') < result.index('C')

def test_critical_path():
    tasks = ['A', 'B', 'C', 'D']
    durations = {'A': 3, 'B': 2, 'C': 4, 'D': 1}
    deps = [('A', 'B'), ('A', 'D'), ('B', 'C')]
    result = critical_path(tasks, durations, deps)
    assert result == 7

def test_ready_tasks():
    tasks = ['A', 'B', 'C', 'D']
    deps = [('A', 'B'), ('A', 'C')]
    completed = ['A']
    ready = get_ready_tasks(tasks, completed, deps)
    assert set(ready) == {'B', 'C'}
```

## Security Considerations

- Pure task scheduling logic
- No network access
- SQLite for isolated state persistence