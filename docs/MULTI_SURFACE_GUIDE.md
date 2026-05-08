# Multi-Surface Orchestration Guide

This document explains how to create skills that truly leverage the Em-Cubed framework's multilogic architecture by orchestrating execution across multiple surfaces.

## Understanding Multi-Surface Orchestration

True multi-surface orchestration goes beyond simply having multiple implementations of the same logic in different languages. Instead, it involves:

1. **Dynamic Cross-Surface Communication**: One surface generating code or data for another surface to execute
2. **Leveraging Paradigm Strengths**: Using each surface for what it does best (e.g., Prolog for logical inference, Python for data processing)
3. **Context Sharing**: Passing data between surfaces through the shared execution context
4. **Workflow Orchestration**: Controlling the flow of execution across surfaces

## The Context["surfaces"] Injection Pattern

The key to multi-surface orchestration is the automatic injection of available surface plugins into the skill execution context:

```python
# In skill_executor.py, lines 135-140:
# Inject surface plugins for cross-surface interaction
context["surfaces"] = {}
for surface_name in ["python", "prolog", "hy", "z3", "datalog", "janus"]:
    surf_plugin = self.plugin_manager.get(surface_name)
    if surf_plugin and surf_plugin.available:
        context["surfaces"][surface_name] = surf_plugin
```

This makes all available surfaces accessible within skills via `context["surfaces"]["surface_name"]`.

## Orchestration Patterns

### Pattern 1: Python-as-Orchestrator, Prolog-as-Reasoner

Have Python handle data processing, control flow, and orchestration while delegating logical inference to Prolog:

```python
def solve_logical_problem(facts, rules, queries):
    # Process and validate input data in Python
    processed_facts = validate_and_format_facts(facts)
    
    # Generate Prolog code
    prolog_code = generate_prolog_code(processed_facts, rules)
    
    # Execute Prolog reasoning
    prolog_result = context["surfaces"]["prolog"].execute(prolog_code, {})
    
    if prolog_result["status"] != "ok":
        return handle_error(prolog_result)
    
    # Process results further in Python
    final_results = process_prolog_output(prolog_result["result"], queries)
    
    return final_results
```

### Pattern 2: Prolog-as-Fact-Base, Python-as-Processor

Use Prolog to maintain a knowledge base and Python for complex computations:

```python
def hybrid_approach(initial_data):
    # Load initial facts into Prolog
    prolog_facts = generate_initial_facts(initial_data)
    context["surfaces"]["prolog"].execute(prolog_facts, {})
    
    # Perform complex calculations in Python that would be difficult in Prolog
    python_results = perform_complex_calculations(initial_data)
    
    # Feed Python results back to Prolog as new facts
    new_facts = generate_facts_from_python_results(python_results)
    context["surfaces"]["prolog"].execute(new_facts, {})
    
    # Query the combined knowledge base
    query_result = context["surfaces"]["prolog"].execute(final_query, {})
    
    return process_results(query_result)
```

### Pattern 3: Pipeline Processing

Create execution pipelines where data flows through multiple surfaces:

```python
def pipeline_processing(input_data):
    # Stage 1: Initial processing in Python
    stage1_result = context["surfaces"]["python"].execute(stage1_code, {"input": input_data})
    
    # Stage 2: Logical inference in Prolog
    stage2_code = generate_prolog_from_python_output(stage1_result["value"])
    stage2_result = context["surfaces"]["prolog"].execute(stage2_code, {})
    
    # Stage 3: Final validation in Python
    stage3_code = generate_validation_code(stage2_result)
    stage3_result = context["surfaces"]["python"].execute(stage3_code, {})
    
    return stage3_result["value"]
```

## Best Practices for Multi-Surface Skills

1. **Clear Separation of Concerns**: Assign specific responsibilities to each surface based on its strengths
2. **Minimal Data Transfer**: Only pass essential data between surfaces to reduce overhead
3. **Error Handling**: Implement robust error handling for each surface interaction
4. **Timeout Awareness**: Remember that each surface call respects its own timeout settings
5. **Context Management**: Be mindful of what data is stored in the context between executions
6. **Surface Availability**: Always check if required surfaces are available before attempting to use them

## Example: Integrated Logic Solver

See `skills/General/integrated-logic-solver/SKILL.md` for a complete example that:
- Uses Python to process family relationship data
- Dynamically generates Prolog facts and rules
- Queries the Prolog surface for complex relationship inference
- Processes and formats the results in Python

## Debugging Multi-Surface Skills

When debugging orchestrated skills:
1. Test each surface interaction independently
2. Log the code/data being passed between surfaces
3. Check surface availability before execution
4. Verify the format of data being exchanged
5. Monitor execution times for each surface interaction

## Performance Considerations

While multi-surface orchestration provides powerful capabilities, consider:
- The overhead of context switching between surfaces
- Data serialization costs when passing complex objects
- Potential bottlenecks if one surface becomes the limiting factor
- Opportunities for caching or batching operations

By following these patterns and best practices, you can create skills that truly harness the power of Em-Cubed's multilogic architecture, solving problems that would be difficult or impossible with a single programming paradigm.