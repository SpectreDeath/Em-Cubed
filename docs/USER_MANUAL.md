# Em-Cubed (EM3) — User Manual
> **Polyglot AI Skill Engine & Neuro-Symbolic Ontological OS**

---

## 📋 Table of Contents
1. [Overview & System Architecture](#overview--system-architecture)
2. [Installation & Runtime Prerequisites](#installation--runtime-prerequisites)
3. [The 15 Polyglot Execution Surfaces](#the-15-polyglot-execution-surfaces)
4. [Zero-Copy Polyglot Shared Substrate (Apache Arrow & Polars)](#zero-copy-polyglot-shared-substrate-apache-arrow--polars)
5. [Sandbox Security, AST Isolation & Landlock Model](#sandbox-security-ast-isolation--landlock-model)
6. [CLI Command Reference (`em3`)](#cli-command-reference-em3)
7. [Skill Auto-Chaining, LLM Compiler & Package Manager](#skill-auto-chaining-llm-compiler--package-manager)
8. [Neuro-Symbolic Ontology OS, Merkle ZK Proofs & Self-Healing Loops](#neuro-symbolic-ontology-os-merkle-zk-proofs--self-healing-loops)
9. [Durable Workflows, Distributed Worker Mesh & Budget Breakers](#durable-workflows-distributed-worker-mesh--budget-breakers)
10. [MCP Server Setup & Python API Developer Guide](#mcp-server-setup--python-api-developer-guide)
11. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)

---

## 🏛️ Overview & System Architecture

**Em-Cubed (EM3)** is a high-performance **Polyglot AI Skill Engine** and **Neuro-Symbolic OS**. It provides 148+ pre-built execution skills across 15 multi-paradigm surfaces, allowing AI agents to choose the exact runtime surface best suited to a computational task (e.g. Z3 for constraint satisfaction, PySWIP for logic unification, DuckDB / Polars for columnar analytics, Julia for automatic differentiation, PyTorch for GPU tensor acceleration).

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
 │    Auto-Chaining Engine & Compiler│    Budget Circuit Breaker (Cost)   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Zero-Copy Shared Memory Substrate (Arrow)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      15 Polyglot Execution Surfaces                    │
 │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────────────┐ │
 │ │ Python AST  │ │ SWI-Prolog  │ │ Z3 SMT      │ │ WASM (wasmtime)    │ │
 │ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├────────────────────┤ │
 │ │ Datalog     │ │ QuickJS     │ │ Clingo (ASP)│ │ SQLite / Container │ │
 │ ├─────────────┤ ├─────────────┤ ├─────────────┤ ├────────────────────┤ │
 │ │ DuckDB      │ │ Polars      │ │ Julia       │ │ PyTorch GPU        │ │
 │ ├─────────────┤ └─────────────┘ └─────────────┘ └────────────────────┘ │
 │ │ Kanren/Janus│                                                        │
 │ └─────────────┘                                                        │
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

## 🌐 The 15 Polyglot Execution Surfaces

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
| `polars` | Polars Engine | Sub-millisecond vectorized DataFrame transformations in memory |
| `julia` | Julia Runtime / `juliacall` | High-performance automatic differentiation & ODE/PDE differential equations |
| `tensor` | PyTorch GPU / CUDA | Hardware-accelerated tensor computations with VRAM cache management |
| `wasm` | `wasmtime` engine | Zero-trust sandboxed WebAssembly execution with fuel metering |
| `clingo` | Clingo (Potassco) | Answer Set Programming (ASP), combinatorial optimization |
| `kanren` | `microKanren` / `kanren` | Declarative relational logic & pattern matching |
| `quickjs` | `pyquickjs` sandbox | Safe JavaScript code evaluation |
| `janus` | SWI-Janus C-bindings | Bidirectional C-native Python <-> Prolog bridging |
| `rust` | `ctypes` / `cffi` | Native compiled Rust dynamic library (.so / .dll / .dylib) execution |
| `container` | Docker Sandbox | Isolated container execution auto-fallback when native runtimes are missing |



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

## 🛡️ Sandbox Security, AST Isolation & Landlock Model

Em-Cubed enforces multi-layered defense to prevent untrusted code execution risks:

1. **AST Allowlisting**: Disallows dangerous Python dunder methods (`__subclasses__`, `__import__`), raw file system access, and system calls.
2. **Process-Level Landlock Sandboxing**: `LandlockSandbox` applies Linux Kernel Landlock & Seccomp process isolation to restrict filesystem access to allowed directories (`/tmp`, `/usr`, `/lib`) without requiring container runtimes.
3. **Resource & Concurrency Limits**:
   - Wall-clock execution timeout (`EM_CUBED_TIMEOUT`, default 10s).
   - Maximum concurrency slots per surface plugin.
   - WASM fuel metering for step-count bounding.
   - Automatic GPU VRAM cache clearing post-execution for `tensor` surface.
4. **Containerized Execution**: Ephemeral Docker containers isolate untrusted external skills with read-only root filesystems and disabled network interfaces (`pip install "em-cubed[docker]"`).


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

### Auto-Chaining & Direct Code Execution
```bash
# Auto-synthesize a multi-surface skill execution pipeline from a goal specification
em3 auto-chain "optimization algorithm and data analysis" --inputs '{"data": "csv"}'

# Execute Python snippet
em3 run --surface python --code "result = [x**2 for x in range(10)]"

# Execute Polars DataFrame transformation
em3 run --surface polars --code "import polars as pl; result = pl.DataFrame({'a': [1, 2]}).select(pl.col('a').sum())"

# Execute DuckDB SQL transformation
em3 run --surface duckdb --code "SELECT 42 AS answer, 'DuckDB' AS engine;"
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

## ✍️ Skill Auto-Chaining, LLM Compiler & Package Manager

### 1. Dynamic Skill Auto-Chaining (`AutoChainer`)
The `AutoChainer` engine uses schema compatibility and semantic graph search over the `SkillRegistry` to auto-synthesize multi-step polyglot workflow pipelines connecting input specifications to target goals:

```python
from em_cubed.skills.auto_chain import AutoChainer

chainer = AutoChainer(registry_path="registry.json")
result = chainer.find_chain(
    input_schema={"dataset": "csv", "features": "list"},
    goal_description="optimization algorithm"
)
print(f"Pipeline Length: {result['pipeline_length']} steps")
```

### 2. Skill Authoring Spec (`SKILL.md`)
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

## 🧠 Neuro-Symbolic Ontology OS, Merkle ZK Proofs & Self-Healing Loops

### Zero-Knowledge Merkle Inclusion Proofs (`ZKPAuditor`)
`ZeroKnowledgeOntologyAttestor` and `ZKPAuditor` generate and verify non-interactive zero-knowledge Merkle inclusion proofs over sensitive state fragments without disclosing raw ontology triples:

```python
from em_cubed.ontology.zk_attestation import ZeroKnowledgeOntologyAttestor, ZKPAuditor

proof = ZeroKnowledgeOntologyAttestor.generate_merkle_proof(state_triples, target_index=0)
is_valid = ZKPAuditor.verify_merkle_proof(proof["leaf"], proof["path"], proof["root"])
print("Merkle ZK Proof Verified:", is_valid)
```

### Kit Fine Counterfactual Fault Localization
When a multi-step agent pipeline fails, `ExactTruthmakerClassifier.locate_counterfactual_fault()` evaluates exact truthmaking state ($s \Vdash A$) to pinpoint the minimal sub-state fragment $s$ that caused falsemaker status ($s \Vdash_f A$).

### Autonomous Self-Healing Skill Loop (`SelfHealingSkillLoop`)
Detects production execution errors or quality score degradation, synthesizes logic repair patches via `SkillCompiler`, validates syntax in a container sandbox, and auto-patches the target skill file.

---

### Declarative Dynamic Workflow DAGs (`WorkflowDagParser`)
Declarative YAML/JSON DAG specifications support standard skill execution nodes as well as dynamic control flow nodes:
* `IfConditionNode`: Branch execution based on evaluation of prior node outputs.
* `LoopUntilNode`: Repeatedly execute child task until condition is satisfied.
* `SwitchNode`: Multi-way dynamic branching.
* `MapReduceNode`: Parallel batch evaluation across list inputs.

Example YAML Specification (`workflow.yaml`):
```yaml
workflow_id: dynamic_analytics_pipeline
tasks:
  - task_id: fetch_data
    skill_id: DATA_PROCESSING/fetch-dataset
    input_data: { source: "db" }

  - task_id: evaluate_quality
    type: if
    condition: "context.get('data_quality') > 0.8"
    then_task: train_model
    else_task: clean_dataset
    dependencies: [fetch_data]

  - task_id: train_model
    skill_id: MACHINE_LEARNING/logistic-regression
    dependencies: [evaluate_quality]
```

### Real-Time SSE Telemetry & Opt-In API Key Auth
The FastAPI server (`em3 serve`) exposes real-time Server-Sent Events (SSE) and opt-in API Key security:
* `GET /telemetry/stream`: Real-time SSE telemetry event stream.
* `X-API-Key`: Opt-in authentication enabled via `export EM_CUBED_API_KEY=your_secret_key` (omitted by default for frictionless local development).

### Distributed Polyglot Worker Process (`PolyglotWorker`)

`PolyglotWorker` provides an autonomous worker process that polls distributed task queues and executes skill steps across assigned polyglot surfaces:

```bash
# Launch a polyglot worker process listening for python, prolog, and polars tasks
python -m em_cubed.workflow.worker --surfaces python prolog polars duckdb
```

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
from em_cubed import DuckDBSurface, PolarsSurface, PythonSurface, SkillExecutor
from em_cubed.skills.auto_chain import AutoChainer

# 1. Execute Polars sub-millisecond DataFrame transformation
polars_surface = PolarsSurface()
res = polars_surface.execute_sync("import polars as pl; result = pl.DataFrame({'x': [10, 20]}).select(pl.col('x').sum())")
print("Polars Output:", res["value"])

# 2. Auto-synthesize multi-surface skill chain
chainer = AutoChainer()
chain = chainer.find_chain(input_schema={"dataset": "csv"}, goal_description="optimization algorithm")
print("Synthesized Chain Steps:", chain["pipeline_length"])

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
