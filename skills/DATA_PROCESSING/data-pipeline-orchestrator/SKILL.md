---
name: data-pipeline-orchestrator
domain: DATA_PROCESSING
version: 1.0.0
surfaces:
- python
- prolog
- hy
description: Data pipeline orchestrator for composing, validating, and executing multi-step data transformation workflows.
compatibility: PYTHON
complexity: High
type: Process
category: Data Engineering Skills
estimated execution time: 5-15 minutes
source: community
allowed-tools: '- read

  - write

  - edit

  - bash

  - glob

  - grep

  - codebase_search

  - task

  - sequentialthinking_sequentialthinking

  - webfetch

  - websearch

  - question

  - suggest

  '
---
origin: manual
triggers:
  - etl
  - data_processing
  - workflow
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:30:00Z"
updated_at: "2026-05-02T12:30:00Z"

## Purpose

Multi-surface data pipeline orchestrator that combines Python for data transformation, Prolog for data lineage and constraint validation, and Datalog for recursive data flow rules.

## Description

This skill provides comprehensive data pipeline orchestration:
- Python for data transformation, cleaning, and streaming operations
- Prolog for data lineage tracking, schema validation, and business rule enforcement
- Datalog for recursive dependency resolution and incremental computation

## Examples

### ETL Pipeline with Lineage

```
Input: Raw CSV files with transformation rules
Output: Transformed data with complete lineage graph and quality metrics
```

## Implementation

### Python Pipeline Orchestration

```python
from typing import Dict, List, Optional, Any, AsyncIterator
import asyncio
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum

class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PipelineStage:
    name: str
    func: callable
    dependencies: List[str] = field(default_factory=list)
    schema: Dict = field(default_factory=dict)
    status: StageStatus = StageStatus.PENDING
    error: Optional[str] = None

class DataPipeline:
    """Multi-stage data pipeline orchestrator."""
    
    def __init__(self, name: str):
        self.name = name
        self.stages: Dict[str, PipelineStage] = {}
        self.context: Dict[str, Any] = {}
        self.lineage: List[Dict] = []
    
    def add_stage(self, stage: PipelineStage) -> None:
        """Add a pipeline stage."""
        self.stages[stage.name] = stage
    
    async def execute(self) -> Dict[str, Any]:
        """Execute pipeline stages in dependency order."""
        execution_order = self._topological_sort()
        results = {}
        
        for stage_name in execution_order:
            stage = self.stages[stage_name]
            stage.status = StageStatus.RUNNING
            
            try:
                # Check dependencies
                for dep in stage.dependencies:
                    if dep in results and isinstance(results[dep], Exception):
                        stage.status = StageStatus.SKIPPED
                        stage.error = f"Dependency {dep} failed"
                        results[stage_name] = Exception(stage.error)
                        continue
                
                # Execute stage
                stage_result = await stage.func(self.context)
                results[stage_name] = stage_result
                self.context[stage_name] = stage_result
                stage.status = StageStatus.COMPLETED
                
                # Track lineage
                self.lineage.append({
                    "stage": stage.name,
                    "input": list(stage.dependencies),
                    "output": stage_name,
                    "timestamp": "2026-05-02T12:30:00Z",
                    "status": "success"
                })
                
            except Exception as e:
                stage.status = StageStatus.FAILED
                stage.error = str(e)
                results[stage_name] = e
                self.lineage.append({
                    "stage": stage.name,
                    "error": str(e),
                    "timestamp": "2026-05-02T12:30:00Z",
                    "status": "failed"
                })
        
        return results
    
    def _topological_sort(self) -> List[str]:
        """Sort stages by dependencies."""
        visited = set()
        result = []
        
        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            for dep in self.stages[name].dependencies:
                if dep in self.stages:
                    visit(dep)
            result.append(name)
        
        for stage_name in self.stages:
            visit(stage_name)
        
        return result

async def stream_transform(stream: AsyncIterator[Dict], 
                           transformations: List[callable]) -> AsyncIterator[Dict]:
    """Apply transformations to streaming data."""
    async for record in stream:
        for transform in transformations:
            record = await transform(record)
        yield record

def validate_schema(df: pd.DataFrame, schema: Dict) -> bool:
    """Validate DataFrame against schema."""
    for col, dtype in schema.get("columns", {}).items():
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
        if not pd.api.types.is_dtype_equal(df[col].dtype, dtype):
            raise ValueError(f"Column {col} has wrong type")
    return True
```

### Prolog Data Lineage

```prolog
% Data lineage rules
ancestor_data(RawData, ProcessedData) :-
    data_transformation(RawData, ProcessedData, _, _).

ancestor_data(RawData, FinalOutput) :-
    data_transformation(RawData, Intermediate, _, _),
    ancestor_data(Intermediate, FinalOutput).

% Schema validation
valid_schema(Data, Schema) :-
    findall(Missing, (member(Column, Schema.columns), \+ member(Column, Data)), Missing),
    length(Missing, 0).

% Pipeline constraint validation
pipeline_consistent(Stages, Context) :-
    forall(member(Stage, Stages),
           (stage_input_schema(Stage, RequiredInput),
            schema_satisfied(RequiredInput, Context))).

% Data quality checks
quality_check_passed(Data, Checks) :-
    forall(member(Check, Checks),
           call(Check, Data)).

% Dependency resolution
stage_ready(Stage, CompletedStages) :-
    stage_dependencies(Stage, Dependencies),
    subset(Dependencies, CompletedStages).

% Failure propagation
failure_propagates(FailedStage, AffectedStages, AllStages) :-
    member(Affected, AllStages),
    \+ stage_dependencies(Affected, [FailedStage]),
    \+ (member(Dep, stage_dependencies(Affected, _)), Dep = FailedStage).
```

### Datalog Flow Rules

```datalog
% Data flow dependencies
stage_depends_on("transform", "extract").
stage_depends_on("load", "transform").
stage_depends_on("validate", "extract").

% Transitive dependencies
depends_on(Stage, Dep) :- stage_depends_on(Stage, Dep).
depends_on(Stage, Dep) :- stage_depends_on(Stage, Intermediate),
                            depends_on(Intermediate, Dep).

% Incremental computation
needs_recomputation(Stage, ChangedData) :-
    produces(Stage, Output),
    depends_on_data(Output, ChangedData).

% Parallel execution
can_run_in_parallel(Stage1, Stage2) :-
    stage_depends_on(Stage1, Deps1),
    stage_depends_on(Stage2, Deps2),
    \+ (member(Dep, Deps1), member(Dep, Deps2)).
```

## Testing

```python
# Test pipeline execution
from skills.data_pipeline_orchestrator import DataPipeline, PipelineStage

pipeline = DataPipeline("test")

async def extract(context):
    return {"data": [1, 2, 3]}

async def transform(context):
    data = context["extract"]["data"]
    return {"transformed": [x * 2 for x in data]}

pipeline.add_stage(PipelineStage("extract", extract))
pipeline.add_stage(PipelineStage("transform", transform, dependencies=["extract"]))

# Run pipeline
results = asyncio.run(pipeline.execute())
assert results["transform"]["transformed"] == [2, 4, 6]
```

````
