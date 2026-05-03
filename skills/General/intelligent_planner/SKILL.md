---
name: Intelligent Task Planner
Domain: General
Version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
triggers:
  - planning
  - task
  - orchestration
  - scheduling
  - multi_surface
  - coordination
---

## Purpose

Demonstrate intelligent task planning and execution using multi-surface orchestration across Python, Prolog, and Hy Lisp.

## Description

A comprehensive AI planning system that leverages the strengths of each execution surface:
- **Python**: Main orchestration, numerical computations, API integrations
- **Prolog**: Logical constraints, rule-based reasoning, constraint satisfaction
- **Hy**: Fuzzy logic, heuristic search, symbolic computation

This skill showcases how complex AI problems can be solved by combining different programming paradigms in a coordinated workflow.

## Examples

### Project Resource Allocation

**Problem**: Allocate developers to projects with complex constraints and optimization goals.

**Solution Approach**:
1. **Python**: Parse requirements, manage workflow, generate reports
2. **Prolog**: Handle hard constraints (skills, availability, dependencies)
3. **Hy**: Fuzzy optimization of soft constraints (preferences, workload balance)

### Smart Home Automation

**Problem**: Optimize home energy usage with multiple constraints and preferences.

**Solution Approach**:
1. **Python**: Interface with IoT devices, collect sensor data
2. **Prolog**: Logical rules for device interactions and safety constraints
3. **Hy**: Fuzzy logic for comfort preferences and energy optimization

## Implementation

### Python Orchestration Layer

