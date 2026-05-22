---
name: MultiSurfaceLogic
Domain: Logic
Version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
---
## Purpose

Demonstrate multi-surface coordination by combining Python, Prolog, and Hy for complex logic problems.

## Description

This skill showcases how to orchestrate logic execution across multiple surfaces (Python, Prolog, Hy) to solve problems that benefit from each surface's strengths:
- Python for data processing and orchestration
- Prolog for declarative logic and constraint solving  
- Hy for functional programming and metaprogramming

## Examples

### Basic Coordination

```python
# Python orchestrator calling Prolog and Hy
def solve_logic_problem(facts, rules):
    # 1. Process facts in Python
    processed_facts = preprocess_facts(facts)
    
    # 2. Execute logic in Prolog
    prolog_results = prolog_surface.execute(generate_prolog_code(processed_facts, rules))
    
    # 3. Post-process with Hy
    final_results = hy_surface.execute(postprocess_hy_code(prolog_results))
    
    return final_results
```

### Constraint Solving Pipeline

```prolog
% Prolog constraint definition
valid_solution(X, Y, Z) :-
    X #> 0, Y #> 0, Z #> 0,
    X + Y #= Z,
    X * Y #< 100.
```

```hy
# Hy post-processing
(defn filter-solutions [solutions]
  (filter (fn [s] (> (:score s) 0.5)) solutions))
```

## Implementation

### Python Surface
Handles orchestration, data preprocessing, and interfacing with other surfaces.

### Prolog Surface  
Executes declarative logic rules and constraint satisfaction problems.

### Hy Surface
Provides functional programming capabilities for transforming and analyzing results.

## Security Considerations

- All surfaces execute in containerized environments by default
- Input validation is performed before cross-surface data transfer
- Resource limits are enforced per surface execution

## Dependencies

- Python 3.11+
- PySWIP (for Prolog surface)
- Hy language
- Em-Cubed framework

## Performance Characteristics

- Enables problem decomposition across paradigm boundaries
- May have coordination overhead but enables more expressive solutions
- Each surface can be optimized for its specific subtask