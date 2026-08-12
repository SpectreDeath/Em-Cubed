# Em-Cubed: Polyglot AI Skill Engine & Neuro-Symbolic OS

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/SpectreDeath/Em-Cubed)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Native-purple)](mcp/README.md)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT)

**Em-Cubed** is a high-performance **Polyglot AI Skill Engine** and **Neuro-Symbolic Ontological OS**. It enables AI agents, LLMs, and developers to run 148+ reusable skills across 14 execution surfaces (Python, Prolog, Z3, Datalog, Hy, SQLite, QuickJS, WASM, Clingo, Kanren, Janus, DuckDB, Julia, PyTorch GPU) with zero-copy PyArrow shared memory, AST sandboxing, lockfile verification, and built-in MCP integration.

---

## ⚡ 30-Second Quick Start

Try Em-Cubed instantly with `uv` / `uvx`:

```bash
# Search 148+ skills for optimization algorithms
uvx em-cubed em3 search "optimization"

# Execute a skill directly from the command line
uvx em-cubed em3 run --surface python --code "result = 2 + 3"

# Synthesize a new skill from natural language prompt specs
uvx em-cubed em3 generate-skill "Matrix multiplication and ODE solver" --domain OPTIMIZATION

# Launch the Model Context Protocol (MCP) server for Claude Desktop / Cursor
uvx em-cubed em3-mcp
```

### Installation

```bash
# Clone the repository
git clone https://github.com/SpectreDeath/Em-Cubed.git
cd Em-Cubed

# Install core package with dev dependencies
pip install -e ".[dev]"

# Build/verify skill index
em3 index skills/ -o registry.json
```

---

## 🚀 Core Features

### 🧩 148+ Pre-Built Polyglot Skills & LLM Compiler
- **Optimization**: Dialectic Search, Chaos Optimization, Fractal-Based Algorithm, Central Force, Spiral Dynamics, CMA-ES, Differential Evolution.
- **Machine Learning & Analytics**: K-Means Clustering, Logistic Regression, Random Forest, Naive Bayes, Decision Trees, ARMA/ARIMA Time Series.
- **Distributed Systems & Loops**: DAG Task Scheduler, Durable Execution Engine, Self-Healing Skill Loop, Budget Circuit Breaker.
- **LLM Skill Compiler & Hub**: `em3 generate-skill` prompt compilation with Z3 formal SMT verification, `em3 install`, and `em3.lock` lockfile signatures.

### 🌐 14 Polyglot Execution Surfaces
Run logic in the optimal language or solver for the task:
| Surface | Primary Use Case | Runtime Security |
|---------|------------------|------------------|
| `python` | General ML, data science, numerical routines | `asteval` AST isolation + process pool |
| `prolog` | Unification, Horn clause logic, relation queries | PySWIP SWI-Prolog sandbox |
| `z3` | SMT constraint solving, formal verification | Z3 Solver Engine |
| `datalog` | Deductive relational queries, fact indexing | `pyDatalog` thread isolation + FIFO cache |
| `hy` | Lisp metaprogramming and macro execution | AST cond-rewriter |
| `sqlite` | SQL relational querying & database ops | In-memory session isolation |
| `duckdb` | High-speed columnar OLAP SQL transformations | In-memory DuckDB engine |
| `julia` | Differential equations & automatic differentiation | Julia runtime / `juliacall` |
| `tensor` | GPU/CUDA hardware acceleration | PyTorch VRAM memory isolation |
| `wasm` | Sandboxed WebAssembly binary execution | `wasmtime` fuel metering + `/dev/null` WASI |
| `clingo` | Answer Set Programming (ASP) | Clingo solver |
| `kanren` | Relational logic programming (microKanren) | Symbol-allowlisted namespace |
| `quickjs` | Safe JavaScript execution | `pyquickjs` sandbox |
| `janus` | High-performance Python-Prolog bridge | SWI-Janus C-bindings |
| `container` | Isolated Docker container execution | Docker container sandbox (requires `pip install "em-cubed[docker]"`) |

### 🔌 MCP Native (Claude Desktop & Cursor)
Em-Cubed exposes tools over standard JSON-RPC STDIO/SSE for instant integration into AI agent IDEs. See [docs/USER_MANUAL.md](docs/USER_MANUAL.md) for full configuration setup.

### 🧠 Formal Neuro-Symbolic Ontology OS
Grounds agent execution in Topos $\Omega$ subobject classifiers, Kit Fine exact truthmakers ($s \Vdash A$), counterfactual fault localization, BFO/OntoClean elicitation pipelines, and SHACL shapes. See [docs/USER_MANUAL.md](docs/USER_MANUAL.md) for complete user manual.


## 📖 Basic Python API Usage

```python
from em_cubed import PythonSurface, SkillExecutor, search_registry

# 1. Search skill index
results = search_registry("optimization", registry_path="registry.json")
print(f"Found {len(results)} matching skills")

# 2. Execute Python code with timeout protection & slot control
surface = PythonSurface(timeout=10.0)
res = surface.execute_sync("result = sum(i * i for i in range(100))")
print(f"Status: {res['status']}, Value: {res['value']}")

# 3. Run a registered skill by ID
executor = SkillExecutor()
result = executor.execute_skill_sync("OPTIMIZATION/cma-es-optimizer", input_data={"dimensions": 5})
print(f"Skill Output: {result.output}")
```

---

## 📁 Repository Structure

```
em-cubed/
├── src/em_cubed/         # Core Python package
│   ├── surfaces/         # 11 Polyglot Execution Surface plugins
│   ├── skills/           # Skill Registry, Executor, Validator, Benchmarks
│   ├── workflow/         # Distributed DAG Task Scheduler & Pipelining
│   ├── gateway/          # MCP Server & Policy Steering
│   └── ontology/         # Topos, Truthmaker, Concept Induction, ZKP
├── skills/               # 148+ SKILL.md definition files & tests
├── lsp/                  # Language Server Protocol (pygls) extension
├── mcp/                  # MCP server installation docs
├── docs/                 # Formal Ontology OS documentation & specs
└── tests/                # Automated pytest suite (1,100+ tests)
```

---

## 📄 License & Citation

Licensed under the [MIT License](LICENSE).
