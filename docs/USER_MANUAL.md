# Em-Cubed v0.8.0 — User Manual
> **Polyglot AI Skill Engine & Neuro-Symbolic Ontological OS**

---

## 📋 Table of Contents
1. [Overview & System Architecture](#overview--system-architecture)
2. [Installation & Runtime Prerequisites](#installation--runtime-prerequisites)
3. [The 11 Polyglot Execution Surfaces](#the-11-polyglot-execution-surfaces)
4. [Sandbox Security & AST Isolation Model](#sandbox-security--ast-isolation-model)
5. [CLI Command Reference (`em3`)](#cli-command-reference-em3)
6. [MCP Server Setup (Claude Desktop / Cursor)](#mcp-server-setup-claude-desktop--cursor)
7. [Skill Authoring Specification](#skill-authoring-specification)
8. [Python API Developer Guide](#python-api-developer-guide)
9. [Neuro-Symbolic Ontology OS Overview](#neuro-symbolic-ontology-os-overview)
10. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)

---

## 🏛️ Overview & System Architecture

**Em-Cubed** is a high-performance **Polyglot AI Skill Engine** and **Neuro-Symbolic OS**. It provides 148+ pre-built execution skills across 11 multi-paradigm surfaces, allowing AI agents to choose the exact runtime surface best suited to a computational task (e.g. Z3 for constraint satisfaction, PySWIP for logic unification, Wasmtime for zero-trust binaries).

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      AI Agent / MCP Client (IDE)                       │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ JSON-RPC (STDIO / HTTP)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                        Em-Cubed Gateway & MCP                          │
 ├───────────────────────────────────┬────────────────────────────────────┤
 │      Skill Registry (148+)        │     DAG Task Scheduler & Pipeline  │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Surface Selection & Isolation
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      11 Polyglot Execution Surfaces                    │
 │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │
 │ │ Python AST  │ │ SWI-Prolog  │ │ Z3 SMT      │ │ WASM (wasmtime)    │ │
 │ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├────────────────────┤ │
 │ │ Datalog     │ │ QuickJS     │ │ Clingo (ASP)│ │ SQLite / Container │ │
 │ └─────────────┘ └─────────────┘ └─────────────┘ └────────────────────┘ │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Installation & Runtime Prerequisites

### System Requirements
- **Python**: `>=3.10`
- **C/C++ Tools** (optional for native extensions): `gcc` or `clang`, `cmake`.

### Optional Polyglot Runtimes
To unlock full multi-surface capabilities:
- **Prolog**: Install SWI-Prolog (`swipl`)
- **Z3**: Included via `z3-solver` Python package
- **WASM**: Uses `wasmtime` Python bindings
- **Clingo**: Included via `clingo` Python package
- **Container Surface**: Requires Docker (`pip install "em-cubed[docker]"`)

### Quick Installation
```bash
# Clone & install core package in editable mode
git clone https://github.com/SpectreDeath/Em-Cubed.git
cd Em-Cubed
pip install -e ".[dev]"

# Generate/update the skill registry index
em3 index skills/ -o registry.json
```

---

## 🌐 The 11 Polyglot Execution Surfaces

Em-Cubed dynamically routes code execution to dedicated surface plugins:

| Surface | Backend / Engine | Best Used For |
|---|---|---|
| `python` | `asteval` + Isolated Process | Numerical routines, ML, matrix operations |
| `prolog` | SWI-Prolog via PySWIP | First-order logic, Horn clause unification, graph queries |
| `z3` | Z3 SMT Solver | Constraint satisfaction, program synthesis, formal verification |
| `datalog` | `pyDatalog` thread engine | Deductive database queries, transitive closure indexing |
| `hy` | Hy (Lisp-on-Python) | Functional metaprogramming, AST macro expansion |
| `sqlite` | SQLite In-Memory DB | SQL queries, tabular data manipulation, temporary schemas |
| `wasm` | `wasmtime` engine | Zero-trust binary execution with byte/fuel limits |
| `clingo` | Clingo (Potassco) | Answer Set Programming (ASP), combinatorial solving |
| `kanren` | `microKanren` / `kanren` | Declarative relational logic, pattern matching |
| `quickjs` | `pyquickjs` sandbox | Safe JavaScript code evaluation |
| `janus` | SWI-Janus C-bindings | Ultra-fast bidirectional Python <-> Prolog bridging |

---

## 🛡️ Sandbox Security & AST Isolation Model

Em-Cubed enforces multi-layered defense to prevent malicious code execution:

1. **AST Allowlisting**: Disallows dangerous Python dunder methods (`__subclasses__`, `__import__`), file system I/O, and OS syscalls.
2. **Resource Limits**:
   - Wall-clock timeout (default 10s).
   - Maximum memory allocations per process.
   - WASM fuel metering for step-count bounding.
3. **Process Isolation**: Every untrusted snippet runs inside a spawned worker process or ephemeral container, destroying volatile state post-execution.

---

## 📖 CLI Command Reference (`em3`)

### Skill Discovery & Registry Indexing
```bash
# Search available skills by keyword
em3 search "optimization"

# Generate or update skill registry index
em3 index skills/ -o registry.json

# Validate all SKILL.md definitions against schema
em3 validate skills/
```

### Direct Code Execution
```bash
# Execute Python snippet
em3 run --surface python --code "result = [x**2 for x in range(10)]"

# Execute Z3 SMT constraint problem
em3 run --surface z3 --code "x = Int('x'); s = Solver(); s.add(x > 5, x < 10); s.check()"

# Execute SWI-Prolog query
em3 run --surface prolog --code "parent(tom, bob)." --query "parent(X, bob)"
```

### Benchmarking & Performance
```bash
# Run benchmark suite across execution surfaces
em3 benchmark --skills OPTIMIZATION/cma-es-optimizer
```

---

## 🔌 MCP Server Setup (Claude Desktop / Cursor)

Em-Cubed includes a native Model Context Protocol (MCP) server interface (`em3-mcp`).

### Launching the Server
```bash
em3-mcp
```

### Claude Desktop / Cursor Configuration (`mcp_config.json`)
```json
{
  "mcpServers": {
    "em-cubed": {
      "command": "uvx",
      "args": ["em-cubed", "em3-mcp"]
    }
  }
}
```

### Exposed MCP Tools
- `execute_surface`: Run arbitrary code snippet on specified surface.
- `search_skills`: Search the 148+ skill catalog by domain/keyword.
- `run_skill`: Execute a registered skill by path with input payload.
- `verify_constraint`: Verify a Z3 formal specification.

---

## ✍️ Skill Authoring Specification

Skills are structured directories containing a `SKILL.md` file and optional execution code:

```markdown
---
name: OPTIMIZATION/cma-es-optimizer
surface: python
description: Covariance Matrix Adaptation Evolution Strategy for high-dimensional optimization
version: 1.0.0
inputs:
  dimensions: int
  max_iterations: int
---

### Implementation Code
```python
def execute(inputs):
    # Skill logic here
    return {"status": "success", "result": ...}
```
```

---

## 🐍 Python API Developer Guide

```python
from em_cubed.surfaces.python_surface import PythonSurface
from em_cubed.skills.executor import SkillExecutor

# 1. Execute Surface Directly
surface = PythonSurface(timeout=5.0)
res = surface.execute_sync("result = 42 * 2")
print(res["value"])  # Output: 84

# 2. Execute Pre-Built Skill
executor = SkillExecutor(registry_path="registry.json")
output = executor.execute_skill_sync(
    "OPTIMIZATION/cma-es-optimizer",
    input_data={"dimensions": 5, "max_iterations": 100}
)
print(output.result)
```

---

## 🧠 Neuro-Symbolic Ontology OS Overview

Em-Cubed integrates formal ontologies to ground AI agent reasoning:
- **Topos Subobject Classifiers ($\Omega$)**: Categorical logic for truth-value assignments across heterogeneous domain models.
- **Kit Fine Exact Truthmakers**: Evaluates state truthmaking ($s \Vdash A$) to verify whether model responses satisfy precise formal conditions.
- **BFO & OntoClean Integration**: Maps generated knowledge graphs onto Basic Formal Ontology standard structures.

---

## 🔧 Troubleshooting & Diagnostics

| Problem | Cause | Solution |
|---|---|---|
| `SurfaceNotFoundError` | Surface dependency missing | Install runtime (e.g. `swipl` for prolog, `pip install z3-solver`) |
| `ExecutionTimeoutError` | Skill exceeded time quota | Pass `--timeout 30.0` or update surface config |
| `ASTViolationError` | Forbidden import or system call | Avoid using `os`, `sys`, or reflection in untrusted code |