```python
"""
Intelligent Task Planner - Main Orchestration
Coordinates Python, Prolog, and Hy surfaces for complex planning tasks.
"""
import asyncio
import json
from typing import Dict, Any, List
from dataclasses import dataclass

from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface

@dataclass
class PlanningTask:
    """Represents a planning task with multi-surface execution."""
    name: str
    python_code: str = ""
    prolog_facts: List[str] = None
    prolog_queries: List[str] = None
    hy_code: str = ""
    context: Dict[str, Any] = None

    def __post_init__(self):
        self.prolog_facts = self.prolog_facts or []
        self.prolog_queries = self.prolog_queries or []
        self.context = self.context or {}

class IntelligentPlanner:
    """Multi-surface intelligent planner."""

    def __init__(self):
        self.python_surface = PythonSurface()
        self.prolog_surface = PrologSurface()
        self.hy_surface = HySurface()

    async def execute_task(self, task: PlanningTask) -> Dict[str, Any]:
        """Execute a planning task across multiple surfaces."""
        results = {
            "task_name": task.name,
            "python_result": None,
            "prolog_results": [],
            "hy_result": None,
            "final_decision": None,
            "execution_time": None
        }

        # Phase 1: Python preprocessing and data preparation
        if task.python_code:
            python_result = await self.python_surface.execute(task.python_code, task.context)
            results["python_result"] = python_result
            if python_result["status"] != "ok":
                return {"error": f"Python phase failed: {python_result.get('message', 'Unknown error')}"}

        # Phase 2: Prolog constraint satisfaction and logical reasoning
        if task.prolog_facts and self.prolog_surface.available:
            # Load facts
            for fact in task.prolog_facts:
                self.prolog_surface.execute(fact)

            # Execute queries
            prolog_results = []
            for query in task.prolog_queries:
                result = self.prolog_surface.execute(query)
                prolog_results.append({"query": query, "result": result})
            results["prolog_results"] = prolog_results

        # Phase 3: Hy fuzzy logic and heuristic optimization
        if task.hy_code and self.hy_surface.available:
            hy_result = self.hy_surface.execute(task.hy_code, task.context)
            results["hy_result"] = hy_result

        # Phase 4: Python postprocessing and decision synthesis
        synthesis_code = f"""
# Synthesize results from all surfaces
python_data = {results['python_result']['value'] if results['python_result'] else None!r}
prolog_data = {results['prolog_results']!r}
hy_data = {results['hy_result']['value'] if results['hy_result'] else None!r}

# Intelligent decision synthesis
if python_data and prolog_data and hy_data:
    final_score = (python_data.get('score', 0) * 0.4 +
                   prolog_data[0]['result'].get('confidence', 0) * 0.3 +
                   hy_data.get('optimization_score', 0) * 0.3)
    decision = "approved" if final_score > 0.7 else "needs_review"
else:
    decision = "insufficient_data"

{{
    "decision": decision,
    "confidence_score": final_score if 'final_score' in locals() else 0.0,
    "python_contribution": python_data,
    "prolog_contribution": len(prolog_data),
    "hy_contribution": hy_data
}}
"""
        final_result = await self.python_surface.execute(synthesis_code, {})
        if final_result["status"] == "ok":
            results["final_decision"] = final_result["value"]

        return results

# Example usage
async def main():
    planner = IntelligentPlanner()

    # Define a resource allocation task
    allocation_task = PlanningTask(
        name="Developer Allocation",
        python_code="""
# Parse project requirements
projects = [
    {"name": "Web App", "skills": ["python", "javascript"], "priority": 8},
    {"name": "ML Model", "skills": ["python", "statistics"], "priority": 9},
    {"name": "Database", "skills": ["sql", "python"], "priority": 6}
]

developers = [
    {"name": "Alice", "skills": ["python", "javascript"], "capacity": 100},
    {"name": "Bob", "skills": ["python", "statistics", "sql"], "capacity": 80},
    {"name": "Charlie", "skills": ["javascript", "sql"], "capacity": 90}
]

# Calculate basic metrics
total_capacity = sum(d['capacity'] for d in developers)
project_complexity = sum(p['priority'] for p in projects)

{"projects": projects, "developers": developers,
 "total_capacity": total_capacity, "complexity_score": project_complexity}
""",
        prolog_facts=[
            "developer(alice, [python, javascript], 100).",
            "developer(bob, [python, statistics, sql], 80).",
            "developer(charlie, [javascript, sql], 90).",
            "project(web_app, [python, javascript], 8).",
            "project(ml_model, [python, statistics], 9).",
            "project(database, [sql, python], 6).",
            # Skills matching rules
            "can_assign(D, P) :- developer(D, Skills, _), project(P, ReqSkills, _), subset(ReqSkills, Skills).",
            "subset([], _).",
            "subset([H|T], List) :- member(H, List), subset(T, List)."
        ],
        prolog_queries=[
            "can_assign(alice, web_app).",
            "can_assign(bob, ml_model).",
            "can_assign(charlie, database)."
        ],
        hy_code="""
; Fuzzy optimization for workload balance
(defn workload-balance [assignments]
  "Calculate fuzzy balance score for developer assignments"
  (let [workloads (list-comp (sum (lfor [proj assigned] assignments
                                       (if (= assigned developer) proj-workload 0)))
                            [developer (set (lfor [d _ _] assignments d))])]
    (if workloads
      (let [avg (/ (sum workloads) (len workloads))
            variance (sum (lfor w workloads (** (- w avg) 2)))
            balance-score (/ 1 (+ 1 variance))]  ; Fuzzy balance metric
        balance-score)
      0.0)))

; Example assignments evaluation
(setv sample-assignments
      [{'developer 'alice 'project 'web_app 'workload 60}
       {'developer 'bob 'project 'ml_model 'workload 70}
       {'developer 'charlie 'project 'database 'workload 50}])

{"optimization_score" (workload-balance sample-assignments)
 "recommendations" ['alice 'bob 'charlie]}
"""
    )

    result = await planner.execute_task(allocation_task)
    print("Planning Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

### Prolog Constraint Layer

```prolog
% Constraint satisfaction for resource allocation

% Developer capabilities
developer(alice, [python, javascript], 100).
developer(bob, [python, statistics, sql], 80).
developer(charlie, [javascript, sql], 90).

% Project requirements
project(web_app, [python, javascript], 8).
project(ml_model, [python, statistics], 9).
project(database, [sql, python], 6).

% Skills compatibility
has_skill(D, S) :- developer(D, Skills, _), member(S, Skills).
meets_requirements(D, P) :- project(P, ReqSkills, _),
                           forall(member(S, ReqSkills), has_skill(D, S)).

% Workload constraints
developer_capacity(D, C) :- developer(D, _, C).
project_priority(P, Pr) :- project(P, _, Pr).

% Optimal assignment constraints
valid_assignment(D, P, Workload) :-
    meets_requirements(D, P),
    developer_capacity(D, Capacity),
    project_priority(P, Priority),
    Workload =< Capacity,
    Workload >= Priority * 5.  % Minimum workload based on priority

% Find optimal assignments
optimal_allocation(Assignments) :-
    findall([D, P, W],
            (developer(D, _, _), project(P, _, _), valid_assignment(D, P, W)),
            AllPossible),
    % Select non-conflicting assignments with maximum total priority
    select_optimal(AllPossible, Assignments).

% Helper predicates
member(X, [X|_]).
member(X, [_|T]) :- member(X, T).

forall(P, Q) :- not((P, not(Q))).

