# Em-Cubed: Multi-Surface Skill Framework

[![Tests](https://img.shields.io/badge/tests-100%20passing-brightgreen)](https://github.com/SpectreDeath/Em-Cubed)
[![Coverage](https://img.shields.io/badge/coverage-26%25-brightgreen)](https://github.com/SpectreDeath/Em-Cubed)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT)

Em-Cubed is a secure, multi-surface skill framework enabling execution across Python, Prolog, Hy Lisp, Z3 SMT solving, Datalog logic, and Janus Python-Prolog bridge surfaces with unified indexing and search capabilities. It allows developers to create composable skills that leverage different programming paradigms for optimal problem-solving.

## ✨ Key Features

- **🔒 Secure Execution**: Safe code execution across multiple surfaces
- **🔍 Intelligent Search**: Multi-surface scoring and skill discovery
- **🌐 REST API**: Full HTTP API for skill execution and management
- **📊 Structured Logging**: Comprehensive logging with context
- **🧪 Comprehensive Testing**: 219 tests with ~26% coverage
- **📚 Multi-Paradigm**: Python, Prolog, Hy, Z3, Datalog, and Janus surfaces

## 🎉 What's New in v0.5.0

- **⚡ Async Timeouts**: Configurable execution timeouts across all surfaces (default 30s)
- **🔄 Incremental Indexing**: Only re-index changed skill files (10x+ performance boost)
- **🔌 Plugin System**: Extensible surface architecture with 3 discovery mechanisms
- **🎯 SurfacePlugin Interface**: Abstract base class for custom surface implementations
- **📊 PluginManager**: Manages surface plugins with automatic discovery
- **⏱️ Timeout Protection**: Environment variable and CLI support for execution limits
- **📈 Performance**: Lazy plugin loading and optimized resource management

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/SpectreDeath/Em-Cubed.git
cd Em-Cubed

# Install with development dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import em_cubed; print('Em-Cubed installed successfully!')"
```

### Basic Usage

```python
from em_cubed import search_registry, PythonSurface

# Search for skills
results = search_registry("calculator", "registry.json")
print(f"Found {len(results)} skills")

# Execute Python code safely
surface = PythonSurface()
result = await surface.execute("2 + 3", {})
print(f"Result: {result['value']}")  # Output: 5
```

### API Server

```bash
# Start the API server
uvicorn api.main:app --reload

# Server available at: http://localhost:8000
# Interactive API docs: http://localhost:8000/docs
```

## 📖 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Surface Reference](#surface-reference)
- [API Documentation](#api-documentation)
- [Skill Development](#skill-development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## 🏗️ Architecture Overview

```
em-cubed/
├── src/em_cubed/           # Core package
│   ├── indexer.py         # SKILL.md parsing & registry generation
│   ├── search.py          # Multi-surface scoring search
│   └── surfaces/          # Execution surfaces
│       ├── python_surface.py  # Safe Python via asteval
│       ├── prolog_surface.py  # PySWIP Prolog integration
│       ├── hy_surface.py      # Hy Lisp execution
│       ├── z3_surface.py      # Z3 SMT solving
│       ├── datalog_surface.py # Datalog logic programming
│       └── janus_surface.py   # Python-Prolog bridge (experimental)
├── api/main.py            # FastAPI REST API
├── examples/              # Multi-surface skill examples
├── tests/                 # Comprehensive test suite (219 tests)
└── docs/                  # Technical specifications
```

### Core Components

- **Indexer**: Parses SKILL.md files and builds searchable registries
- **Search Engine**: Multi-surface scoring with context-aware ranking
- **Surfaces**: Secure execution environments for different languages
- **API**: RESTful interface for skill discovery and execution

## 📦 Installation

### Requirements

- Python 3.11+
- Optional: SWI-Prolog (for Prolog surface)
- Optional: Hy (for Hy Lisp surface)

### Development Setup

```bash
# Install all dependencies including dev tools
pip install -e ".[dev]"

# Run tests to verify installation
pytest

# Check code quality
ruff check src/ tests/
mypy src/
```

## 💻 Usage

### Python API

```python
from em_cubed import search_registry, get_skill_metadata, reindex
from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface

# Index skills from directory
reindex("skills/", "registry.json")

# Search for skills
results = search_registry("optimization", "registry.json")
for skill in results:
    print(f"{skill['name']} ({skill['domain']})")
    print(f"  Surfaces: {', '.join(skill['surfaces'])}")

# Execute code on surfaces
python_surface = PythonSurface()
result = await python_surface.execute("2 + 2")
print(f"Result: {result['value']}")  # 4

# Prolog logical reasoning
prolog = PrologSurface()
if prolog.available:
    await prolog.execute("parent(john, mary).")
    result = await prolog.execute("parent(X, Y)")
    print(f"Parents: {result['result']}")
```

### Command Line Interface

Em-Cubed provides a full-featured CLI for skill management:

```bash
# Index/reindex skills
em3 index skills/ -o registry.json
em3 index skills/ --incremental  # Faster, only changed files

# Search for skills
em3 search "machine learning"
em3 search "optimization" --max-results 5

# Execute code on a surface
em3 run --surface python --code "2 + 2"
em3 run --surface prolog --code "parent(X, Y)"

# Validate skills (structure, quality)
em3 validate --skills-dir skills/ --json-output

# Run quality pipeline (validation + tests + benchmarks)
em3 quality --benchmark

# Run tests for specific skill
em3 test NLP/natural-language-generator --generate

# Get skill recommendations
em3 recommend "need to optimize a function"

# Search for skills
results = search_registry("optimization", "registry.json")
for skill in results:
    print(f"{skill['name']}: {skill['purpose']}")

# Execute code on different surfaces
python_surface = PythonSurface()
result = await python_surface.execute("sum([1, 2, 3])", {})
print(f"Python result: {result['value']}")

# Prolog execution (requires PySWIP)
prolog_surface = PrologSurface()
if prolog_surface.available:
    result = await prolog_surface.execute("X is 2 + 3.")
    print(f"Prolog result: {result}")
```

### Command Line (em3)

```bash
# Use the em3 CLI (installed via pip)
em3 --help

# Index skills directory
em3 index ./skills --output registry.json

# Search for skills
em3 search "calculator" --max-results 10

# Start API server
em3 serve --host 127.0.0.1 --port 8000

# Execute code directly
em3 run --surface python --code "2 + 2"
```

## 🔧 Surface Reference

### Python Surface

**Capabilities**: Safe Python code execution with context injection.

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

# Simple expression
result = await surface.execute("2 ** 3", {})
print(result['value'])  # 8

# With context variables
result = await surface.execute("x + y * z", {"x": 1, "y": 2, "z": 3})
print(result['value'])  # 7

# Function execution
result = await surface.execute("len(data)", {"data": [1, 2, 3, 4]})
print(result['value'])  # 4
```

**Security**: Uses asteval for safe evaluation, no access to dangerous builtins. Prolog queries have a 10-second timeout and are limited to 1000 results to prevent resource exhaustion.

### Prolog Surface

**Capabilities**: Logical constraint solving and inference with persistent interpreter (enhanced in v0.3.0).

**New Features in v0.3.0**:
- **Persistent Interpreter**: Facts and rules persist across execute() calls
- **Automatic Mode Detection**: Trailing `.` for assertions vs queries
- **Security Enhancements**: Context value escaping to prevent Prolog injection attacks

```python
from em_cubed.surfaces import PrologSurface

surface = PrologSurface()

# Define facts and query (requires PySWIP + SWI-Prolog)
if surface.available:
    # Define parent relationships (assertions with trailing .)
    surface.execute("parent(john, mary).")
    surface.execute("parent(mary, ann).")

    # Query relationships (queries without trailing .)
    result = surface.execute("parent(X, Y)")
    print(f"Relationships: {result}")

    # Facts persist - add more relationships
    surface.execute("parent(ann, peter).")

    # Query again with accumulated knowledge
    result = surface.execute("ancestor(X, Z)")
    print(f"Ancestry: {result}")
```

**Requirements**: PySWIP library and SWI-Prolog installation.

### Hy Surface

**Capabilities**: Lisp-style programming with Python integration.

```python
from em_cubed.surfaces import HySurface

surface = HySurface()

# Hy Lisp code execution (requires hy library)
if surface.available:
    result = surface.execute("(+ 1 2 3)")
    print(f"Hy result: {result['value']}")  # 6

    # Function definition and call
    result = surface.execute("(defn square [x] (* x x)) (square 5)")
    print(result['value'])  # 25
```

**Requirements**: Hy library installation.

### Z3 Surface

**Capabilities**: SMT (Satisfiability Modulo Theories) solving for formal verification, constraint satisfaction, and symbolic reasoning.

```python
from em_cubed.surfaces import Z3Surface

surface = Z3Surface()
if surface.available:
    # Solve logical constraints
    result = await surface.execute("x + y == 5 && x > 0", {"x": 2, "y": 3})
    print(result['value'])  # {'status': 'sat', 'model': {...}}
```

**Requirements**: z3-solver package. Used for formal verification, optimization, and constraint solving.

### Datalog Surface

**Capabilities**: Logic programming with stratified negation, ideal for graph queries, incremental reasoning, and recursive queries.

```python
from em_cubed.surfaces import DatalogSurface

surface = DatalogSurface()
if surface.available:
    # Define facts and rules
    await surface.execute("parent(john, mary).")
    await surface.execute("ancestor(X, Y) :- parent(X, Y).")
    
    # Query
    result = await surface.execute("ancestor(X, Y)")
    print(result['value'])  # List of bindings
```

**Requirements**: pyDatalog library. Supports stratified negation and efficient bottom-up evaluation.

### Janus Surface

**Capabilities**: Python-Prolog bidirectional integration via the Janus bridge (experimental, optional).

```python
from em_cubed.surfaces import JanusSurface

surface = JanusSurface()
if surface.available:
    # Call Prolog from Python seamlessly
    result = await surface.execute("...")
```

**Requirements**: janus_swi package. This surface provides tight integration between Python and SWI-Prolog, allowing embedding of Prolog calls within Python code. May be unstable; consider using PySWIP directly for production.

## 🎯 Skills Quality Framework

Em-Cubed includes a comprehensive quality assurance system for skills:

### Features

- **🔍 Automated Validation**: Every skill is validated for structure, code quality, and completeness
- **📊 Quality Metrics**: Track execution success rates, performance, and usage patterns
- **🧪 Test Generation**: Automatic test file generation for all skills
- **🔗 Skill Composition**: Compose multiple skills together in pipelines
- **📈 Benchmarking**: Performance benchmarking across surfaces
- **💡 Recommendations**: Intelligent skill recommendation based on task requirements

### CLI Commands

```bash
# Index skills
em3 index skills/ -o registry.json

# Validate all skills
em3 validate --skills-dir skills/

# Run full quality pipeline
em3 quality --benchmark

# Run tests for a skill
em3 test NLP/natural-language-generator

# Get skill recommendations
em3 recommend "generate text from prompt"

# Compose skills
em3 compose --source NLP/text-preprocessor --target NLP/sentiment-analyzer
```

### Quality Standards

Skills must meet minimum thresholds:
- At least 1 surface implementation (Python/Prolog/Hy)
- Purpose ≥10 characters, Description ≥20 characters
- Valid code blocks for each declared surface
- Test coverage ≥80%
- Success rate ≥70%

### Programmatic Usage

```python
from em_cubed.skills import (
    SkillRegistry,
    SkillValidator,
    SkillComposer,
    SkillRecommender,
    SkillBenchmark,
)

# Load registry
registry = SkillRegistry(Path("skills"), Path("registry.json"))

# Validate a skill
validator = SkillValidator()
result = validator.validate_skill_file(skill_path, metadata)

# Compose skills
composer = SkillComposer(plugin_manager, registry)
plan = composer.create_pipeline([...])
result = await composer.compose(plan, input_data)

# Get recommendations
recommender = SkillRecommender(registry)
suggestions = recommender.recommend_for_task("optimize this function")
```

## 🌐 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "ok",
  "surfaces": {
    "python": true,
    "prolog": true,
    "hy": false
  }
}
```

#### List Surfaces
```http
GET /surfaces
```

Response:
```json
{
  "surfaces": [
    {
      "name": "python",
      "available": true,
      "description": "Safe Python execution with asteval"
    }
  ]
}
```

#### Search Skills
```http
POST /search
Content-Type: application/json

{
  "query": "optimization",
  "max_results": 10
}
```

**Search Skills (GET - new in v0.3.0)**
```http
GET /search?q=calculator&top=10
```

**Example with cURL:**
```bash
curl "http://localhost:8000/search?q=calculator&top=5"
```

**Response:**
```json
{
  "results": [
    {
      "name": "Calculator",
      "domain": "Mathematics",
      "purpose": "Perform basic arithmetic operations",
      "description": "Simple calculator for addition, subtraction, multiplication, division",
      "path": "skills/General/python_calculator/SKILL.md",
      "surfaces": ["python"],
      "logic_tags": [],
      "heuristic_tags": ["add", "subtract", "multiply", "divide"],
      "tags": ["add", "subtract", "multiply", "divide"],
      "score": 0.95
    }
  ]
}
```

#### Execute Code
```http
POST /execute
Content-Type: application/json

{
  "surface": "python",
  "code": "sum([1, 2, 3])",
  "context": {}
}
```

### Interactive Documentation

When running the API server, visit `http://localhost:8000/docs` for interactive OpenAPI documentation with live examples.

## 🛠️ Skill Development

### SKILL.md Format

Skills are defined in Markdown files with YAML frontmatter:

```markdown
---
name: My Skill
Domain: Mathematics
Version: 1.0.0
surfaces:
  - python
---

## Purpose
Brief description of what the skill does.

## Description
Detailed explanation and usage examples.

## Implementation

### Python
```python
def my_function(x):
    return x * 2
```

### Prolog
```prolog
double(X, Result) :- Result is X * 2.
```
```

### Skill Creation Guide

1. **Create skill directory**: `mkdir skills/my_skill`
2. **Write SKILL.md**: Define metadata and implementations
3. **Test locally**: Use `python -m em_cubed.indexer` to validate
4. **Add examples**: Include usage examples in the SKILL.md

### Best Practices

- Use specific, searchable names and descriptions
- Include comprehensive examples for each surface
- Test skills across different contexts
- Document any external dependencies

## 🧪 Testing
Em-Cubed includes a comprehensive test suite with 219 tests covering:

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=em_cubed --cov-report=html

# Specific test categories
pytest tests/test_api.py        # API endpoint tests
pytest tests/test_integration.py # Full workflow tests
pytest tests/test_surfaces.py   # Surface execution tests

# Code quality checks
ruff check src/ tests/          # Linting
mypy src/                       # Type checking
```

### Test Structure

- **Unit Tests**: Individual function/component testing
- **Integration Tests**: End-to-end workflow validation
- **API Tests**: HTTP endpoint testing with FastAPI TestClient
- **Async Tests**: Concurrent execution testing

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run the test suite: `pytest`
5. Check code quality: `ruff check src/ tests/ && mypy src/`
6. Commit with conventional format: `git commit -m "feat: add amazing feature"`
7. Push and create a Pull Request

### Code Standards

- **Linting**: Ruff (automatic formatting and import sorting)
- **Type Hints**: Full MyPy compliance
- **Testing**: 80%+ coverage requirement
- **Documentation**: All public APIs documented

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [asteval](https://github.com/newville/asteval) for safe Python evaluation
- [PySWIP](https://github.com/yuce/pyswip) for Prolog integration
- [Hy](https://github.com/hylang/hy) for Lisp in Python
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework

---

**Em-Cubed**: Where multiple programming paradigms unite for smarter solutions.