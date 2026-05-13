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
origin: manual

## Purpose

Multi-surface planning orchestrated by Cangjie. Python generates candidate plans, Prolog validates constraints, and Hy scores plan quality; Cangjie selects optimal assignment.

## Architecture

**Archetype**: Competitive Search (parallel surface evaluation)

```cangjie
struct Task {
    id: String;
    name: String;
    required_skills: Array<String>;
    duration: Int64;
    priority: Int64;
}

struct Developer {
    id: String;
    skills: Array<String>;
    capacity: Int64;  // hours available
}

struct PlanningInput {
    tasks: Array<Task>;
    developers: Array<Developer>;
    weights: Map<String, Float64>;  // {"skill_match": 0.5, "capacity": 0.3, "priority": 0.2}
}

struct Assignment {
    task_id: String;
    dev_id: String;
    score: Float64;
}

struct PlanningOutput {
    assignments: Array<Assignment>;
    total_score: Float64;
    method: String;  // "python" | "prolog" | "hy" | "synthesized"
}
```

## Cangjie Orchestrator

```cangjie
func main(input: PlanningInput) -> PlanningOutput {
    // Step 1: Python — greedy skill-based allocation
    let py_code = """
def greedy_assign(tasks, developers):
    assignments = []
    for task in sorted(tasks, key=lambda t: t["priority"], reverse=True):
        # Find best dev by skill overlap
        best = None
        best_score = -1
        for dev in developers:
            overlap = len(set(task["required_skills"]) & set(dev["skills"]))
            score = overlap / max(1, len(task["required_skills"]))
            if score > best_score:
                best_score = score
                best = dev["id"]
        if best:
            assignments.append({"task_id": task["id"], "dev_id": best, "score": best_score})
    return assignments

assigns = greedy_assign(${input.tasks}, ${input.developers})
"""
    let py_assignments = perform EmCubed.call_surface("python", py_code);

    // Step 2: Prolog — hard constraint validation
    let prolog_code = """
% Constraints
can_assign(Dev, Task) :-
    developer(Dev, Skills, Capacity),
    project(Task, ReqSkills, Duration),
    subset(ReqSkills, Skills),
    Capacity >= Duration.

valid_assignment(Dev, Task) :-
    can_assign(Dev, Task).

% Check all assigned pairs
all_valid(Assignments) :-
    forall(member(dev-task(Dev, Task), Assignments),
           valid_assignment(Dev, Task)).
"""
    // We'd dynamically assert dev/project facts here
    _ = perform EmCubed.call_surface("prolog", prolog_code);

    // Step 3: Hy — fuzzy workload balance scoring
    let hy_code = """
(import numpy)

(defn workload-variance [assignments developers]
  (let [dev-workload (fn [dev]
                       (sum (lfor a assignments
                                  (if (= (:dev_id a) dev) (:duration a) 0))))
        loads (list-comp (dev-workload d) [d developers])
        avg (/ (sum loads) (len loads))
        var (/ (sum (lfor l loads (** (- l avg) 2))) (len loads))]
    var))

(defn balance-score [variance]
  ;; Lower variance => higher score (fuzzy inverted)
  (/ 1.0 (+ 1.0 variance)))

(let [v (workload-variance ${py_assignments} ${input.developers})
      score (balance-score v)]
  {"hy_score" score "variance" v})
"""
    let hy_results = perform EmCubed.call_surface("hy", hy_code);

    // Step 4: Synthesize — weighted multi-criteria selection
    // Python gives skill_match, Hy gives balance, Prolog gives feasibility (binary)
    let python_total = mean(py_assignments.map(|a| a["score"]));
    let hy_balance = hy_results["hy_score"]? 0.5;
    let final_score = python_total * (input.weights["skill_match"]? 0.5)
                    + hy_balance * (input.weights["capacity"]? 0.3)
                    + 1.0 * (input.weights["priority"]? 0.2);  // Prolog = 1 if feasible, else 0

    return PlanningOutput{
        assignments: py_assignments,
        total_score: final_score,
        method_used: "synthesized"
    };
}
```

## Implementation Mapping

| Surface | Lines | Purpose |
|---------|-------|---------|
| Python | ~20 | Greedy skill-matching allocation |
| Prolog | ~15 | Feasibility constraints (subset, capacity) |
| Hy | ~20 | Workload variance → fuzzy balance |
| Cangjie | ~45 | Synthesis + weighted scoring |

**Expected LOC reduction**: ~60% (558 → ~100)

## Testing

```python
surface = CangjieSurface()

input = {
    "tasks": [
        {"id": "t1", "name": "Web App", "required_skills": ["python", "js"], "duration": 100, "priority": 8},
        {"id": "t2", "name": "ML Model", "required_skills": ["python", "stats"], "duration": 150, "priority": 9}
    ],
    "developers": [
        {"id": "alice", "skills": ["python", "js"], "capacity": 120},
        {"id": "bob", "skills": ["python", "stats", "sql"], "capacity": 100}
    ],
    "weights": {"skill_match": 0.6, "capacity": 0.3, "priority": 0.1}
}

result = await surface.execute("", input)
assert len(result["value"]["assignments"]) >= 1
assert result["value"]["total_score"] > 0
```

## Dependencies

- numpy (dev stats)
- pyswip (Prolog)
- hy (fuzzy)
- em_cubed