select_optimal(Possible, Optimal) :- Possible = Optimal.  % Simplified
```

### Hy Fuzzy Optimization Layer

```hy
; Fuzzy logic optimization for multi-criteria decision making

(defn fuzzy-membership [value low medium high]
  "Triangular membership function"
  (cond [(and (>= value low) (< value medium))
         (/ (- value low) (- medium low))]
        [(and (>= value medium) (<= value high))
         (/ (- high value) (- high medium))]
        [True 0.0]))

(defn skill-match-score [dev-skills proj-skills]
  "Fuzzy skill matching score"
  (let [required-count (len proj-skills)
        matched-count (sum (lfor skill proj-skills (if (in skill dev-skills) 1 0)))
        match-ratio (/ matched-count required-count)]
    (fuzzy-membership match-ratio 0.0 0.7 1.0)))

(defn workload-balance-score [current-workload capacity]
  "Fuzzy workload balance score"
  (let [utilization-ratio (/ current-workload capacity)]
    (fuzzy-membership utilization-ratio 0.0 0.8 1.0)))

(defn priority-satisfaction [assigned-priority project-priority]
  "How well priority is satisfied"
  (fuzzy-membership assigned-priority 0 project-priority (* project-priority 1.2)))

(defn composite-fitness [assignment]
  "Calculate overall fitness using fuzzy composition"
  (let [skill-score (skill-match-score (:dev-skills assignment) (:proj-skills assignment))
        workload-score (workload-balance-score (:workload assignment) (:capacity assignment))
        priority-score (priority-satisfaction (:priority assignment) (:proj-priority assignment))
        ; Weighted combination
        overall-score (+ (* skill-score 0.5) (* workload-score 0.3) (* priority-score 0.2))]
    overall-score))

(defn optimize-assignment [possible-assignments]
  "Find optimal assignment using fuzzy fitness"
  (if possible-assignments
    (let [scored (lfor assignment possible-assignments
                      (assoc assignment "fitness" (composite-fitness assignment)))]
      (max scored :key (fn [a] (get a "fitness"))))
    None))

; Example optimization
(setv candidates
      [{"dev-skills" ["python" "javascript"] "proj-skills" ["python" "javascript"]
        "workload" 60 "capacity" 100 "priority" 8 "proj-priority" 8}
       {"dev-skills" ["python" "statistics"] "proj-skills" ["python" "statistics"]
        "workload" 70 "capacity" 80 "priority" 9 "proj-priority" 9}
       {"dev-skills" ["javascript" "sql"] "proj-skills" ["sql" "python"]
        "workload" 50 "capacity" 90 "priority" 6 "proj-priority" 6}])

(setv optimal (optimize-assignment candidates))
{"optimal_assignment" optimal
 "fitness_score" (get optimal "fitness" 0.0)}
```

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface

class TestIntelligentPlanner:
    @pytest.fixture
    async def planner_components(self):
        """Get all surface components."""
        return {
            "python": PythonSurface(),
            "prolog": PrologSurface(),
            "hy": HySurface()
        }

    @pytest.mark.asyncio
    async def test_python_preprocessing(self, planner_components):
        """Test Python data preparation phase."""
        python = planner_components["python"]

        code = """
        projects = [{'name': 'A', 'priority': 8}, {'name': 'B', 'priority': 6}]
        total_priority = sum(p['priority'] for p in projects)
        {'projects': projects, 'total_priority': total_priority}
        """

        result = await python.execute(code, {})
        assert result["status"] == "ok"
        assert result["value"]["total_priority"] == 14

    def test_prolog_constraints(self, planner_components):
        """Test Prolog constraint validation."""
        prolog = planner_components["prolog"]
        if not prolog.available:
            pytest.skip("PySWIP not available")

        # Test basic constraint loading
        result = prolog.execute("project(web_app, [python, javascript], 8).")
        assert result["status"] == "ok"

    def test_hy_optimization(self, planner_components):
        """Test Hy fuzzy optimization."""
        hy = planner_components["hy"]
        if not hy.available:
            pytest.skip("Hy not available")

        code = "(+ (* 0.5 0.8) (* 0.3 0.9) (* 0.2 0.7))"
        result = hy.execute(code)
        assert result["status"] == "ok"
        assert abs(result["value"] - 0.79) < 0.01  # 0.5*0.8 + 0.3*0.9 + 0.2*0.7

    @pytest.mark.asyncio
    async def test_multi_surface_integration(self, planner_components):
        """Test coordination between all surfaces."""
        python = planner_components["python"]

        # Simulate multi-surface result synthesis
        context = {
            "python_data": {"score": 0.8},
            "prolog_data": [{"result": {"confidence": 0.9}}],
            "hy_data": {"optimization_score": 0.7}
        }

        synthesis_code = """
        final_score = (python_data['score'] * 0.4 +
                      prolog_data[0]['result']['confidence'] * 0.3 +
                      hy_data['optimization_score'] * 0.3)
        decision = "approved" if final_score > 0.7 else "needs_review"
        {"decision": decision, "score": final_score}
        """

        result = await python.execute(synthesis_code, context)
        assert result["status"] == "ok"
        assert result["value"]["decision"] == "approved"
        assert result["value"]["score"] > 0.7
```

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_planner_skill_integration():
    """Test the intelligent planner skill end-to-end."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create skill directory
        skills_dir = Path(tmpdir) / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "intelligent_planner"
        skill_dir.mkdir()

        # Create SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: Intelligent Task Planner
Domain: Artificial Intelligence
surfaces:
  - python
  - prolog
  - hy
---

## Purpose
Multi-surface intelligent planning

## Description
Intelligent planner using all three surfaces for testing
""")

        # Index skills
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir, registry_file)

        # Search for planner skill
        results = search_registry("planner", registry_file)
        assert len(results) >= 1

        skill_result = next((r for r in results if r["name"] == "Intelligent Task Planner"), None)
        assert skill_result is not None
        assert len(skill_result["surfaces"]) == 3
        assert "python" in skill_result["surfaces"]
        assert "prolog" in skill_result["surfaces"]
        assert "hy" in skill_result["surfaces"]
