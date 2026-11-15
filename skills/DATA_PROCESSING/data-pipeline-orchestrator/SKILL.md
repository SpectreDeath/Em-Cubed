---
name: data-pipeline-orchestrator
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
description: Multi-stage asynchronous DAG data pipeline orchestration and transformation engine. Sorts transformation stages into topological execution orders, validates input/output schemas using Pandas and Prolog, captures end-to-end data lineage and provenance ancestry in Prolog (ancestor_data/2), resolves transitive stage dependencies in Datalog, and executes parallel or streaming transformations in Python. Use when composing ETL workflows, ensuring schema conformance across transformation steps, or auditing data lineage.
purpose: Compose, validate, and execute asynchronous multi-stage DAG data transformation pipelines with Prolog lineage tracking.
dependencies: []
tags:
  - data-pipeline-orchestrator
  - dag-execution
  - data-lineage
  - prolog-provenance
  - datalog-rules
  - etl-workflow
inputs:
  pipeline_name:
    type: string
    required: true
    description: Identifier name for the data pipeline (e.g. `'etl_sales_aggregation'`).
  stages:
    type: array
    required: true
    description: 'List of pipeline stage specifications `[{''name'': ''extract'', ''dependencies'': []}, {''name'': ''transform'', ''dependencies'': [''extract'']}]`.'
  context_data:
    type: object
    required: false
    description: Initial context dictionary containing raw input datasets or parameters.
outputs:
  execution_order:
    type: array
    description: Topologically sorted list of stage execution names.
  stage_results:
    type: object
    description: Dictionary mapping each stage name to its execution result or status.
  lineage_graph:
    type: array
    description: Provenance lineage records tracing input-to-output data ancestry.
  pipeline_status:
    type: string
    description: Overall pipeline execution status (`'completed'`, `'failed'`, or `'partial'`).
---

# Data Pipeline Orchestrator Engine

`data-pipeline-orchestrator` composes, validates, and executes asynchronous **Directed Acyclic Graph (DAG) data transformation workflows**. It enforces **topological ordering and schema validation in Python**, tracks **data lineage ancestry in Prolog**, and manages **recursive dependencies in Datalog**:

$$\text{DAG} = (V, E), \quad u \to v \in E \implies \text{Order}(u) < \text{Order}(v)$$

$$\text{Prolog Lineage: } \text{ancestor\_data}(D_{\text{raw}}, D_{\text{out}}) \leftarrow \text{transformed}(D_{\text{raw}}, D_{\text{int}}) \land \text{ancestor\_data}(D_{\text{int}}, D_{\text{out}})$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Pipeline Progression

```
[1. Stage & Dependency Ingest] → [2. Topological DAG Sort & Cycle Proof] → [3. Visual Brief] → [4. Checkpoint] → [5. Async Execution & Lineage Emit]
```

### Stage 1: Stage & Dependency Ingest
1. Ingest `pipeline_name`, `stages` list, and `context_data`.
2. Assert that all declared stage dependencies exist within the stages collection.

> **Completion criterion**: Clean pipeline DAG definition verified.

---

### Stage 2: Topological DAG Sort & Cycle Proof
1. Construct dependency graph adjacency list.
2. Execute Kahn's algorithm or recursive DFS in Python to compute topological execution order:
   `["extract", "validate", "transform", "load"]`.
3. Prove acyclicity in Prolog: $\neg \exists \text{cycle}(G)$.

> **Completion criterion**: Valid topological execution sequence resolved.

---

### Stage 3: The Visual Brief
For data pipeline orchestration and lineage graphs, generate an interactive brief:
- **Location**: Write to `%TEMP%\data-pipeline-brief-<timestamp>.html` (Windows) or `/tmp/data-pipeline-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render DAG execution flowchart, data provenance lineage tree, and stage execution latency / status waterfall.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before stage execution:
1. Verify prerequisite readiness: if a parent stage fails, mark child stages as `skipped`.
2. Validate input schema compatibility against context data.

> **Completion criterion**: Dependency readiness and schema gates verified.

---

### Stage 5: Async Execution & Lineage Emission
1. Execute stages asynchronously in topological order.
2. Record stage execution timestamps and input/output provenance in `lineage_graph`.
3. Emit complete `PipelineResult` record.

> **Completion criterion**: Full pipeline execution and lineage payload emitted.

---

## Surface References

### Prolog Lineage Surface

```prolog
:- module(data_lineage, [
    ancestor_data/2,
    stage_ready/2,
    valid_dag/1
]).

ancestor_data(Raw, Processed) :-
    transformation(Raw, Processed).
ancestor_data(Raw, Final) :-
    transformation(Raw, Inter),
    ancestor_data(Inter, Final).

stage_ready(Stage, Completed) :-
    stage_deps(Stage, Deps),
    subset(Deps, Completed).
```

### Python Orchestrator Surface

```python
from typing import Dict, List, Any, Optional, Callable

def topological_sort(stages: List[Dict[str, Any]]) -> List[str]:
    stage_map = {s["name"]: s for s in stages}
    adj = {s["name"]: s.get("dependencies", []) for s in stages}
    
    visited = set()
    temp = set()
    order = []
    
    def visit(name: str):
        if name in temp:
            raise ValueError(f"cyclic_dependency_detected: Stage '{name}' is in a cycle.")
        if name not in visited:
            temp.add(name)
            for dep in adj.get(name, []):
                if dep in stage_map:
                    visit(dep)
            temp.remove(name)
            visited.add(name)
            order.append(name)
            
    for s in stages:
        if s["name"] not in visited:
            visit(s["name"])
            
    return order

def execute_pipeline(
    pipeline_name: str,
    stages: List[Dict[str, Any]],
    context_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    order = topological_sort(stages)
    context = dict(context_data or {})
    results = {}
    lineage = []
    
    for stage_name in order:
        stage = next(s for s in stages if s["name"] == stage_name)
        deps = stage.get("dependencies", [])
        
        # Check parent dependencies
        failed_dep = next((d for d in deps if results.get(d, {}).get("status") == "failed"), None)
        if failed_dep:
            results[stage_name] = {"status": "skipped", "error": f"Parent '{failed_dep}' failed."}
            lineage.append({"stage": stage_name, "status": "skipped", "inputs": deps, "output": None})
            continue
            
        # Execute mock/provided transform
        func = stage.get("func", lambda ctx: {"data": "processed"})
        try:
            res = func(context) if callable(func) else {"status": "ok"}
            results[stage_name] = {"status": "completed", "output": res}
            context[stage_name] = res
            lineage.append({"stage": stage_name, "status": "completed", "inputs": deps, "output": stage_name})
        except Exception as exc:
            results[stage_name] = {"status": "failed", "error": str(exc)}
            lineage.append({"stage": stage_name, "status": "failed", "inputs": deps, "error": str(exc)})
            
    status = "completed" if all(r.get("status") == "completed" for r in results.values()) else "partial"
    return {
        "execution_order": order,
        "stage_results": results,
        "lineage_graph": lineage,
        "pipeline_status": status
    }
```

---

## Anti-Patterns & Guardrails

- **Cyclic Dependency Deadlocks** — Configuring mutual dependencies between stages ($A \to B \to A$), crashing pipeline execution.
- **Cascading Silent Failures** — Continuing downstream execution when prerequisite parent transforms have failed or thrown errors.
- **Untracked Transformation Lineage** — Executing multi-stage mutations without recording input-to-output provenance in the lineage graph.
