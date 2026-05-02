---
Domain: AUTOMATION
Version: 1.0.0
Complexity: High
Type: Synthesis
Category: Workflow Skills
Estimated Execution Time: 5-15 minutes
name: workflow-synthesiser
Source: community
---
origin: manual
triggers:
  - automation
  - workflow_generation
  - process_synthesis
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:30:00Z"
updated_at: "2026-05-02T12:30:00Z"

## Purpose

Multi-surface workflow synthesizer that uses Python for process optimization, Prolog for logical workflow validation, and Hy for adaptive workflow adaptation and execution planning.

## Description

This skill synthesizes workflows by:
- Python for process mining, optimization, and task scheduling
- Prolog for constraint validation and logical workflow correctness
- Hy for fuzzy workflow scoring and adaptive execution strategies

## Examples

### Automated Report Generation Workflow

```
Input: Data sources, report template, delivery requirements
Output: Optimized workflow with execution schedule and failure handling
```

## Implementation

### Python Process Optimization

```python
from typing import Dict, List, Callable, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import itertools
import heapq

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class Task:
    id: str
    name: str
    func: Callable
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 1.0
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class Workflow:
    id: str
    tasks: Dict[str, Task] = field(default_factory=dict)
    context: Dict = field(default_factory=dict)
    
    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task

class WorkflowSynthesizer:
    """Synthesize and optimize workflows."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
    
    def create_workflow(self, workflow_id: str) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(workflow_id)
        self.workflows[workflow_id] = workflow
        return workflow
    
    def optimize_order(self, workflow: Workflow) -> List[str]:
        """Optimize task execution order using topological sort with priorities."""
        in_degree = {task_id: 0 for task_id in workflow.tasks}
        
        for task in workflow.tasks.values():
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.id] += 1
        
        # Priority queue
        queue = [(task.priority, task.id) for task_id, task in workflow.tasks.items() 
                 if in_degree[task_id] == 0]
        heapq.heapify(queue)
        
        result = []
        while queue:
            _, task_id = heapq.heappop(queue)
            result.append(task_id)
            
            for task in workflow.tasks.values():
                if task_id in task.dependencies:
                    in_degree[task.id] -= 1
                    if in_degree[task.id] == 0:
                        heapq.heappush(queue, (task.priority, task.id))
        
        return result
    
    def critical_path(self, workflow: Workflow) -> List[str]:
        """Calculate critical path for workflow."""
        # Forward pass - earliest start times
        earliest_start = {}
        for task_id in self.optimize_order(workflow):
            task = workflow.tasks[task_id]
            deps_end = max([earliest_start.get(dep, 0) + 
                           workflow.tasks[dep].estimated_duration 
                           for dep in task.dependencies if dep in earliest_start], default=0)
            earliest_start[task_id] = deps_end
        
        # Backward pass - latest start times
        latest_start = {}
        total_duration = max(earliest_start.get(t, 0) + workflow.tasks[t].estimated_duration 
                            for t in workflow.tasks)
        
        for task_id in reversed(self.optimize_order(workflow)):
            task = workflow.tasks[task_id]
            successors = [t.id for t in workflow.tasks.values() if task_id in t.dependencies]
            if successors:
                min_successor_start = min(latest_start.get(s, total_duration) 
                                         for s in successors)
                latest_start[task_id] = min_successor_start - task.estimated_duration
            else:
                latest_start[task_id] = total_duration - task.estimated_duration
        
        # Critical tasks
        return [t for t in workflow.tasks if earliest_start[t] == latest_start[t]]
    
    def parallel_execution_plan(self, workflow: Workflow) -> List[List[str]]:
        """Create parallel execution batches."""
        levels = []
        assigned = set()
        
        while len(assigned) < len(workflow.tasks):
            level = []
            for task_id, task in workflow.tasks.items():
                if task_id in assigned:
                    continue
                if all(dep in assigned for dep in task.dependencies):
                    level.append(task_id)
            
            levels.append(level)
            assigned.update(level)
        
        return levels

def workflow_similarity(wf1: Workflow, wf2: Workflow) -> float:
    """Calculate similarity between two workflows."""
    tasks1 = set(wf1.tasks.keys())
    tasks2 = set(wf2.tasks.keys())
    
    common_tasks = tasks1 & tasks2
    union_tasks = tasks1 | tasks2
    
    return len(common_tasks) / len(union_tasks) if union_tasks else 0.0

def generate_conditional_tasks(workflow: Workflow, conditions: Dict[str, Callable]) -> None:
    """Add conditional tasks to workflow."""
    for condition_name, condition_func in conditions.items():
        task = Task(
            id=f"conditional_{condition_name}",
            name=f"Check {condition_name}",
            func=condition_func,
            priority=10
        )
        workflow.add_task(task)
```

### Prolog Workflow Validation

