# ADR 001: Multi-Surface Skill Execution Architecture

## Status

Accepted

## Context

The system needs to support execution of skills across multiple programming languages and logic systems (Python, Prolog, Hy Lisp, Z3, etc.) to enable diverse problem-solving capabilities. Users should be able to write skills in their preferred language while maintaining a unified interface.

## Decision

Implement a plugin-based architecture with:

1. Abstract SurfacePlugin base class defining the execution interface
2. Separate surface implementations for each language/system
3. Unified skill metadata format with surface declarations
4. Runtime surface discovery and loading

## Consequences

### Positive
- Extensible: New surfaces can be added without modifying core code
- Language-agnostic: Skills can leverage the best tool for each problem
- Isolation: Surface failures don't affect other surfaces
- Unified API: Consistent execution interface across all surfaces

### Negative
- Complexity: Plugin system adds architectural overhead
- Dependency management: Each surface has its own dependencies
- Testing: Each surface needs separate testing
- Resource usage: Multiple interpreters loaded simultaneously

## Alternatives Considered

1. Single language (Python) - Too limiting for logic/AI tasks
2. Embedded interpreters - Performance and compatibility issues
3. External services - Network latency and reliability concerns