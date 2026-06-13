---
name: z3-schedule-solver
Domain: OPTIMIZATION
Version: 1.0.0
surfaces:
  - python
  - z3
description: Z3 schedule solver for constraint-based timetabling, resource allocation, and shift planning with formal verification.
compatibility: PYTHON
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
Solve scheduling constraint problems using Z3 SMT solver from within a Python skill.

## Description
This skill uses the Z3 theorem prover to find valid schedules that satisfy a set of constraints. Python prepares the constraints, Z3 solves the problem, and Python interprets and formats the results.

## Implementation

### Python
```python
def main(skill_input):
    """Find a valid schedule using Z3."""
    from z3 import Solver, Int, sat, And

    # Example: schedule three tasks to non-overlapping timeslots 0-2
    tasks = skill_input.get("tasks", ["A", "B", "C"])
    num_slots = skill_input.get("slots", 3)

    solver = Solver()
    # Create integer variables for each task slot
    task_vars = [Int(f"t_{t}") for t in tasks]

    # Each task gets a distinct slot in range [0, num_slots-1]
    for v in task_vars:
        solver.add(And(v >= 0, v < num_slots))

    # All tasks distinct
    for i in range(len(task_vars)):
        for j in range(i + 1, len(task_vars)):
            solver.add(task_vars[i] != task_vars[j])

    # Solve
    if solver.check() == sat:
        model = solver.model()
        schedule = {tasks[i]: model[task_vars[i]].as_long() for i in range(len(tasks))}
        return {"status": "ok", "schedule": schedule}
    else:
        return {"status": "unsat"}
```

## Examples
```python
input_data = {"tasks": ["Task1", "Task2", "Task3"], "slots": 3}
# Expected output: {"status": "ok", "schedule": {"Task1": 0, "Task2": 1, "Task3": 2}} (or other valid mapping)
```
