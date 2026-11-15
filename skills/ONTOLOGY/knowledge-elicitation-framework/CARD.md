# Skill Summary Card: `knowledge-elicitation-framework`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        knowledge-elicitation-framework           │
│ Category:    ONTOLOGY / Knowledge Elicitation Pipeline │
│ Invocation:  /knowledge-elicitation-framework          │
│ Trigger:     "elicit ontology", "pmest analysis",      │
│              "ontoclean partition", "derive cqs",      │
│              "common logic echo", "bfo alignment"      │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      6-stage operational pipeline compiling    │
│              natural language text into formal BFO/CCO │
│              ontologies with OntoClean rigor.          │
└────────────────────────────────────────────────────────┘
```

---

## The 6-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Strategic DSQ** | Deconstruct concerns into precision DSQs | Domain-Specific Questions | Granular questions targeting gaps formulated |
| **2. PMEST Faceting** | Classify concepts into 5 fundamental facets | PMEST Facet Map | All domain concepts assigned to PMEST buckets |
| **3. CQ Derivation** | Synthesize formal Competency Questions | Competency Questions List | Formal CQs generated with required classes |
| **4. OntoClean Partition**| Partition Independent vs Role & mint IRIs | Opaque IRI Registry | Entities partitioned with opaque IRIs |
| **5. Common Logic Echo**| Generate natural language confirmation dialogue | Echo Dialogue Script | Common logic echo verified with domain expert |
| **6. BFO Alignment** | Ground into BFO/CCO and emit triples | Formal OntologyTriples | Triples validated under BFO upper ontology |

---

## Invariants & Guardrails

- [ ] **Opaque IRIs**: All entities minted with non-semantic identifiers (`PREFIX_XXXXXX`).
- [ ] **OntoClean Rigor**: Rigid independent things separated from extrinsic relative roles.
- [ ] **PMEST Exhaustiveness**: Every elicited concept classified under Personality, Matter, Energy, Space, or Time.
