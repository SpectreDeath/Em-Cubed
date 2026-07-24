---
name: production-rest-governance-agent
description: Demonstrates Phase 6 Production REST API Governance, Visual Graph Exploration, and Audit Trail Rendering.
domain: ONTOLOGY
surfaces:
  - python
  - prolog
  - datalog
  - z3
version: 1.0.0
---

# Production REST Governance Agent Skill

## Overview

The `production-rest-governance-agent` skill demonstrates **Phase 6 Production REST API Governance & Visual Graph Exploration** in `Em-Cubed`.

## Endpoints Exposed

- `POST /api/v1/loopy/execute`: Executes a loopy skill sub-routine with trajectory logging and audit report generation.
- `POST /api/v1/ontology/validate`: Validates structural door schemas + OWL ontology ledger rules.
- `GET /api/v1/ontology/graph-rag`: Queries multi-hop Knowledge Graph paths for an entity.
- `GET /api/v1/ontology/federated-status`: Returns SHA-256 state alignment across federated swarm nodes.

## Interactive Visualization Output

Renders standalone HTML/SVG interactive visualizations for Knowledge Graph paths and `LoopTrajectory` step proof metrics via `KnowledgeGraphVisualizer.render_subgraph_html()`.
