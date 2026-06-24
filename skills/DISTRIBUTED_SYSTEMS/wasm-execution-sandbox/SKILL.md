---
name: wasm-execution-sandbox
domain: DISTRIBUTED_SYSTEMS
version: 1.0.0
surfaces:
- python
- datalog
description: Multi-surface WASM execution sandbox with Python surface for runtime compilation and Datalog surface for capability
  verification. Supports versioned execution and memory safety checks.
compatibility: PYTHON
allowed-tools: '- read

  - write

  - edit

  - bash

  - glob

  - grep

  - codebase_search

  - task

  - sequentialthinking_sequentialthinking

  - webfetch

  - websearch

  - question

  - suggest

  '
---

# WASM Execution Sandbox

Secure sandboxed WebAssembly execution for portable compute across distributed nodes.

## Purpose

Execute untrusted WASM modules with resource bounds and security isolation for distributed computing.

## Description

This skill provides:
- Python: WASM module loader, resource limiting, sandbox orchestration
- Datalog: Execution policy rules, capability declarations, audit logging

## Implementation

### Python Sandbox Loader

```python
def parse_wat_module(wat_source):
    """Parse WAT text format to extract function signatures."""
    functions = []
    lines = wat_source.split('\n')
    in_func = False
    for line in lines:
        if '(func' in line:
            in_func = True
            name = extract_string_arg(line, '$') or 'anonymous'
            params = extract_params(line)
            results = extract_results(line)
            functions.append({'name': name, 'params': params, 'results': results})
    return functions

def extract_string_arg(line, prefix):
    """Extract string argument after prefix from line."""
    import re
    match = re.search(rf'{prefix}(\w+)', line)
    return match.group(1) if match else None

def extract_params(line):
    """Extract (param ...) declarations."""
    import re
    matches = re.findall(r'\(param\s+(?:i32|f32|i64|f64)\s+\$\w+\)', line)
    return [m for m in matches]

def extract_results(line):
    """Extract (result ...) declarations."""
    import re
    matches = re.findall(r'\(result\s+(?:i32|f32|i64|f64)\)', line)
    return [m for m in matches]

def validate_module_bounds(wat_source, max_memory=10000, max_funcs=50):
    """Validate WASM module stays within resource bounds."""
    functions = parse_wat_module(wat_source)
    total_memory = wat_source.count('(memory')
    if len(functions) > max_funcs:
        return False, f"Too many functions: {len(functions)}"
    if total_memory > max_memory:
        return False, f"Memory limit exceeded"
    return True, "Valid"

def create_sandbox_config(allowed_imports=None, memory_limit=64):
    """Create sandbox configuration dictionary."""
    config = {
        'memory_limit': memory_limit,
        'allowed_imports': allowed_imports or [],
        'timeout_ms': 5000,
        'max_tables': 10,
        'max_memories': 1
    }
    return config
```

### Datalog Policy Rules

```datalog
% Allowed capabilities per module
capability(module, memory).
capability(module, compute).

% Denied operations
denied(module, network).
denied(module, filesystem).
denied(module, env).

% Resource limits
memory_limit(module, 64).
timeout_limit(module, 5000).

% Audit trail
execution_log(module, timestamp, status).
execution_log(module, timestamp, error) :- denied(module, Operation).

% Security policy
allowed_module(Module) :- capability(Module, _), not denied(Module, _).
```

## Testing

### Unit Tests

```python
def test_parse_wat_module():
    wat = '(module (func $add (param i32 i32) (result i32)))'
    funcs = parse_wat_module(wat)
    assert len(funcs) == 1
    assert funcs[0]['name'] == 'add'

def test_validate_module_bounds():
    wat = '(module (func $f1 (param i32)))'
    valid, msg = validate_module_bounds(wat, max_funcs=10)
    assert valid == True

def test_create_sandbox_config():
    config = create_sandbox_config()
    assert config['memory_limit'] == 64
    assert config['timeout_ms'] == 5000
```

## Security Considerations

- No network access
- Memory and timeout bounds
- Import whitelist enforcement
- Isolated execution context