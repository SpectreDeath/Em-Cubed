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
# Graph pathfinding in Python (BFS)
# This code runs inside asteval - no async/await or imports allowed

edges = skill_input.get("edges", [])
start = skill_input.get("start", "")
end = skill_input.get("end", "")

# Build adjacency list
graph = {}
for src, tgt in edges:
    if src not in graph:
        graph[src] = []
    graph[src].append(tgt)

# BFS
queue = [(start, [start])]
visited = {start}
found_path = None

while queue:
    node, path = queue.pop(0)
    if node == end:
        found_path = path
        break
    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            visited.add(neighbor)
            queue.append((neighbor, path + [neighbor]))

result = {"path": found_path, "count": len(found_path) if found_path else 0}
result
```

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
