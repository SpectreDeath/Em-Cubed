# ADR 002: Safe Code Execution with asteval

## Status

Accepted

## Context

Python surface needs to execute user-provided code securely. Direct exec() is dangerous due to potential system access, file operations, and arbitrary code execution. Need a sandboxed execution environment.

## Decision

Use asteval library for safe Python code execution with:

1. Restricted symbol table (no builtins that allow system access)
2. Timeout protection via asyncio
3. Limited standard library access
4. Safe math and data operations only

## Consequences

### Positive
- Security: Prevents malicious code execution
- Performance: Fast execution for mathematical/scientific code
- Compatibility: Supports numpy, scipy, and other scientific libraries
- Simplicity: Drop-in replacement for basic Python execution

### Negative
- Limitations: Cannot use arbitrary Python features (import, file I/O, etc.)
- Dependency: Requires asteval package
- Learning curve: Users must understand asteval restrictions
- Maintenance: Need to track asteval security updates

## Alternatives Considered

1. Docker containers - Heavy resource usage, slower startup
2. PyPy sandbox - Deprecated, limited Python support
3. RestrictedPython - More complex, less scientific library support
4. No execution - Removes Python surface capability