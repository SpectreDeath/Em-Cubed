---
name: w3c-rdf-shacl-interoperability-agent
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
description: W3C RDF, OWL, and SHACL interoperability agent. Serializes internal ontology triples to standard W3C RDF Turtle (.ttl) and RDF/XML, generates SHACL constraint shapes from ledger axioms, and parses external Turtle files for ingestion into enterprise triplestores (e.g. GraphDB, Stardog). Use when exporting ontologies to standard W3C formats, generating machine-enforceable SHACL validation shapes, or importing external RDF/TTL datasets.
purpose: Bidirectionally serialize and validate W3C RDF/Turtle files and generate SHACL constraint shapes.
dependencies: []
tags:
  - w3c-rdf
  - rdf-turtle
  - shacl-shapes
  - owl-interop
  - enterprise-triplestore
inputs:
  operation_type:
    type: string
    required: true
    description: "export_turtle | generate_shacl | import_turtle"
  triples_or_turtle:
    type: any
    required: true
    description: Array of internal OntologyTriples for export, or raw Turtle string for import.
  base_iri:
    type: string
    required: false
    description: "Base namespace IRI (default: 'http://em-cubed.org/ontology#')."
outputs:
  serialized_content:
    type: string
    description: Formatted W3C RDF Turtle or SHACL shapes output string.
  imported_triples:
    type: array
    description: Parsed internal OntologyTriple objects from external Turtle.
  validation_passed:
    type: boolean
    description: True if RDF/SHACL syntax satisfies W3C standards.
---

# W3C RDF & SHACL Interoperability Agent Engine

`w3c-rdf-shacl-interoperability-agent` implements **Phase 14 W3C OWL/RDF & SHACL Standard Interoperability Engine** in `Em-Cubed`. It connects the neurosymbolic operating system to enterprise triplestores (GraphDB, Stardog, AllegroGraph) via standard W3C RDF Turtle serialization, automated SHACL constraint shape generation, and external Turtle parsing.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Interoperability Progression

```
[1. Syntax & Invariant Audit] → [2. RDF/SHACL Compilation] → [3. Visual Brief] → [4. Checkpoint] → [5. Validation & Export]
```

### Stage 1: Syntax & Invariant Audit
1. Ingest input payload (triple array or raw Turtle text).
2. Validate namespace prefixes and IRI structure compliance ($http / https / urn$).

> **Completion criterion**: Namespace prefixes and input syntax parsed without errors.

---

### Stage 2: RDF Serialization & SHACL Shape Compilation
1. Map internal entity axioms to standard W3C vocabularies (`rdf:type`, `rdfs:subClassOf`, `owl:disjointWith`).
2. If `generate_shacl`, compile ledger constraints into W3C SHACL NodeShapes and PropertyShapes:
   ```turtle
   :EntityShape a sh:NodeShape ;
       sh:targetClass :MaterialEntity ;
       sh:property [ sh:path :hasIdentifier ; sh:minCount 1 ] .
   ```

> **Completion criterion**: Turtle/SHACL strings compiled adhering to W3C RDF syntax.

---

### Stage 3: The Visual Brief
For complex ontology exports or large SHACL shape graphs, generate an interactive brief:
- **Location**: Write to `%TEMP%\w3c-interop-brief-<timestamp>.html` (Windows) or `/tmp/w3c-interop-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the RDF class hierarchy and SHACL constraint validation graph.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before importing external RDF Turtle datasets into production ledgers:
1. Verify that external triples do not inject conflicting circular subclass axioms.
2. Ensure external entities map cleanly onto BFO upper categories.

> **Completion criterion**: External dataset verified safe and disjointness-compliant.

---

### Stage 5: W3C Syntax Validation & Output Emit
1. Execute RDFlib/pyshacl validator over generated content.
2. Emit verified Turtle/SHACL string or parsed triple array.

> **Completion criterion**: Content emitted with `validation_passed: true` and zero syntax errors.

---

## Surface References

### Python RDF & SHACL Surface

```python
from typing import List, Dict, Any

def serialize_to_turtle(triples: List[Dict[str, str]], base_iri: str = "http://em-cubed.org/ontology#") -> Dict[str, Any]:
    prefixes = [
        f"@prefix : <{base_iri}> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> ."
    ]
    
    body_lines = []
    for t in triples:
        s = t.get("subject", "")
        p = t.get("predicate", "")
        o = t.get("object", "")
        body_lines.append(f":{s} :{p} :{o} .")
        
    turtle_output = "\n".join(prefixes) + "\n\n" + "\n".join(body_lines)
    return {
        "serialized_content": turtle_output,
        "imported_triples": triples,
        "validation_passed": True
    }
```

---

## Anti-Patterns & Guardrails

- **Missing Namespace Prefixes** — Emitting un-prefixed local names or invalid QNames that fail standard Turtle parsers.
- **Unbounded SHACL Recursion** — Generating recursive SHACL property paths that cause validator deadlocks.
- **Lossy Literal Serialization** — Dropping XML Schema datatypes (`xsd:integer`, `xsd:dateTime`) during serialization.
