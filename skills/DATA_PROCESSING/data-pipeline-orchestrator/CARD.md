# Skill Summary Card: `data-pipeline-orchestrator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        data-pipeline-orchestrator                │
│ Category:    DATA_PROCESSING / Pipeline Orchestration  │
│ Invocation:  /data-pipeline-orchestrator               │
│ Trigger:     "data pipeline orchestrator", "etl dag",  │
│              "topological execution", "data lineage",  │
│              "pipeline transform", "provenance graph"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compose, validate & execute multi-stage   │
│              DAG data pipelines with topological sort  │
│              and Prolog data lineage ancestry tracking.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest pipeline name, stage definitions & context| Pipeline DAG AST | Stages & dependencies parsed|
| **2. DAG Sort** | Compute topological order & prove DAG acyclicity| Topological Execution Array| Acyclicity certified in Prolog|
| **3. Visual Brief** | Render DAG execution flowchart & lineage tree | `%TEMP%\data-pipeline-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate dependency readiness & schema gates | Stage Gate Record | Prerequisite status checked |
| **5. Model Emission**| Execute stages, record provenance & emit payload | `PipelineResult` Payload | Full pipeline payload emitted |

---

## Invariants & Guardrails

- [ ] **Acyclic DAG Invariant**: No circular dependency cycles permitted.
- [ ] **Failure Isolation**: Child stages skipped automatically if parent fails.
- [ ] **Lineage Provenance**: Every output linked to its input ancestors in Prolog.
