---
name: self-evolving-compliance-agent
description: Demonstrates Phase 4 Autonomous Skill Evolution and Triple Induction, refining retry directives over consecutive runs.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - datalog
version: 1.0.0
---

# Self-Evolving Compliance Agent Skill

## Overview

The `self-evolving-compliance-agent` skill demonstrates **Phase 4 Autonomous Neuro-Symbolic Self-Refinement** in `Em-Cubed`.

## Refinement Workflow

1. **Run 1 (Exploration)**: Experiences 3 retries due to ungrounded initial state assumptions.
2. **Audit & Evolution**: `SkillEvolutionEngine` extracts abductive failure patterns from `AuditReport` proof trails and compiles preventative steering directives.
3. **Run 2 (Evolved Execution)**: Achieves **1-step direct deductive convergence** using the synthesized preventative steering rules.
4. **Triple Induction**: `TripleInductionEngine` automatically induces new verified `OntologyTriple` assertions into `GraphPathRAG`.

## Evolved Directive Output Example

```json
{
  "skill_name": "self-evolving-compliance-agent",
  "preventative_rules": [
    "PREVENTIVE DIRECTIVE (From Step 1): Avoid 'Disjoint Class Violation: Entity User_99 is already SupportRep'"
  ],
  "optimized_retry_count": 1
}
```
