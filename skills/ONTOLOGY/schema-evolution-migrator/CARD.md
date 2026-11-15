# Skill Summary Card: `schema-evolution-migrator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        schema-evolution-migrator                 │
│ Category:    ONTOLOGY / Schema Evolution & Migration   │
│ Invocation:  /schema-evolution-migrator                │
│ Trigger:     "migrate ontology schema",                │
│              "schema evolution", "upgrade triple store",│
│              "rename ontology predicate"               │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Dynamic, backward-compatible schema       │
│              evolution and lossless triple migration   │
│              across versioned ontology ledgers.        │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate version tags & source triple store | Source Triple AST | Valid semver order ($v_{\text{target}} > v_{\text{source}}$) |
| **2. Compatibility** | Check backward compatibility against SHACL | Compatibility Report | Certified `compatibility_passed: true` |
| **3. Visual Brief** | Render schema migration diff graph | `%TEMP%\schema-migration-brief-*.html`| Dark theme HTML migration diff brief |
| **4. Checkpoint** | Validate Merkle backup snapshot | Safety Gate Record | Cryptographic snapshot recorded before edit |
| **5. Migration Run** | Execute transforms & validate target schema | Migrated Triple Store | Output triples 100% valid under target schema |

---

## Invariants & Guardrails

- [ ] **Lossless Migration**: No triples dropped without explicit deletion rules.
- [ ] **Pre-Migration Snapshot**: State snapshot must be recorded prior to schema mutation.
- [ ] **Semver Ordering**: Target version must be strictly newer than source version.
