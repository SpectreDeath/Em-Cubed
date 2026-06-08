---
Domain: EXAMPLES
name: python-prolog-pipeline
Version: 1.0.0
surfaces:
  - python
  - prolog
origin: manual
triggers:
  - example
  - pipeline
  - graph
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-07T21:00:00Z"
updated_at: "2026-05-07T21:00:00Z"
---

## Purpose

Demonstrates a multi-surface skill with Python orchestration and Prolog validation. Each surface code block runs independently when the skill is executed.

## Description

This skill provides graph pathfinding with two surface implementations:

- **Python**: BFS pathfinding with graph traversal
- **Prolog**: Declarative path finding with logical rules

When executed via the SkillExecutor, the caller chooses which surface to run. Both surfaces implement the same graph algorithm in their native paradigm.

## Examples

```
Input: {"edges": [["a","b"], ["b","c"], ["c","d"]], "start": "a", "end": "d"}
Output: {"path": ["a","b","c","d"], "count": 4}
```

## Implementation

### Python Code

```python
# Graph pathfinding with Python orchestration and Prolog logic
# This demonstrates a true multi-surface pipeline

edges = skill_input.get("edges", [])
start = skill_input.get("start", "")
end = skill_input.get("end", "")

if not edges or not start or not end:
    result = {"error": "Missing input data"}
else:
    prolog = context["surfaces"]["prolog"]
    
    # 1. Reset and load rules into Prolog
    prolog.execute_sync("retractall(edge(_, _)).")
    prolog.execute_sync("path(X, X, [X]).")
    prolog.execute_sync("path(X, Y, [X|Rest]) :- edge(X, Z), path(Z, Y, Rest).")
    
    # 2. Assert facts from Python input
    for src, tgt in edges:
        prolog.execute_sync(f"edge({src}, {tgt}).")
    
    # 3. Query Prolog for the path
    query = f"path({start}, {end}, Path)"
    res = prolog.execute_sync(query)
    
    if res.get("status") == "ok" and res.get("result"):
        # Take the first path found
        found_path = res["result"][0]["Path"]
        result = {
            "path": found_path,
            "count": len(found_path),
            "method": "python-orchestrated-prolog-inference"
        }
    else:
        result = {"path": None, "count": 0, "error": "No path found"}

result
```

````

### Prolog Code

```prolog
% Graph pathfinding in Prolog (declarative)
% Facts are asserted at runtime, then path rules apply

% Assert edges from input (done by executor wrapper)

% Path finding rules
path(Start, End, [Start|Rest]) :-
    edge(Start, Next),
    path(Next, End, Rest).
path(End, End, [End]).
```
