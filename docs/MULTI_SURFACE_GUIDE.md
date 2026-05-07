# Multi-Surface Integration Guide

## Overview

Em-Cubed enables skills to leverage multiple execution surfaces (Python, Prolog, Hy, Z3, Datalog, Janus) through a unified context injection mechanism. This guide explains the intended pattern for cross-surface interaction.

## Context Injection

When a skill is executed via `SkillExecutor`, the framework automatically populates the execution context with a `surfaces` dictionary containing all available surface plugins:

```python
context = {
    "skill_input": {...},       # Input data for the skill
    "skill_metadata": {...},    # Skill frontmatter + metadata
    "surfaces": {               # Available surface plugins
        "python": <PythonSurface>,
        "prolog": <PrologSurface>,
        "hy": <HySurface>,
        "z3": <Z3Surface>,
        "datalog": <DatalogSurface>,
        "janus": <JanusSurface>,
    },
    ...  # Additional user-provided context
}
```

## Pattern: Python Preprocessing → Prolog Validation → Hy Scoring

```python
# Python skill code (executed on Python surface)
def process(data):
    # Access injected surfaces via context
    prolog = context["surfaces"]["prolog"]
    hy = context["surfaces"]["hy"]

    # Step 1: Python preprocessing
    cleaned = preprocess(data)

    # Step 2: Prolog constraint validation
    validation = await prolog.execute(
        f"valid({cleaned})", {}
    )

    # Step 3: Hy fuzzy scoring
    score = await hy.execute(
        f"(score {cleaned} {weights})", {}
    )

    return {
        "cleaned": cleaned,
        "valid": validation["value"],
        "score": score["value"]
    }
```

## Important Limitations

1. **Surface isolation**: Each surface has its own interpreter/memory. Shared state must pass through the context dict.
2. **Not true multi-surface skills**: Existing skills with code blocks in multiple surfaces run independently—one surface per execution. The `surfaces` dict enables calling other surfaces from within a surface.
3. **Available surfaces**: If a surface's dependencies are not installed, it won't appear in `context["surfaces"]`. Always check:
   ```python
   if "prolog" in context.get("surfaces", {}):
       prolog = context["surfaces"]["prolog"]
   ```

## Example: True Multi-Surface Skill

```markdown
---
Domain: EXAMPLE
name: python-prolog-pipeline
Version: 1.0.0
surfaces: [python, prolog]
---

## Python Code

```python
# Access the Prolog surface injected via context
prolog_surface = surfaces["prolog"]

# Define facts for Prolog
facts = "edge(a, b). edge(b, c). edge(c, d)."
await prolog_surface.execute(facts, {})

# Query Prolog
result = await prolog_surface.execute("path(a, d, Path)", {})
paths = result["value"]

# Post-process in Python in the same execution
sorted_paths = sorted(paths, key=len)
return {"shortest": sorted_paths[0] if sorted_paths else None}
```

## Prolog Code

```prolog
% Rules can be loaded by the Python code above
path(Start, End, [Start|Rest]) :-
    edge(Start, Next),
    path(Next, End, Rest).
path(End, End, [End]).
```
```

## Testing Multi-Surface Skills

Use `SkillExecutor` for integration tests. Do not import surface classes directly in test files:

```python
from em_cubed.skills.executor import SkillExecutor, SkillExecutionRequest

executor = SkillExecutor(plugin_manager, registry, skills_dir)
request = SkillExecutionRequest(
    skill_id="EXAMPLE/python-prolog-pipeline",
    input_data={"graph": {"edges": [["a","b"],["b","c"]]}, "start": "a", "end": "c"}
)
result = await executor.execute(request)
assert result.success
assert result.output["shortest"] == ["a", "b", "c"]
```

## Surface Reference

| Surface | Use Case | Key Methods |
|---------|----------|-------------|
| Python | General computation, orchestration | `surfaces["python"].execute(code, context)` |
| Prolog | Logic rules, constraint solving | `surfaces["prolog"].execute(query, context)` |
| Hy | Lisp-style processing, fuzzy logic | `surfaces["hy"].execute(code, context)` |
| Z3 | SMT solving, formal verification | `surfaces["z3"].execute(constraints, context)` |
| Datalog | Graph queries, recursive rules | `surfaces["datalog"].execute(query, context)` |
| Janus | Python-Prolog bridge (experimental) | `surfaces["janus"].execute(code, context)` |
