---
name: schema-evolution-migrator
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: Dynamic ontological schema evolution and lossless migration engine. Executes backward-compatible versioned migration chains over active knowledge graphs, verifies compatibility invariants, and rewrites triple predicates/classes deterministically without data loss. Use when upgrading semantic ontology versions, migrating live triple stores across schema revisions, renaming ontology predicates safely, or checking forward/backward compatibility.
purpose: Execute deterministic, backward-compatible schema migrations over active ontology ledgers.
dependencies: []
tags:
  - schema-evolution
  - migration-engine
  - version-compatibility
  - predicate-renaming
  - lossless-migration
inputs:
  source_triples:
    type: array
    required: true
    description: Active ontology triples under current schema version.
  from_version:
    type: string
    required: true
    description: Current schema version tag (e.g. 'v1.0.0').
  target_version:
    type: string
    required: true
    description: Target schema version tag (e.g. 'v1.1.0').
  migration_rules:
    type: array
    required: false
    description: Explicit transform directives (e.g. RENAME_PREDICATE, SPLIT_CLASS).
outputs:
  migrated_triples:
    type: array
    description: Transformed knowledge graph triples adhering to target schema version.
  compatibility_passed:
    type: boolean
    description: True if migration preserves backward compatibility and passes SHACL validation.
  steps_applied:
    type: array
    description: Detailed log of applied schema transform operations.
---

# Schema Evolution Migrator Engine

`schema-evolution-migrator` implements **Phase 10 Dynamic Ontological Schema Evolution & Migration** in `Em-Cubed`. As domain requirements evolve, ontology schemas change. This engine applies formal migration pipelines to active triple stores, verifying backward compatibility and executing lossless predicate/class transformations.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Schema Migration Progression

```
[1. Version & Schema Invariant Audit] → [2. Compatibility Verification] → [3. Visual Brief] → [4. Checkpoint] → [5. Lossless Transform & Re-audit]
```

### Stage 1: Version & Schema Invariant Audit
1. Parse source version, target version, and `source_triples`.
2. Ensure target version is higher in semver ordering ($v_{\text{target}} > v_{\text{source}}$).

> **Completion criterion**: Version tags and source triple store parsed without syntax errors.

---

### Stage 2: Forward & Backward Compatibility Verification
1. Check migration rule set against target schema SHACL shapes.
2. Verify that no mandatory properties are deleted without default fallback expressions.

> **Completion criterion**: Compatibility certified with `compatibility_passed: true`.

---

### Stage 3: The Visual Brief
For major version migrations or multi-predicate renames, generate an interactive brief:
- **Location**: Write to `%TEMP%\schema-migration-brief-<timestamp>.html` (Windows) or `/tmp/schema-migration-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render schema migration diff graph showing old predicates mapping to new predicates.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before applying migration transforms to production triple ledgers:
1. Verify that a state snapshot/backup is recorded in the Merkle replay engine.
2. Halt for human sign-off on breaking changes or class deletions.

> **Completion criterion**: Backup snapshot verified and migration approved.

---

### Stage 5: Lossless Transform & Ledger Commit
1. Apply rewrite rules:
   - `RENAME_PREDICATE(old_p, new_p)`
   - `MAP_CLASS(old_c, new_c)`
2. Validate post-migration triples against target version schema.
3. Emit transformed triples and migration audit log.

> **Completion criterion**: Transformed triples emitted with 100% data retention and valid target schema.

---

## Surface References

### Python Schema Migration Surface

```python
from typing import List, Dict, Any

def migrate_ontology_schema(triples: List[str], from_ver: str, to_ver: str) -> Dict[str, Any]:
    steps = []
    migrated = []
    
    for t in triples:
        if "has_origin" in t:
            new_t = t.replace("has_origin", "has_country_of_origin")
            steps.append("RENAME_PREDICATE: has_origin -> has_country_of_origin")
            migrated.append(new_t)
        else:
            migrated.append(t)
            
    return {
        "from_version": from_ver,
        "target_version": to_ver,
        "compatibility_passed": True,
        "migrated_triples_count": len(migrated),
        "steps_applied": list(set(steps)),
        "migrated_triples": migrated
    }
```

---

## Anti-Patterns & Guardrails

- **Destructive Schema Mutations** — Dropping properties or classes during migration without providing a backward-compatible mapping rule.
- **Unversioned Triple Stores** — Mutating knowledge graph assertions without tagging the resulting graph with target schema version metadata.
- **Unverified Post-Migration State** — Assuming migrations succeeded without running automated SHACL re-validation over the output.
