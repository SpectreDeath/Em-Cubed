# Skill Summary Card: `loopy-refactor-linter`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        loopy-refactor-linter                     │
│ Category:    ONTOLOGY / Self-Healing Loopy Skills      │
│ Invocation:  /loopy-refactor-linter                    │
│ Trigger:     "loopy refactor", "lint self-healing",    │
│              "ast auto-fix", "fix code style loop"     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Iterative AST mutation and deterministic  │
│              linter self-correction within bounded     │
│              trajectory loops.                         │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Parse & Invariants** | Parse input code into AST representation | AST Tree Object | Syntactic parse succeeds or errors isolated |
| **2. Linter Sensor** | Check code against ruff / parser rules | Sensor Diagnostic Map | Concrete error codes & line numbers extracted |
| **3. AST Mutation** | Apply targeted patch to resolve observed codes | Transformed Code String | Patch applied and logged into trajectory |
| **4. Checkpoint** | Validate interface invariants and semantics | Equivalence Assertion | Semantic equivalence preserved |
| **5. Prolog Validation** | Verify class disjointness & emit trajectory | Final JSON Payload | `passed_guard: true` or iteration budget hit |

---

## Invariants & Guardrails

- [ ] **Hard Iteration Ceiling**: Never exceed configured `max_iterations` ($\le 10$).
- [ ] **Deterministic Trajectory**: Every edit recorded with `iteration`, `action_taken`, and `observation`.
- [ ] **Semantic Preservation**: Zero changes to function arity or public exported signatures without explicit checkpoint.
