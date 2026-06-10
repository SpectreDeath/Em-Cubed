# Comprehensive Testing Strategy for Em-Cubed Skills

## Overview
This document outlines a comprehensive testing strategy for validating all skills in the Em-Cubed framework, ensuring correctness, performance, and reliability across all execution surfaces.

## Test Categories

### 1. Unit Tests (per skill)
Each skill should have unit tests covering:
- Metadata validation (name, domain, version, surfaces)
- Surface availability verification
- Core algorithm correctness
- Edge case handling
- Error conditions

**Example Structure:**
```python
def test_metadata_valid():
    """Test skill metadata is valid."""
    metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
    assert metadata_dict is not None
    assert metadata_dict["name"] == "skill-name"
    assert metadata_dict["domain"] == "DOMAIN"
    assert len(metadata_dict["surfaces"]) >= 1

def test_surfaces_implemented():
    """Test at least one required surface is available."""
    metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
    available_surfaces = []
    for surface in metadata_dict.get("surfaces", []):
        plugin = plugin_manager.get(surface)
        if plugin and plugin.available:
            available_surfaces.append(surface)
    assert len(available_surfaces) >= 1, f"No available surfaces found for {metadata_dict['name']}"

# Skill-specific unit tests would go here
```

### 2. Integration Tests
Tests for skill composition and interaction:
- Sequential composition
- Parallel composition  
- Conditional composition
- Cross-domain skill chaining
- Data passing between skills

### 3. Performance Tests
- Execution time validation (ensure <30s timeout)
- Memory usage profiling
- Scalability tests with larger datasets
- Timeout triggering validation

### 4. Surface-Specific Tests
Tests targeting each execution surface:
- Python: Algorithmic correctness, numerical stability
- Prolog: Logical consistency, constraint satisfaction
- SQL: Query correctness, data persistence
- Datalog: Rule evaluation, recursive queries
- Z3: Constraint solving, satisfiability checking
- Hy: Functional programming correctness
- QuickJS: JavaScript execution, performance
- Kanren: Relational logic, miniKanren patterns
- Clingo: ASP solving, stable model generation

### 5. Error Handling Tests
- Invalid input handling
- Missing dependency scenarios
- Surface unavailable fallbacks
- Malformed data handling
- Resource exhaustion scenarios

### 6. Security Tests
- Sandbox escape attempts
- Resource limit enforcement
- File system access restrictions
- Network access restrictions

## Test Organization

### Per-Skill Test Files
Each skill should have a corresponding test file:
```
tests/skills/test_{domain}_{skill-name}.py
```

### Shared Test Utilities
- Conftest.py for shared fixtures
- Test helper functions in `tests/skills/test_utils.py`
- Mock data generators for common test scenarios

## Specific Test Recommendations by Domain

### ANALYTICS Domain
- Bayesian Evidence Updater: Test posterior convergence, MECE validation
- Statistical Test Advisor: Test routing logic for all combinations, fallback triggers
- Time Series Preprocessor: Test datetime alignment, outlier detection, imputation
- Autoregressive Parameter Estimator: Test ACF/PACF, stationarity tests, ARIMA selection
- Forecasting Monitor: Test concept drift detection, error metrics, retraining triggers

### DISTRIBUTED_SYSTEMS Domain
- DAG Task Scheduler: Test topological sort, critical path, Z3 verification
- WASM Execution Sandbox: Test secure loading, resource bounds, policy enforcement
- Durable Execution Engine: Test checkpoint/recovery, persistence, fault tolerance
- Observability Dashboard: Test metrics collection, alert thresholds, visualization

### OPTIMIZATION Domain
- All optimizers: Test convergence, solution quality, parameter sensitivity
- Constraint solvers: Test feasibility, optimality, constraint satisfaction
- Metaheuristics: Test exploration/exploitation balance, stagnation handling

### STATISTICS Domain
- Statistical tests: Test type I/II errors, power, validity
- Uncertainty quantification: Test propagation, convergence, calibration
- Bootstrap analyzer: Test confidence intervals, bias correction, accuracy

### MACHINE_LEARNING Domain
- Decision trees: Test splitting criteria, overfitting prevention, pruning
- SVM: Test margin maximization, kernel tricks, support vectors
- Random Forest: Test ensemble diversity, feature importance, OOB error
- Logistic regression: Test sigmoid calibration, regularization, convergence
- Naive Bayes: Test independence assumption, smoothing, log probabilities

### EPIDEMIOLOGY Domain
- Transmission networks: Test R0 calculation, herd immunity, intervention effects
- Stochastic models: Test probability distributions, stochastic trajectories, extinction

## Performance Benchmarks

### Async Timeout Validation
- Create skills with known long-running computations
- Verify 30-second timeout triggers appropriately
- Test with UCI Census Income dataset (large-scale)
- Test with UCR Time Series Classification Archive (iterative loads)

### Surface Performance Comparison
- Benchmark Python vs Prolog vs Hy vs QuickJS for equivalent logic
- Measure Kanren/Clingo execution performance vs Prolog
- Validate Z3 constraint solving performance vs brute-force search

## Data-Driven Testing

### Recommended Test Datasets
1. **UCI Machine Learning Repository** - Adult/Census Income dataset
   - Stress test async timeouts with Random Forest/DAG scheduler
   - Test feature scaling, normalization skills

2. **UCR Time Series Classification Archive**  
   - Benchmark Kanren/Clingo logic surfaces with clean numeric datasets
   - Test time series forecasting, anomaly detection skills

3. **Web Data Commons** (JSON-LD/RDFa from Common Crawl)
   - Test SQLite surface with relational data
   - Test Datalog surface with graph traversal, recursive queries

4. **Yelp Open Dataset**
   - Test SQL surface persistence with business/review/user relations
   - Test recommendation engine skills

5. **GEO Gene Expression Omnibus**
   - Test EPIDEMIOLOGY skills with real biological data
   - Test Z3 surface with genomic constraint satisfaction

6. **StatLib Datasets Archive**
   - Test Kanren/Clingo surfaces with structured logic data
   - Test statistical skills with known distributions

## Test Execution Protocol

### Local Development
```bash
# Run all skill tests
python -m pytest tests/skills/ -v

# Run specific domain tests
python -m pytest tests/skills/test_ANALYTICS_*.py -v

# Run integration tests
python -m pytest tests/test_skills_integration.py -v
```

### CI/CD Pipeline
1. Unit test execution (skills/)
2. Integration test execution (test_skills_integration.py)
3. Performance benchmarking (timeout/memory validation)
4. Security scanning (sandbox escape attempts)
5. Coverage reporting (>80% target)

### Validation Gates
- All skills must pass metadata and surface availability tests
- At least 70% of execution tests must pass per skill
- No skill may exceed 30-second execution time
- Memory usage must remain under 512MB
- All surfaces used by a skill must be available and functional

## Continuous Improvement

### Test Maintenance
- Update tests when skill interfaces change
- Add regression tests for fixed bugs
- Expand test coverage for edge cases
- Benchmark against baseline performance

### Test Enhancement
- Add property-based testing (Hypothesis) where applicable
- Implement mutation testing for critical skills
- Add fuzzing for input validation
- Create chaos engineering tests for distributed skills

## Success Metrics
- Test pass rate: ≥95% for all skills
- Test coverage: ≥80% lines covered per skill
- Execution time: <30s for 99% of test cases
- Memory usage: <512MB for all tests
- Security: Zero sandbox escape vulnerabilities