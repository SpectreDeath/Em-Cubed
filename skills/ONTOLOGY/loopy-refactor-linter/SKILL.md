---
name: loopy-refactor-linter
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
description: Self-correcting code refactoring loopy skill with deterministic linter verification guardrails. Executes iterative AST mutation in Python, validates ontological type signatures and class disjointness in Prolog, and bounds recursion up to a configured iteration budget. Use when refactoring Python code against strict style and typing linters, fixing AST syntax regressions automatically, or enforcing ontology-aligned interface constraints.
purpose: Encapsulate iterative AST mutation and multi-surface linter verification within a bounded self-healing loop.
dependencies: []
tags:
  - loopy-skill
  - refactor-linter
  - ast-mutation
  - prolog-disjointness
  - self-correction
inputs:
  source_code:
    type: string
    required: true
    description: Raw Python source code snippet to refactor.
  target_linter:
    type: string
    required: false
    description: "Linter sensor engine: ruff | flake8 | ast_parser (default: ruff)"
  max_iterations:
    type: integer
    required: false
    description: Maximum self-correction attempts before halting (default 5).
outputs:
  refactored_code:
    type: string
    description: Clean, linter-verified source code.
  trajectory:
    type: array
    description: Step-by-step record of mutation actions and linter observations.
  passed_guard:
    type: boolean
    description: True if code satisfies all linter rules and ontology checks.
---

# Loopy Refactor Linter Engine

`loopy-refactor-linter` implements the bounded self-healing edit-and-verify contract in `Em-Cubed`. Instead of failing prematurely on linter violations, it executes iterative AST transformations and validates ontological constraints at the ledger until all rules pass.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Loopy Refactoring Progression

```
[1. Parse & Invariant Audit] → [2. Linter Sensor Check] → [3. AST Patch Mutation] → [4. Checkpoint] → [5. Prolog Validation & Finish]
```

### Stage 1: Parse & Invariant Audit
1. Parse `source_code` into Python AST.
2. Ensure input is syntactically valid or repairable, and establish iteration limit (`max_iterations <= 10`).

> **Completion criterion**: AST parsed successfully or structural errors isolated into diagnostic map.

---

### Stage 2: Deterministic Linter Sensor Check
1. Execute target linter sensor (`ruff check --stdin-filename=snippet.py`).
2. If zero errors, terminate loop early with `passed_guard: true`.
3. Extract structured error codes (`E501`, `F401`, `E302`) and line offsets.

> **Completion criterion**: Discrete list of linter violations extracted with source line coordinates.

---

### Stage 3: Targeted AST Patch Mutation
1. Generate focused AST transform patches targeting the specific observed linter error codes.
2. Apply formatters or import trimmers while preserving code semantics.
3. Record action and observation into execution `trajectory`.

> **Completion criterion**: Modified source string generated and recorded into iteration history.

---

### Stage 4: Mandatory Checkpoint
Before applying mutations that alter function signatures or public interfaces:
1. Verify semantic equivalence against baseline test probes.
2. If interface modifications are detected, pause and request explicit user confirmation.

> **Completion criterion**: AST mutation confirmed non-breaking with respect to public APIs.

---

### Stage 5: Prolog Ontology Validation & Ledger Emit
1. Export modified class/function signature facts to Prolog:
   ```prolog
   valid_signature(FnName, Arity) :- declared_interface(FnName, Arity).
   ```
2. Verify class disjointness and interface compliance.
3. Emit final payload with complete execution trajectory.

> **Completion criterion**: Code passes both linter sensors and Prolog ontology verification.

---

## Surface References

### Python Loopy Engine Surface

```python
import ast
from typing import Dict, Any, List

def run_loopy_refactor(source_code: str, max_iterations: int = 5) -> Dict[str, Any]:
    current_code = source_code
    trajectory = []
    
    for iteration in range(1, max_iterations + 1):
        # 1. Verifier / Sensor
        try:
            tree = ast.parse(current_code)
            # Simulated linter sensor
            violations = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and len(node.name) > 30:
                    violations.append(f"Function name '{node.name}' exceeds max length")
            
            if not violations:
                trajectory.append({
                    "iteration": iteration,
                    "action_taken": "Validated AST and lint rules",
                    "observation": "Passed (0 errors)",
                    "passed_guard": True
                })
                return {"refactored_code": current_code, "trajectory": trajectory, "passed_guard": True}
                
            # 2. Mutator
            action = f"Shortened long function names (resolved {len(violations)} issues)"
            current_code = current_code.replace("extremely_long_unnecessary_function_name", "clean_func")
            trajectory.append({
                "iteration": iteration,
                "action_taken": action,
                "observation": f"Violations found: {violations}",
                "passed_guard": False
            })
        except SyntaxError as e:
            trajectory.append({"iteration": iteration, "action_taken": "Syntax error repair", "observation": str(e), "passed_guard": False})
            break
            
    return {"refactored_code": current_code, "trajectory": trajectory, "passed_guard": False}
```

### Prolog Disjointness Surface

```prolog
% Ontological validation for function signatures
disjoint_class(ClassA, ClassB) :- ClassA \= ClassB.
valid_refactor(FnName, Signature) :-
    registered_symbol(FnName),
    signature_compatible(FnName, Signature).
```

---

## Anti-Patterns & Guardrails

- **Infinite Mutation Cycles** — Oscillation between competing linters (e.g. formatter adding space, linter removing space). Always bound iterations and enforce strict trajectory uniqueness.
- **Silent Semantic Drift** — Altering runtime behavior or deleting functional statements while attempting to satisfy style rules. Enforce strict AST equality for functional nodes.
- **Unbounded Recursion** — Omitting `max_iterations` ceiling. Hard-clamp recursion depth to $\le 10$.
