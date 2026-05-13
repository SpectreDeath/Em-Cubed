# Test Plan: Comparing Original Skills vs Cangjie-Optimized Versions

## Overview
This test plan outlines the methodology for comparing original Em-Cubed skills (Python-orchestrated) with their Cangjie-optimized counterparts. The goal is to validate that Cangjie versions:
1. Produce equivalent or better results (correctness)
2. Show improved performance (execution time, throughput)
3. Maintain or improve code clarity and maintainability
4. Preserve the same interface and invocation pattern

## Test Scope
Skills to be tested (19 migrated skills):
- OPTIMIZATION: pathfinding-with-constraints, optimization-landscape-analyzer, constraint-satisfaction-solver
- DECISION_MAKING: multi-surface-decision-tree, multi-criteria-weight-calculator
- RECOMMENDER_SYSTEMS: recommendation-engine
- RESOURCE_MANAGEMENT: resource-allocation-planner
- TIME_SERIES: time-series-forecaster
- STATISTICS: uncertainty-quantifier
- SIMULATION: system-dynamics-modeler
- MODEL_VALIDATION: model-validation-suite
- ML_OPERATIONS: anomaly-detection-system
- DATA_PROCESSING: data-pipeline-orchestrator
- AUTOMATION: workflow-synthesiser
- GENERAL: intelligent-planner
- ENSEMBLE: ensemble-method-manager
- DISTRIBUTED_SYSTEMS: multi-agent-coordinator
- KNOWLEDGE_GRAPH: knowledge-graph-builder
- NLP: sentiment-intelligence-engine

## Test Environment
- **Framework**: Em-Cubed with Python, Prolog, and Hy surfaces available
- **Hardware**: Standardized test machine (to be specified)
- **Software**: 
  - Python 3.9+ with required packages (numpy, scikit-learn, spacy, transformers where applicable)
  - Prolog implementation (SWI-Prolog or equivalent)
  - Hy Lisp implementation
- **Execution**: Each test run in isolated process to avoid interference

## Test Methodology

### 1. Correctness Testing
For each skill:
- Identify canonical test cases from original skill documentation
- Run both original and Cangjie versions on identical inputs
- Compare outputs for semantic equivalence
- For stochastic skills: run multiple iterations and compare statistical properties

### 2. Performance Testing
For each skill:
- Measure wall-clock execution time for standard workload
- Measure CPU time utilization
- Measure memory footprint
- For batch-processing skills: measure throughput (items/second)
- Run each test N times (N≥5) and report mean ± stddev

### 3. Code Quality Metrics
For each skill version:
- Count lines of documentation (SKILL.md vs SKILL_CANGJIE.md)
- Count lines of actual surface code (Python/Prolog/Hy) invoked
- Measure orchestration complexity (number of surface calls, depth of nesting)
- Assess readability via structured review (subjective but guided)

### 4. Interface Compatibility
Verify that:
- Skill invocation pattern remains identical
- Input/output data structures are compatible
- Error handling behavior is preserved
- Configuration parameters have same meaning and format

## Test Categories

### Unit Tests
Test individual skill components in isolation where possible.

### Integration Tests
Test skills in realistic workflows with multiple surface interactions.

### Regression Tests
Ensure Cangjie version doesn't break existing functionality.

### Benchmark Tests
Measure performance under standardized loads.

## Success Criteria
A Cangjie version is considered successful if:
1. **Correctness**: Output matches original within tolerance (exact for deterministic, statistical equivalence for stochastic)
2. **Performance**: ≥1.2× speedup OR ≥30% reduction in orchestration overhead
3. **Compatibility**: Same invocation interface, no breaking changes
4. **Quality**: No significant degradation in code clarity or maintainability

## Test Organization

```
skills/
├── DOMAIN/
│   ├── skill-name/
│   │   ├── SKILL.md                 # Original
│   │   ├── SKILL_CANGJIE.md         # Cangjie-optimized
│   │   ├── test_original.py         # Tests for original version
│   │   ├── test_cangjie.py          # Tests for Cangjie version
│   │   └── test_comparison.py       # Joint comparison tests
```

## Sample Test Structure

Each skill test suite should include:

```python
# test_comparison.py
import time
import statistics
from em_cubed.skills.DOMAIN.skill_name import original_skill, cangjie_skill

def test_correctness():
    """Verify both versions produce equivalent results"""
    test_cases = load_test_cases()  # From skill documentation
    
    original_results = []
    cangjie_results = []
    
    for case in test_cases:
        # Run original version
        start = time.perf_counter()
        orig_result = original_skill.execute(case.input)
        orig_time = time.perf_counter() - start
        
        # Run Cangjie version
        start = time.perf_counter()
        cangjie_result = cangjie_skill.execute(case.input)
        cangjie_time = time.perf_counter() - start
        
        # Compare results
        assert results_equivalent(orig_result, cangjie_result), \
            f"Results differ for case {case.id}"
        
        # Collect timing
        original_timings.append(orig_time)
        cangjie_timings.append(cangjie_time)
    
    # Report timing comparison
    print(f"Original mean time: {statistics.mean(original_timings):.4f}s")
    print(f"Cangjie mean time: {statistics.mean(cangjie_timings):.4f}s")
    print(f"Speedup: {statistics.mean(original_timings)/statistics.mean(cangjie_timings):.2f}×")

def test_performance_under_load():
    """Test with larger/more complex inputs"""
    # Implementation depends on skill type
    pass

def test_interface_compatibility():
    """Verify same inputs produce same output types"""
    pass
```

## Reporting
After testing all skills, generate:
1. **Individual skill reports**: Detailed comparison for each skill
2. **Summary matrix**: Cross-skill performance and correctness summary
3. **Trend analysis**: Patterns in what types of skills benefit most
4. **Recommendations**: Guidance for future Cangjie adoption

## Next Steps
1. Implement test harness for each skill
2. Run baseline tests on original versions
3. Implement and test Cangjie versions
4. Generate comparison reports
5. Identify skills that didn't meet success criteria for investigation