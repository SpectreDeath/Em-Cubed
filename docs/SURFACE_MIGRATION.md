# Surface Migration Guide

This guide helps skill authors transition from direct library imports to using Em-Cubed's surface abstractions.

## Why Migrate?

Direct imports of surface libraries (e.g., `pyswip`, `hy`, `z3`) in skills cause:

- **Portability issues**: Skills fail when dependencies are missing or configured differently.
- **Security risks**: Bypassing the sandbox and timeout controls provided by Em-Cubed.
- **Inconsistent state management**: Surfaces manage their own state, initialization, and cleanup.
- **Lack of abstraction**: Skills become tightly coupled to specific implementations.

By using the framework's surface API, skills gain:
- Uniform execution interface (`execute(code, context)`)
- Automatic timeout and error handling
- Access to plugin discovery and availability checks
- Future compatibility as the framework evolves

## Migration Patterns

### Python → no change

Python skills already use `asteval` through `PythonSurface`; keep using that surface.

### Prolog

**Before:**
```python
from pyswip import Prolog

prolog = Prolog()
prolog.assertz("parent(john, mary)")
result = list(prolog.query("parent(X, Y)"))
```

**After:**
```python
# Skill code receives surface via execute
# The surface handles all Prolog interactions internally
code = """
parent(john, mary).
parent(X, Y) :- parent(john, X), parent(X, Y).
"""
result = await surface.execute(code, context={})
# Returns structured result with 'status' and 'result' keys
```

The skill's code block for Prolog should contain Prolog source directly; the framework runs it through the `PrologSurface` which manages the PySWIP instance.

**Important:** The PySWIP API exposed via `PrologSurface` mirrors the common operations (`assertz`, `query`, `consult`). If your skill needs file consultation, use `consult` through the surface's `execute` with appropriate code (e.g., `consult('file.pl').`).

### Hy

**Before:**
```python
import hy
forms = hy.read_many("(defn add [x y] (+ x y))")
hy.eval(forms)
```

**After:**
```python
code = "(defn add [x y] (+ x y))"
result = await surface.execute(code, context)
```

### Z3

**Before:**
```python
from z3 import Solver, Int, sat

s = Solver()
x = Int('x')
s.add(x > 5)
s.check()
```

**After:**
```python
code = """
solver = Solver()
x = Int('x')
solver.add(x > 5)
result = solver.check()
"""
result = await surface.execute(code, context={})
# result['value'] may contain solver state
```

### Datalog

**Before:**
```python
from pyDatalog import pyDatalog
pyDatalog.create_atoms('likes')
pyDatalog.assert_fact(likes, 'john', 'pizza')
pyDatalog.ask('likes(john, X)')
```

**After:**
```python
code = """
from pyDatalog import pyDatalog
pyDatalog.create_atoms('likes')
+ (likes['john', 'pizza'])
"""
result = await surface.execute(code, context)
```

Note: The Datalog surface uses asteval to execute pyDatalog code safely. The same pyDatalog syntax applies.

## Executing Across Multiple Surfaces

Skills that previously manually instantiated different language runtimes should now declare multiple surfaces in their SKILL.md and implement each block separately. The framework selects the appropriate surface at runtime.

Example: A skill that needs both Python for data processing and Prolog for logic:

```yaml
surfaces:
  - python
  - prolog
```

Then in the `Implementation` section:

```markdown
### Python Core

```python
# Data preprocessing
cleaned = [x for x in data if x > 0]
```

### Prolog Rules

```prolog
% Classification rules
valid_item(X) :- X > 0.
```
```

The framework executes the right block based on the requested surface.

## Using Context

The `context` parameter provides input values to the execution:

```python
result = await surface.execute("x + y", context={"x": 10, "y": 5})
# result['value'] == 15
```

Context variables are injected into the surface's namespace before code execution.

## Error Handling

The surface returns a consistent result structure:

```json
{
  "status": "ok" | "error",
  "value": ... ,           // on success
  "message": "...",        // on error
  "result": [...]          // for queries (Prolog/Datalog)
}
```

Check `status` before using `value`.

## Testing Migration

Update skill unit tests to use the `PythonSurface` or relevant surface from `em_cubed.surfaces`:

```python
from em_cubed.surfaces import PythonSurface, PrologSurface

surface = PrologSurface()
result = await surface.execute("parent(john, X).", {})
assert result["status"] == "ok"
```

Avoid importing external libraries directly in tests; use the surface abstractions.

## Need Help?

- Open an issue on GitHub
- See `docs/MULTI_SURFACE.md` for multi-surface patterns
- Reference existing skills in `skills/` directory for examples
