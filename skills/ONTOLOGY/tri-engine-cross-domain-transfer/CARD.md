# Skill Summary Card: `tri-engine-cross-domain-transfer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        tri-engine-cross-domain-transfer          │
│ Category:    ONTOLOGY / Cross-Domain Knowledge Mapping │
│ Invocation:  /tri-engine-cross-domain-transfer         │
│ Trigger:     "transfer domain knowledge",              │
│              "map concept taxonomy", "bfo transfer",   │
│              "cross-domain triples", "align ontology"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Map concept taxonomies and transfer       │
│              relational triples across domain silos    │
│              via shared BFO upper ontology categories. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Source Invariants**| Parse source triples and domain taxonomy | Source Graph AST | Syntax and taxonomy valid |
| **2. BFO Alignment** | Map concepts through BFO upper categories | Alignment Mapping | Shared BFO upper category identified |
| **3. Visual Brief** | Render cross-domain bipartite taxonomy graph | `%TEMP%\cross-domain-transfer-brief-*.html`| Dark theme HTML mapping brief |
| **4. Checkpoint** | Validate target domain disjointness axioms | Safety Gate Record | Target domain consistency verified |
| **5. Translation** | Apply term substitutions & emit triples | Transferred Triples | Output triples validated in target domain |

---

## Invariants & Guardrails

- [ ] **BFO Category Preservation**: `Continuant` $\to$ `Continuant`, `Occurrent` $\to$ `Occurrent`.
- [ ] **Alignment Threshold**: Alignment confidence must reach $\ge 0.80$.
- [ ] **Relational Integrity**: Triples must preserve predicate valence and directionality.
