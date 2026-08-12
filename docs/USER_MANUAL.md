# Em-Cubed (EM3) — User Manual
> **Polyglot AI Skill Engine & Neuro-Symbolic Ontological OS**

---

## 📋 Table of Contents
1. [Overview & System Architecture](#overview--system-architecture)
2. [Installation & Runtime Prerequisites](#installation--runtime-prerequisites)
3. [The 14 Polyglot Execution Surfaces](#the-14-polyglot-execution-surfaces)
4. [Zero-Copy Polyglot Shared Substrate (Apache Arrow)](#zero-copy-polyglot-shared-substrate-apache-arrow)
5. [Sandbox Security & AST Isolation Model](#sandbox-security--ast-isolation-model)
6. [CLI Command Reference (`em3`)](#cli-command-reference-em3)
7. [Skill Authoring, LLM Compiler & Package Manager](#skill-authoring-llm-compiler--package-manager)
8. [Neuro-Symbolic Ontology OS & Self-Healing Loops](#neuro-symbolic-ontology-os--self-healing-loops)
9. [Durable Workflow Execution & Budget Circuit Breakers](#durable-workflow-execution--budget-circuit-breakers)
10. [MCP Server Setup & Python API Developer Guide](#mcp-server-setup--python-api-developer-guide)
11. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)

---

## 🏛️ Overview & System Architecture

**Em-Cubed (EM3)** is a high-performance **Polyglot AI Skill Engine** and **Neuro-Symbolic OS**. It provides 148+ pre-built execution skills across 14 multi-paradigm surfaces, allowing AI agents to choose the exact runtime surface best suited to a computational task (e.g. Z3 for constraint satisfaction, PySWIP for logic unification, DuckDB for columnar analytics, Julia for automatic differentiation, PyTorch for GPU tensor acceleration).

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      AI Agent / MCP Client (IDE)                       │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ JSON-RPC (STDIO / HTTP / SSE)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   Em-Cubed Gateway & Policy Steering                   │
 ├───────────────────────────────────┬────────────────────────────────────┤
 │    Skill Registry & Hub (148+)    │    Durable Task DAG Scheduler      │
 ├───────────────────────────────────┼────────────────────────────────────┤
 │    LLM Skill Compiler & Verifier  │    Budget Circuit Breaker (Cost)   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Zero-Copy Shared Memory Substrate (Arrow)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      14 Polyglot Execution Surfaces                    │
 │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │
 │ │ Python AST  │ │ SWI-Prolog  │ │ Z3 SMT      │ │ WASM (wasmtime)    │ │
 │ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├────────────────────┤ │
 │ │ Datalog     │ │ QuickJS     │ │ Clingo (ASP)│ │ SQLite / Container │ │
 │ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├────────────────────┤ │
 │ │ DuckDB      │ │ Julia       │ │ PyTorch GPU │ │ Kanren / Janus     │ │
 │ └─────────────┘ └─────────────┘ └─────────────┘ └────────────────────┘ │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Installation & Runtime Prerequisites

### System Requirements
- **Python**: `>=3.10`
- **C/C++ Tools** (optional for native extensions): `gcc`, `clang`, or `cmake`.

### Optional Surface Extra Runtimes
To unlock full multi-surface capabilities:
- **Prolog**: Install SWI-Prolog (`swipl`) or Janus bridge
- **Z3 SMT**: `pip install z3-solver`
- **DuckDB**: `pip install duckdb`
- **Julia**: Install Julia runtime (`julia` executable on PATH) or `pip install juliacall`
- **PyTorch GPU**: `pip install torch`
- **Apache Arrow Substrate**: `pip install pyarrow`
- **Container Surface**: Docker (`pip install "em-cubed[docker]"`)

### Quick Installation
```bash
# Clone & install core package in editable mode
git clone https://github.com/SpectreDeath/Em-Cubed.git
cd Em-Cubed
pip install -e ".[dev]"

# Generate/update skill registry index
em3 index skills/ -o registry.json
```

---

## 🌐 The 14 Polyglot Execution Surfaces

Em-Cubed dynamically routes code execution to dedicated surface plugins:

| Surface | Backend / Engine | Best Used For |
|---|---|---|
| `python` | `asteval` + Isolated Process | Numerical routines, ML, general data processing |
| `prolog` | SWI-Prolog via PySWIP | First-order logic, Horn clause unification, graph queries |
| `z3` | Z3 SMT Solver | Constraint satisfaction, formal verification, theorem proving |
| `datalog` | `pyDatalog` thread engine | Deductive relational queries, transitive closure indexing |
| `hy` | Hy (Lisp-on-Python) | Functional metaprogramming, AST macro expansion |
| `sqlite` | SQLite In-Memory DB | Relational SQL queries, temporary tabular schemas |
| `duckdb` | DuckDB Engine | High-speed columnar OLAP SQL transformations & Parquet/Arrow queries |
| `julia` | Julia Runtime / `juliacall` | High-performance automatic differentiation & ODE/PDE differential equations |
| `tensor` | PyTorch GPU / CUDA | Hardware-accelerated tensor computations with VRAM cache management |
| `wasm` | `wasmtime` engine | Zero-trust sandboxed WebAssembly execution with fuel metering |
| `clingo` | Clingo (Potassco) | Answer Set Programming (ASP), combinatorial optimization |
| `kanren` | `microKanren` / `kanren` | Declarative relational logic & pattern matching |
| `quickjs` | `pyquickjs` sandbox | Safe JavaScript code evaluation |
| `janus` | SWI-Janus C-bindings | Bidirectional C-native Python <-> Prolog bridging |

---

## 🚀 Zero-Copy Polyglot Shared Substrate (Apache Arrow)

Em-Cubed includes an in-memory **Apache Arrow Shared Memory Substrate** (`ArrowSharedSubstrate`).

* **Zero-Copy Memory Exchange**: Transmit datasets across Python, DuckDB, WASM, and Prolog surfaces using Arrow IPC stream serialization (`pyarrow.ipc.RecordBatchStreamWriter`) without JSON string overhead.
* **Automatic Fallback**: Gracefully degrades to native Python dictionary structures if `pyarrow` is not installed.

```python
from em_cubed.surfaces import ArrowSharedSubstrate

substrate = ArrowSharedSubstrate()
substrate.register_table("dataset1", [{"id": 1, "value": 100.0}, {"id": 2, "value": 200.0}])

# Serialize to IPC byte stream for zero-copy surface passing
ipc_bytes = substrate.serialize_ipc("dataset1")
```

---

## 🛡️ Sandbox Security & AST Isolation Model

Em-Cubed enforces multi-layered defense to prevent untrusted code execution risks:

1. **AST Allowlisting**: Disallows dangerous Python dunder methods (`__subclasses__`, `__import__`), raw file system access, and system calls.
2. **Resource & Concurrency Limits**:
   - Wall-clock execution timeout (`EM_CUBED_TIMEOUT`, default 10s).
   - Maximum concurrency slots per surface plugin.
   - WASM fuel metering for step-count bounding.
   - Automatic GPU VRAM cache clearing post-execution for `tensor` surface.
3. **Containerized Execution**: EPhemeral Docker containers isolate untrusted external skills with read-only root filesystems and disabled network interfaces (`pip install "em-cubed[docker]"`).

---

## 📖 CLI Command Reference (`em3`)

### Skill Search & Indexing
```bash
# Search available skills by query
em3 search "optimization"

# Generate or update skill registry index
em3 index skills/ -o registry.json --incremental

# Display full metadata for a skill
em3 skill-info OPTIMIZATION/cma-es-optimizer
```

### Direct Code Execution
```bash
# Execute Python snippet
em3 run --surface python --code "result = [x**2 for x in range(10)]"

# Execute DuckDB SQL transformation
em3 run --surface duckdb --code "SELECT 42 AS answer, 'DuckDB' AS engine;"

# Execute PyTorch GPU tensor code
em3 run --surface tensor --code "a = torch.tensor([1.0, 2.0]); result = (a * 2.0).tolist()"
```

### LLM Skill Compilation & Package Management (Phase 2)
```bash
# Synthesize a new skill from natural language prompt specs
em3 generate-skill "Matrix multiplication and ODE solver" --domain OPTIMIZATION --surfaces python z3 duckdb

# Install a remote or local skill package
em3 install https://example.com/skills/custom_skill.md

# Generate or refresh em3.lock lockfile
em3 lock

# Verify cryptographic SHA-256 signature against em3.lock
em3 verify Custom/custom_skill.md
```

---

## ✍️ Skill Authoring, LLM Compiler & Package Manager

### 1. Skill Authoring Spec (`SKILL.md`)
Skills follow a standardized Markdown structure with YAML frontmatter:

```markdown
---
name: matrix-optimizer
domain: OPTIMIZATION
version: 1.0.0
purpose: "Perform matrix multiplication and numerical optimization"
description: "Provides multi-surface optimization algorithms"
surfaces:
  - python
  - duckdb
---

# Matrix Optimizer

## Python Surface (`python`)
```python
input_val = context.get("input_data", "")
result = {"status": "ok", "computed": input_val}
```
```

### 2. Formal SMT Precondition/Postcondition Verification
`SkillCompiler` integrates Z3 SMT solver verification to formally prove that preconditions logically guarantee postconditions ($Pre \implies Post$) before a skill is registered.

### 3. Lockfile Security (`em3.lock`)
`SkillHub` maintains an `em3.lock` lockfile recording exact SHA-256 hashes of all registered skills to prevent unauthorized tampering or supply-chain mutation.

---

## 🧠 Neuro-Symbolic Ontology OS & Self-Healing Loops

### Kit Fine Counterfactual Fault Localization
When a multi-step agent pipeline fails, `ExactTruthmakerClassifier.locate_counterfactual_fault()` evaluates exact truthmaking state ($s \Vdash A$) to pinpoint the minimal sub-state fragment $s$ that caused falsemaker status ($s \Vdash_f A$).

### Autonomous Self-Healing Skill Loop (`SelfHealingSkillLoop`)
Detects production execution errors or quality score degradation, synthesizes logic repair patches via `SkillCompiler`, validates syntax in a container sandbox, and auto-patches the target skill file.

---

## ⚙️ Durable Workflow Execution & Budget Circuit Breakers

### Durable Execution Checkpoint Recovery (`DurableExecutionManager`)
- Persists step checkpoints incrementally to SQLite (`.workflow_checkpoints.db`).
- Crashed or paused long-running DAG workflows resume instantly from the exact failed/paused node without re-executing completed dependencies.

### Budget Circuit Breakers (`BudgetCircuitBreaker`)
- Sets maximum USD cost budgets per agent session/project.
- Automatically opens circuit breakers (`CircuitState.OPEN`) when budget thresholds are met, redirecting execution to local/open-source fallback surfaces (e.g. switching from commercial LLMs to local Python/QuickJS surfaces).

```python
from em_cubed.telemetry.budget_circuit_breaker import BudgetCircuitBreaker

cb = BudgetCircuitBreaker(max_budget_dollars=5.0)
cb.record_cost(5.50)  # Budget exceeded!

status = cb.check_execution_allowed("llm")
print(status)
# Output: {'allowed': False, 'reason': 'Budget circuit breaker is OPEN ($5.50 / $5.00).', 'recommended_fallback': 'python'}
```

---

## 🔌 MCP Server Setup & Python API Developer Guide

### Launching MCP Server (Model Context Protocol)
```bash
em3-mcp
```

### Claude Desktop / Cursor Setup (`mcp_config.json`)
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

### Python API Example
```python
from em_cubed import DuckDBSurface, PythonSurface, SkillExecutor, SkillCompiler

# 1. Execute DuckDB analytical query
duck_surface = DuckDBSurface()
res = duck_surface.execute_sync("SELECT 'Em-Cubed' AS engine, 14 AS surfaces;")
print(res["value"])

# 2. Synthesize new skill dynamically
compiler = SkillCompiler()
compiled = compiler.compile_skill("Time series forecasting algorithm", domain="TIME_SERIES")
print(compiled["skill_id"])

# 3. Execute pre-built skill by ID
executor = SkillExecutor(registry_path="registry.json")
output = executor.execute_skill_sync(
    "OPTIMIZATION/cma-es-optimizer",
    input_data={"dimensions": 5, "max_iterations": 100}
)
print(output.result)
```

---

## 🔧 Troubleshooting & Diagnostics

| Problem | Cause | Solution |
|---|---|---|
| `SurfaceNotFoundError` | Surface plugin missing or not installed | Verify surface name in `em3 surfaces` or install optional package (`duckdb`, `juliacall`, `torch`) |
| `ExecutionTimeoutError` | Skill exceeded time quota | Pass `--timeout 30.0` or update `EM_CUBED_TIMEOUT` env var |
| `ASTViolationError` | Forbidden import or system call | Remove prohibited imports (`os`, `sys`, `subprocess`) from untrusted Python code |
| `IntegrityVerificationError` | Skill file modified without updating lockfile | Run `em3 lock` to refresh `em3.lock` or run `em3 verify <path>` to diagnose |