```

## Usage Patterns

### Resource Allocation Planning

```python
from intelligent_planner import IntelligentPlanner, PlanningTask

planner = IntelligentPlanner()

allocation_task = PlanningTask(
    name="Team Resource Allocation",
    python_code="""
# Gather project and team data
projects = [
    {"id": "web", "skills": ["python", "js"], "effort": 100, "deadline": "2024-06-01"},
    {"id": "ml", "skills": ["python", "stats"], "effort": 150, "deadline": "2024-07-01"},
    {"id": "db", "skills": ["sql", "python"], "effort": 80, "deadline": "2024-05-15"}
]

team = [
    {"id": "alice", "skills": ["python", "js"], "capacity": 120},
    {"id": "bob", "skills": ["python", "stats", "sql"], "capacity": 100},
    {"id": "charlie", "skills": ["js", "sql"], "capacity": 110}
]

{"projects": projects, "team": team, "total_effort": sum(p['effort'] for p in projects)}
""",
    prolog_facts=[
        "developer(alice, [python, javascript], 120).",
        "developer(bob, [python, statistics, sql], 100).",
        "developer(charlie, [javascript, sql], 110).",
        "project(web, [python, javascript], 100).",
        "project(ml, [python, statistics], 150).",
        "project(db, [sql, python], 80)."
    ],
    prolog_queries=[
        "findall(D-P, (developer(D, Skills, _), project(P, Req, _), subset(Req, Skills)), Matches)."
    ]
)

result = await planner.execute_task(allocation_task)
print(f"Planning decision: {result['final_decision']}")
```

### Smart Scheduling

```python
# Multi-constraint meeting scheduling
scheduling_task = PlanningTask(
    name="Meeting Scheduler",
    # ... implementation combining availability constraints (Prolog)
    # with preference optimization (Hy) and calendar integration (Python)
)
```

## Security Considerations

Multi-surface execution requires careful security consideration:

- **Surface Isolation**: Each surface runs in controlled environment
- **Data Sanitization**: Validate all inputs before cross-surface sharing
- **Resource Limits**: Prevent infinite loops and excessive resource usage
- **Audit Logging**: Track all cross-surface data flows

## Performance Characteristics

- **Python**: Fast numerical computing, I/O operations
- **Prolog**: Efficient logical inference, backtracking search
- **Hy**: Good for symbolic processing, functional algorithms
- **Combined**: Optimal for complex AI planning problems

## Dependencies

- **Em-Cubed**: Core framework
- **PySWIP**: Prolog integration (optional)
- **Hy**: Lisp functionality (optional)

## Future Enhancements

- **Distributed Planning**: Multi-agent coordination
- **Learning Integration**: ML-based optimization
- **Real-time Adaptation**: Dynamic replanning capabilities
- **Domain-Specific Languages**: Custom planning DSLs</content>
<parameter name="filePath">D:\GitHub\projects\em-cubed\skills\intelligent_planner\SKILL.md