---
name: high-stakes-financial-auditor
description: High-stakes financial transaction auditor utilizing Graph-Path RAG, Constraint-Aware Prompt Steering, and Z3 SMT Symbolic Proof Verification.
domain: ONTOLOGY
surfaces:
  - python
  - z3
  - datalog
version: 1.0.0
---

# High-Stakes Financial Auditor Skill

## Overview

The `high-stakes-financial-auditor` skill demonstrates **Phase 2 Neurosymbolic AI** in `Em-Cubed`. It enforces **zero-hallucination compliance** for financial transactions by combining:

1. **Neurosymbolic Graph-Path RAG**: Traverses multi-hop semantic triples to construct grounded context subgraphs.
2. **Constraint-Aware Prompt Steering**: Injects OWL functional property uniqueness rules and disjoint class boundaries into prompt directives.
3. **Symbolic Proof Verification**: Evaluates financial balance invariants using Z3 SMT solvers and exports JSON-LD compliance audit trails.

## Audit Workflow

```
[ Financial Payout Request ]
           │
           ▼
[ Graph-Path RAG Traversal ]  ──> Traverses (Account -> BelongsTo -> User)
           │
           ▼
[ Constraint Steering ]       ──> Injects "Functional Property: Max 1 Refund per Order"
           │
           ▼
[ Loopy Execution Engine ]    ──> Runs Z3 Solver Verification Sensor
           │
           ▼
[ JSON-LD Audit Report ]      ──> Exports Proof Trace Annotation (Deductive Verification)
```
