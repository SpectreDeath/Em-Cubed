# Skill Summary Card: `skill-taxonomy`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-taxonomy                            │
│ Category:    META_ENGINEERING / Prolog Ontology       │
│ Invocation:  /skill-taxonomy                           │
│ Trigger:     "skill taxonomy", "ontology ground truth",│
│              "query professions", "resolve ancestry",  │
│              "recommend materials", "subskill tree"    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Declarative Prolog ontology ground truth  │
│              for professions, domains, literature      │
│              references, and subskill dependency trees.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest query predicate & argument parameters | Ontology Query AST | Supported predicate verified |
| **2. Prolog Goal** | Execute query goal against `skill_taxonomy.pl` | Prolog Goal Solution | Knowledge base unifications |
| **3. Visual Brief** | Render profession-domain graph & subskill trees | `%TEMP%\skill-taxonomy-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate fact grounding or engage built-in fallback | Grounding Gate Record | Grounded facts certified |
| **5. Model Emission**| Format query solutions & emit structured payload | `TaxonomyQueryResult` Payload| Full ontology payload emitted |

---

## Invariants & Guardrails

- [ ] **Ontological Grounding Invariant**: Terms must exist in `skill_taxonomy.pl`.
- [ ] **Acyclic Subskill Hierarchy**: No circular parent-child dependency loops.
- [ ] **Literature Verification**: Canonical domains backed by verified textbooks.
