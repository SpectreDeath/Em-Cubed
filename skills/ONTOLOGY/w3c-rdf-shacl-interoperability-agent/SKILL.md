---
name: w3c-rdf-shacl-interoperability-agent
description: Demonstrates Phase 14 W3C OWL/RDF Turtle (.ttl) export, SHACL constraint shape generation, and external Turtle file importing for enterprise triplestores.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
  - datalog
version: 1.0.0
---

# W3C RDF & SHACL Interoperability Agent Skill

## Overview

The `w3c-rdf-shacl-interoperability-agent` skill demonstrates **Phase 14 W3C OWL/RDF & SHACL Standard Interoperability Engine** in `Em-Cubed`.

## Interoperability Workflow

```
[ OntologyTriples & Ledger Constraints ]
                    │
                    ├─► RDFSerializer ────────► RDF Turtle (.ttl) & RDF/XML (.rdf)
                    ├─► SHACLConstraintGen ───► W3C SHACL Shapes (.shacl.ttl)
                    └─► OWLImporter ──────────► Parse External .ttl to Triples
```

## Serialized RDF Turtle Output Example

```turtle
@prefix : <http://em-cubed.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

:FolicAcidSupplier a :SupplyChainEntity .
:FolicAcidSupplier :provides :FolicAcid .
```
