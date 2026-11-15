# Skill Summary Card: `w3c-rdf-shacl-interoperability-agent`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        w3c-rdf-shacl-interoperability-agent      │
│ Category:    ONTOLOGY / W3C Standards & SHACL Shapes   │
│ Invocation:  /w3c-rdf-shacl-interoperability-agent     │
│ Trigger:     "export rdf turtle", "generate shacl",    │
│              "import turtle file", "w3c owl export"    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Bidirectional W3C RDF Turtle/XML          │
│              serialization, SHACL shape compilation,   │
│              and external dataset parsing.             │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Syntax Audit** | Validate IRI prefixes and input syntax | Namespace Context AST | Prefix declarations & syntax valid |
| **2. Compilation** | Compile RDF Turtle or SHACL shape graph | Formatted RDF Buffer | Valid Turtle/SHACL syntax emitted |
| **3. Visual Brief** | Render class hierarchy and SHACL constraint DAG | `%TEMP%\w3c-interop-brief-*.html`| Dark theme HTML export brief |
| **4. Checkpoint** | Validate external imports against core axioms | Safety Gate Record | Zero circular subclassing or collisions |
| **5. W3C Validation** | Execute RDFlib / pyshacl validation | Verified Artifact String | Syntax certified under W3C standard |

---

## Invariants & Guardrails

- [ ] **W3C Syntax Conformity**: Output must parse validly with standard RDFlib Turtle parser.
- [ ] **SHACL Shape Precision**: All generated property shapes must include `sh:path` and explicit cardinality constraints.
- [ ] **Explicit Base IRI**: Base IRI prefix must resolve to a valid URI scheme.
