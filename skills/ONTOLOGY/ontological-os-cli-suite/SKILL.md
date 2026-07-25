---
name: ontological-os-cli-suite
description: Demonstrates Phase 11 End-to-End Ontological OS CLI Suite, executing terminal subcommands for validation, elicitation, truthmaker semantics, concept induction, visualization, and migration.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - z3
  - datalog
version: 1.0.0
---

# Ontological OS CLI Suite Skill

## Overview

The `ontological-os-cli-suite` skill demonstrates **Phase 11 End-to-End Ontological OS CLI Suite** in `Em-Cubed`.

## Terminal Command Usage

```bash
# 1. Door & Ledger Rule Validation
em3 ontology validate --subject USO_1001 --predicate has_origin --object Uruguay --functional-prop has_origin

# 2. 6-Stage Knowledge Elicitation Pipeline
em3 ontology elicit --domain-prompt "Supply Chain Folic Acid Sourcing in South America"

# 3. Kit Fine's Truthmaker Semantics
em3 ontology truthmaker --proposition "Ingredient Compliance" --predicates has_ingredient has_origin

# 4. Description Logic Concept Induction
em3 ontology induce --subclass-name AutonomousVehicle --parent-class Vehicle

# 5. Interactive Knowledge Graph Visualization
em3 ontology visualize --output-html graph_dashboard.html

# 6. Versioned Schema Migration
em3 ontology migrate --from-pred has_origin --to-pred has_country_of_origin
```