```prolog
% Workflow structure validation
valid_workflow(Workflow) :-
    workflow_tasks(Workflow, Tasks),
    acyclic(Tasks),
    no_orphan_tasks(Tasks).

% Acyclicity check
acyclic(Tasks) :-
    topological_sort(Tasks, _).

topological_sort([], []).
topological_sort(Tasks, [H|T]) :-
    select(Task, Tasks, Remaining),
    no_unresolved_dependencies(Task, Remaining),
    topological_sort(Remaining, T).

no_unresolved_dependencies(Task, Tasks) :-
    task_dependencies(Task, Deps),
    \+ (member(Dep, Deps), member(Dep, Tasks)).

% Task dependency rules
requires_completion(Prerequisite, Dependent) :-
    task_dependencies(Dependent, Prerequisites),
    member(Prerequisite, Prerequisites).

% Workflow consistency
consistent_workflow(Workflow, Context) :-
    workflow_tasks(Workflow, Tasks),
    forall(member(Task, Tasks),
           task_satisfies_constraints(Task, Context)).

% Error handling patterns
task_can_retry(Task) :-
    task_max_retries(Task, Max),
    task_retry_count(Task, Count),
    Count < Max.

failure_propagation(FailedTask, AffectedTasks, AllTasks) :-
    member(Affected, AllTasks),
    depends_on(FailedTask, Affected),
    \+ task_can_retry(Affected).

% Resource allocation
sufficient_resources(Tasks, Resources) :-
    findall(Req, (member(Task, Tasks), task_resource_requirement(Task, Req)), Reqs),
    total_resources(Reqs, TotalReq),
    sufficient_resources(TotalReq, Resources).

% Deadlock detection
potential_deadlock(Tasks) :-
    member(A, Tasks),
    member(B, Tasks),
    requires(A, B),
    requires(B, A),
    A \= B.
```

### Hy Adaptive Execution

```hy
(defn workflow-score [workflow context factors]
  "Score workflow for specific context and requirements"
  (let [efficiency (get factors "efficiency" 1.0)
        reliability (get factors "reliability" 1.0)
        cost (get factors "cost" 1.0)
        adaptability (get factors "adaptability" 1.0)]
    (/ (+ (* efficiency 0.4) (* reliability 0.3) (* (- 1 cost) 0.2) (* adaptability 0.1)) 1.0)))

(defn adapt-workflow [base-workflow context-changes]
  "Adapt workflow based on context changes"
  (let [adaptation-rules (get context-changes "rules" [])
        modified-tasks (map (fn [rule]
                             (let [task-id (get rule "task")
                                   new-params (get rule "params" {})]
                               [task-id new-params]))
                           adaptation-rules)]
    (for [task base-workflow.tasks]
      (if (in (get task "id") (map first modified-tasks))
          (let [new-params (second (find (fn [t] (= (first t) (get task "id"))) modified-tasks))]
            (assoc task "params" (merge (get task "params" {}) new-params))
          task))))

(defn execution-risk [workflow historical-data]
  "Assess execution risk based on historical data"
  (let [failure-rates (map (fn [task] (get historical-data (get task "id") "failure_rate" 0)) workflow.tasks)
        avg-risk (mean failure-rates)
        max-risk (max failure-rates)
        risk-variance (variance failure-rates)]
    {:average_risk avg-risk :worst_case max-risk :stability (- 1 risk-variance)}))

(defn dynamic-prioritization [tasks current-state context]
  "Dynamically prioritize tasks based on state and context"
  (let [urgency-scores (map (fn [task]
                              (let [base-priority (get task "priority" 1)
                                    deadline-factor (if (get task "deadline")
                                                     (/ 1 (- (get task "deadline") (current-state "time")))
                                                     1)
                                    dependency-factor (if (get task "dependencies")
                                                         (len (get task "dependencies"))
                                                         0)]
                                (* base-priority deadline-factor dependency-factor)))
                            tasks)]
    (zip tasks urgency-scores)))

(defn workflow-optimization [base-workflow objectives constraints]
  "Optimize workflow for given objectives and constraints"
  (let [candidates (generate-variants base-workflow)
        scored (map (fn [w] [w (workflow-score w objectives)]) candidates)
        valid (filter (fn [pair] (satisfies-constraints (first pair) constraints)) scored)]
    (apply max valid :key (fn [pair] (second pair)))))

(defn execution-monitoring [workflow execution-log]
  "Monitor execution and suggest adaptations"
  (let [delays (filter (fn [entry] (> (get entry "actual" 0) (get entry "expected" 0))) execution-log)
        error-rate (/ (len delays) (len execution-log))
        bottlenecks (group-by (fn [e] (get e "task")) delays)]
    {:error_rate error-rate :bottlenecks bottlenecks :suggested_adjustments (suggest-adaptations bottlenecks)}))
```

## Testing

```python
# Test workflow synthesis
from skills.workflow_synthesiser import WorkflowSynthesizer, Task, TaskStatus

synthesizer = WorkflowSynthesizer()
wf = synthesizer.create_workflow("test")

async def task1(context):
    return {"result": 1}

async def task2(context):
    return {"result": 2}

wf.add_task(Task("t1", "Task 1", task1, priority=2))
wf.add_task(Task("t2", "Task 2", task2, dependencies=["t1"], priority=1))

order = synthesizer.optimize_order(wf)
assert order[0] == "t1"
assert order[1] == "t2"

critical = synthesizer.critical_path(wf)
assert len(critical) > 0
```