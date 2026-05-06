---
Domain: COGNITIVE_SKILLS
Version: 1.0.0
Complexity: Medium
Type: Process
Category: Thinking Skills
Estimated Execution Time: 3-10 minutes
name: multi-surface-problem-solver
Source: community
---
origin: manual
triggers:
  - agent
  - ai
  - development
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-04-28T10:00:00Z"
updated_at: "2026-04-28T10:00:00Z"

## Purpose

Demonstrate multi-surface problem solving using Python orchestration, Prolog constraints, and Hy heuristics.

## Description

This skill showcases the integration of three programming surfaces to solve problems:
- Python for main logic and orchestration
- Prolog for logical constraints and verification
- Hy for heuristic decision making and fuzzy logic

The skill solves optimization problems by combining logical constraints with heuristic search.

## Examples

### Resource Allocation Problem

```
Input: Allocate 100 units across 3 projects with constraints
Output: Optimal allocation satisfying all constraints
```

## Implementation

### Python Entry Point

```python
def solve_allocation_problem(total_units=100, projects=3):
    """Solve resource allocation using multi-surface approach"""

    # Access injected surface plugins
    prolog_surface = context["surfaces"]["prolog"]
    hy_surface = context["surfaces"]["hy"]

    # Initialize Prolog constraints using injected surface
    prolog_result = prolog_surface.execute("""
max_allocation(30).
min_allocation(10).
""")
    if prolog_result["status"] != "ok":
        return {"error": "Failed to initialize Prolog constraints"}

    # Use Hy for heuristic scoring via injected surface
    hy_code = """
(defn score-allocation [alloc]
  "Score allocation based on balance heuristic"
  (let [avg (/ (sum alloc) (len alloc))
        variance (sum (list (** (- x avg) 2) (for [x alloc])))]
    (/ 1 (+ 1 variance))))  ; Lower variance = higher score
"""

    # Execute Hy code to define the function
    hy_result = hy_surface.execute(hy_code)
    if hy_result["status"] != "ok":
        return {"error": "Failed to initialize Hy heuristic"}

    # Generate and evaluate allocations
    best_allocation = None
    best_score = 0

    # Try different allocations (simplified brute force)
    for a in range(10, 31):
        for b in range(10, min(31, 101-a)):
            c = 100 - a - b
            if 10 <= c <= 30:
                allocation = [a, b, c]

                # Check Prolog constraints using injected surface
                constraint_ok = True
                for units in allocation:
                    query_result = prolog_surface.execute(f"max_allocation(M), min_allocation(N), {units} =< M, {units} >= N")
                    if query_result["status"] != "ok" or not query_result.get("result", []):
                        constraint_ok = False
                        break

                if constraint_ok:
                    # Score with Hy heuristic using injected surface
                    score_code = f"""
(defn score-allocation [alloc]
  "Score allocation based on balance heuristic"
  (let [avg (/ (sum alloc) (len alloc))
        variance (sum (list (** (- x avg) 2) (for [x alloc])))]
    (/ 1 (+ 1 variance))))

(score-allocation {[a, b, c]})
"""
                    score_result = hy_surface.execute(score_code)
                    if score_result["status"] == "ok":
                        score = score_result["value"]
                        if score > best_score:
                            best_score = score
                            best_allocation = allocation

    return {
        "allocation": best_allocation,
        "score": best_score,
        "constraints_satisfied": True
    }

# Example usage
result = solve_allocation_problem()
print(f"Optimal allocation: {result['allocation']}")
print(f"Balance score: {result['score']:.3f}")
```

### Prolog Constraints

```prolog
% Maximum allocation constraint
max_allocation(30).

% Minimum allocation constraint  
min_allocation(10).

% Verify allocation meets constraints
valid_allocation(A, B, C) :-
    max_allocation(Max),
    min_allocation(Min),
    A =< Max, A >= Min,
    B =< Max, B >= Min, 
    C =< Max, C >= Min,
    Total is A + B + C,
    Total =:= 100.
```

### Hy Heuristics

```hy
(defn score-allocation [alloc]
  "Score allocation based on balance heuristic"
  (let [avg (/ (sum alloc) (len alloc))
        variance (sum (list (** (- x avg) 2) (for [x alloc)))]
    (/ 1 (+ 1 variance))))

(defn fuzzy-balance [alloc]
  "Fuzzy logic assessment of balance"
  (let [ratios (list (/ x (sum alloc)) (for [x alloc]))]
    (if (> (apply max ratios) 0.5) 
        "unbalanced"
        "balanced")))
```

## Testing

Test the multi-surface integration:

```python
# Test all three surfaces
result = solve_allocation_problem(100, 3)
assert result["constraints_satisfied"] == True
assert len(result["allocation"]) == 3
assert sum(result["allocation"]) == 100

# Verify Prolog constraints work through injected surface
prolog_result = context["surfaces"]["prolog"].execute("max_allocation(30)")
assert prolog_result["status"] == "ok"

# Verify Hy functions work through injected surface
hy_result = context["surfaces"]["hy"].execute("(defn test-fn [] 42)")
assert hy_result["status"] == "ok"
hy_result2 = context["surfaces"]["hy"].execute("(test-fn)")
assert hy_result2["value"] == 42
```
