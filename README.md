# Em-Cubed: Multi-Surface Skill Framework

[![Tests](https://img.shields.io/badge/tests-54%20passing-brightgreen)](https://github.com/SpectreDeath/Em-Cubed)
[![Coverage](https://img.shields.io/badge/coverage-76%25+-brightgreen)](https://github.com/SpectreDeath/Em-Cubed)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://opensource.org/licenses/MIT)

Em-Cubed is a secure, multi-surface skill framework enabling execution across Python, Prolog, and Hy Lisp surfaces with unified indexing and search capabilities. It allows developers to create composable skills that leverage different programming paradigms for optimal problem-solving.

## ✨ Key Features

- **🔒 Secure Execution**: Safe code execution across multiple surfaces
- **🔍 Intelligent Search**: Multi-surface scoring and skill discovery
- **🌐 REST API**: Full HTTP API for skill execution and management
- **📊 Structured Logging**: Comprehensive logging with context
- **🧪 Comprehensive Testing**: 54 tests with 76%+ coverage
- **📚 Multi-Paradigm**: Python, Prolog logic, and Hy Lisp support

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
│       └── janus_surface.py   # Python-Prolog bridge
├── api/main.py            # FastAPI REST API
├── examples/              # Multi-surface skill examples
├── tests/                 # Comprehensive test suite (54 tests)
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
    print(f"{skill['name']}: {skill['purpose']}")

# Execute code on different surfaces
python_surface = PythonSurface()
result = await python_surface.execute("sum([1, 2, 3])", {})
print(f"Python result: {result['value']}")

# Prolog execution (requires PySWIP)
prolog_surface = PrologSurface()
if prolog_surface.available:
    result = prolog_surface.execute("X is 2 + 3.")
    print(f"Prolog result: {result}")
```

### Command Line

```bash
# Index skills
python -m em_cubed.indexer skills/ registry.json

# Search registry
python -m em_cubed.search registry.json "calculator"

# Start API server
uvicorn api.main:app --host 0.0.0.0 --port 8000
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

**Capabilities**: Logical constraint solving and inference.

```python
from em_cubed.surfaces import PrologSurface

surface = PrologSurface()

# Define facts and query (requires PySWIP + SWI-Prolog)
if surface.available:
    # Define parent relationships
    surface.execute("parent(john, mary).")
    surface.execute("parent(mary, ann).")

    # Query relationships
    result = surface.execute("parent(X, Y).")
    print(f"Relationships: {result}")
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

### Janus Surface (Future)

**Capabilities**: Seamless Python-Prolog interoperation.

*Currently a placeholder for future Python-Prolog bridge implementation.*

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

Em-Cubed includes a comprehensive test suite with 54 tests covering:

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