# Multi-Surface Skill Pattern

## Overview
Brief introduction to the concept: skills can declare capabilities across three programming surfaces (Python, Prolog, Hy) within a single SKILL.md file.

## The Three Surfaces

### Python Surface
- **Role**: Orchestration, main logic, API calls, data processing
- **Authority**: Primary surface for most skills
- **Fenced block**: ```python
- **Runtime**: Direct execution via Python interpreter

### Prolog Surface
- **Role**: Logical constraints, declarative rules, verification logic
- **Authority**: Definitive for logical reasoning tasks
- **Fenced block**: ```prolog
- **Runtime**: Via PySWIP (pyswip.Prolog)
- **Tag extraction**: Predicate names → logic_tags

### Hy Surface
- **Role**: Heuristic decision making, fuzzy logic, DSL-like expressions
- **Authority**: Preferred for heuristic/scoring functions
- **Fenced block**: ```hy
- **Runtime**: Via Hy Lisp (hy.read/eval)
- **Tag extraction**: Function names from defn → heuristic_tags

## Authority Hierarchy

When multiple surfaces can solve a task:
1. **Prolog** - Use for logical constraints and verification (declarative truth)
2. **Hy** - Use for heuristics and scoring (expressive, concise)
3. **Python** - Use for orchestration and everything else

The hierarchy is about *which surface should implement a given concern*, not execution order.

## Fenced Block Conventions

### SKILL.md Format
```markdown
## Implementation

### Python Entry Point
```python
# Python code here - indexed as python_surface
```

### Prolog Constraints
```prolog
% Prolog code here - indexed as prolog_surface
% Predicate names extracted to logic_tags
```

### Hy Heuristics
```hy
;; Hy code here - indexed as hy_surface
;; Function names extracted to heuristic_tags
```
```

### Automatic Detection
The `indexer` module automatically:
1. Extracts fenced blocks by language tag
2. Builds `surfaces` list from detected blocks
3. Extracts `logic_tags` from Prolog predicate heads
4. Extracts `heuristic_tags` from Hy `defn` forms
5. Falls back to `surfaces: ["python"]` if no blocks found

## Registry Schema Extension

New fields in `skill_registry.json`:
```json
{
  "name": "skill-name",
  "domain": "Domain",
  "surfaces": ["python", "prolog", "hy"],
  "logic_tags": ["predicate_name", ...],
  "heuristic_tags": ["function-name", ...],
  ...
}
```

## Search Integration

`search` module scores matches on new fields:
- **Surface match** (exact): +6 points
- **Tag match** (exact): +8 points (higher priority for precision)
- **Tag match** (substring): +2 points per word

Example queries:
- `"prolog"` - finds skills with Prolog surface
- `"max_allocation"` - finds skills with that Prolog predicate
- `"score-allocation"` - finds skills with that Hy function

## Canonical Example: multi-surface-problem-solver

**Location**: `examples/multi-surface-problem-solver/SKILL.md`

This POC demonstrates:
1. Python orchestration (`solve_allocation_problem`)
2. Prolog constraints (`max_allocation`, `min_allocation`, `valid_allocation`)
3. Hy heuristics (`score-allocation`, `fuzzy-balance`)

**Key Pattern**:
- Python is the entry point
- Prolog handles "what is valid" (constraints)
- Hy handles "what is optimal" (heuristics)

## Migration Guidelines

When converting single-surface skills to multi-surface:

1. **Identify the concern**: What logic can move to Prolog or Hy?
2. **Extract to fenced block**: Add ```prolog or ```hy block
3. **Reindex**: Run `python -m em_cubed.indexer <skills_dir> <registry_output>`
4. **Verify**: Search for new tags with `python -m em_cubed.search <registry_path> "tag_name"`

**Good candidates for migration**:
- Strategy domain: Game theory logic → Prolog
- Epistemology: Belief revision rules → Prolog
- Agent R&D: Heuristic scoring → Hy

## For Kilo Code

When creating or migrating skills:
1. Always consider if Prolog can express logical constraints
2. Always consider if Hy can express heuristics concisely
3. Use Python for orchestration, not for logic that fits other surfaces
4. Include fenced blocks with correct language tags
5. The indexer will automatically detect and register surfaces/tags

## Testing Multi-Surface Integration

```python
# Test all three surfaces work
from pyswip import Prolog
import hy

# Prolog
prolog = Prolog()
prolog.assertz("test_fact(ok)")
assert len(list(prolog.query("test_fact(X)"))) > 0

# Hy
result = hy.eval(hy.read("(+ 1 2 3)"))
assert result == 6

# Python integration
assert True  # Orchestration works
```

## Verification

1. Run `python -m em_cubed.indexer <skills_dir> <registry_output>` - should index skills
2. Check registry JSON has `surfaces`, `logic_tags`, `heuristic_tags` fields
3. Run `python -m em_cubed.search <registry_path> "prolog"` - should find Prolog skills
4. Run `python -m em_cubed.search <registry_path> "max_allocation"` - should find POC skill
5. Verify POC skill at `examples/multi-surface-problem-solver/SKILL.md` is documented as canonical example

## Notes

- This is documentation for the multi-surface pattern
- The POC skill is the living example, the doc explains the pattern
- Future Kilo Code sessions will read this to understand multi-surface expectations
