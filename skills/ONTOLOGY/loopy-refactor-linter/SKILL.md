---
name: loopy-refactor-linter
description: Demonstrates a self-correcting code refactoring loopy skill with deterministic linter verification guardrails.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
version: 1.0.0
---

# Loopy Refactor Linter Skill

## Overview

The `loopy-refactor-linter` skill demonstrates the **Loopy Skill** contract in `Em-Cubed`. Instead of returning immediately on a linter failure, the skill encapsulates an internal edit-and-verify cycle that self-corrects code up to a configured iteration limit before handing the result back to the orchestrator.

## Structure

1. **Mutator**: Generates AST or text transformation patches on python snippets.
2. **Verifier (Sensor)**: Executes deterministic linter checks (`ruff check` or AST parser).
3. **Ontology Validator**: Validates that function signatures and class disjointness rules are maintained at the ledger.

## Trajectory Output

```json
{
  "success": true,
  "final_output": "def clean_function(): pass",
  "trajectory": [
    {
      "iteration": 1,
      "action_taken": "Removed unused imports",
      "observation": "Linter failed: E501 line too long",
      "passed_guard": false
    },
    {
      "iteration": 2,
      "action_taken": "Formatted line lengths",
      "observation": "Linter passed (0 errors)",
      "passed_guard": true
    }
  ]
}
```
