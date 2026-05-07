# Contributing to Em-Cubed

Thank you for your interest in contributing to Em-Cubed! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## 🤝 Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Optional: SWI-Prolog (for Prolog surface development)
- Optional: Hy (for Hy surface development)

### Quick Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/Em-Cubed.git
cd Em-Cubed

# Set up development environment
pip install -e ".[dev]"

# Run tests to verify setup
pytest

# Check code quality
ruff check src/ tests/
mypy src/
```

## 🛠️ Development Setup

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SpectreDeath/Em-Cubed.git
   cd Em-Cubed
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation**
   ```bash
   python -c "import em_cubed; print('Setup successful!')"
   pytest --version
   ruff --version
   mypy --version
   ```

### Development Tools

- **pytest**: Test runner with async support
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker
- **structlog**: Structured logging
- **FastAPI**: API framework with auto-docs

## 🔄 Development Workflow

### Branching Strategy

We use a simplified Git Flow:

```
main (production-ready)
├── feature/* (new features)
├── bugfix/* (bug fixes)
├── docs/* (documentation)
└── refactor/* (code refactoring)
```

### Working on Features

1. **Choose an issue** from the [GitHub Issues](https://github.com/SpectreDeath/Em-Cubed/issues)
2. **Create a branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number-description
   ```

3. **Develop with TDD** (Test-Driven Development):
   ```bash
   # Write tests first
   # Implement functionality
   # Run tests continuously
   pytest -v
   ```

4. **Follow code standards**:
   ```bash
   ruff check src/ tests/
   ruff format src/ tests/
   mypy src/
   ```

5. **Commit regularly** with clear messages:
   ```bash
   git add .
   git commit -m "feat: add new surface capability"
   ```

### Testing Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=em_cubed --cov-report=html

# Run specific tests
pytest tests/test_surfaces.py -v

# Run tests in watch mode (if installed)
# ptw tests/
```

## 📏 Code Standards

### Python Style

- **Formatter**: [Ruff](https://github.com/astral-sh/ruff) (replaces Black + isort)
- **Linter**: Ruff with strict rules
- **Type Checker**: [MyPy](https://mypy.readthedocs.io/) with strict mode

### Code Formatting

```bash
# Format code automatically
ruff format src/ tests/

# Check for linting issues
ruff check src/ tests/

# Fix auto-fixable issues
ruff check src/ tests/ --fix
```

### Type Hints

All public APIs must have complete type hints:

```python
from typing import Dict, Any, Optional

def execute_code(code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute code with proper typing."""
    pass
```

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Modules**: `snake_case`
- **Tests**: `test_function_name` or `TestClassName`

### Async/Await

Use async/await for I/O operations and when interfaces require it:

```python
async def execute_python(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Python code asynchronously."""
    # Implementation
    pass
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── test_core.py        # Core functionality
├── test_search.py      # Search engine
├── test_api.py         # API endpoints
├── test_integration.py # Full workflows
├── test_surfaces.py    # Surface execution
└── test_indexer.py     # Additional indexer tests
```

### Writing Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface

class TestPythonSurface:
    @pytest.mark.asyncio
    async def test_execute_expression(self):
        """Test basic expression execution."""
        surface = PythonSurface()
        result = await surface.execute("2 + 3", {})

        assert result["status"] == "ok"
        assert result["value"] == 5

    @pytest.mark.asyncio
    async def test_execute_with_context(self):
        """Test execution with context variables."""
        surface = PythonSurface()
        context = {"x": 10, "y": 20}
        result = await surface.execute("x + y", context)

        assert result["status"] == "ok"
        assert result["value"] == 30
```

### Test Coverage

- **Target**: 85%+ coverage for core modules
- **Required**: All new features must include tests
- **Integration**: End-to-end tests for critical workflows

### Running Tests

```bash
# Basic test run
pytest

# With coverage
pytest --cov=em_cubed --cov-report=term-missing

# Specific module
pytest tests/test_api.py -v

# Failed tests only
pytest --lf

# New tests only
pytest --nf
```

### CLI Testing

- **Coverage**: Test all `em3` subcommands (index, search, serve, run)
- **Mocking**: Mock system exits and command-line arguments
- **Error Handling**: Verify help text and error handling
- **Integration**: End-to-end CLI workflows

```bash
# Test CLI commands
pytest tests/test_cli.py -v

# Test CLI help output
em3 --help
```

## 📚 Documentation

### Code Documentation

- **Docstrings**: All public functions/classes must have Google-style docstrings
- **Comments**: Explain complex logic, not obvious code
- **Type Hints**: Complete type annotations

```python
def search_registry(query: str, registry_path: Path, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search the skill registry with multi-surface scoring.

    Args:
        query: Search query string
        registry_path: Path to registry JSON file
        max_results: Maximum number of results to return

    Returns:
        List of matching skills with scores

    Raises:
        FileNotFoundError: If registry file doesn't exist
    """
    pass
```

### README Updates

When adding new features:

1. Update relevant sections in README.md
2. Add usage examples
3. Update API documentation if endpoints change
4. Update installation requirements if dependencies change

## 📝 Submitting Changes

### Pull Request Process

1. **Ensure tests pass**:
   ```bash
   pytest
   ruff check src/ tests/
   mypy src/
   ```

2. **Validate skill quality** (for skill contributions):
   ```bash
   em3 quality --skills-dir skills/
   ```

3. **Update documentation** if needed

4. **Write clear commit messages**:
   ```
   feat: add new surface capability
   fix: resolve memory leak in search engine
   docs: update API documentation
   test: add integration tests for skill execution
   refactor: simplify indexer logic
   skills: enhance skill quality framework
   ```

5. **Create Pull Request**:
   - Use descriptive title
   - Reference related issues
   - Provide context and testing instructions
   - Request review from maintainers

6. **Address review feedback** and iterate

## 🧠 Skill Development Guide

### Creating a New Skill

Skills in Em-Cubed are defined in `skills/<DOMAIN>/<skill-name>/SKILL.md` files following a multi-surface paradigm.

#### Skill Structure

```markdown
---
name: My Skill
Domain: MACHINE_LEARNING  # Must be from allowed domains list
Version: 1.0.0
surfaces:
  - python  # At least 1 required, can include prolog, hy, z3, datatalog
dependencies:  # Optional dependencies on other skills
  - skill_id: "NLP/text-preprocessor"
    version_range: ">=1.0.0"
input_schema:  # JSON Schema for skill inputs
  type: object
  properties:
    data:
      type: array
  required: ["data"]
output_schema:  # JSON Schema for skill outputs
  type: object
  properties:
    result:
      type: number
capabilities:  # Required capabilities
  surfaces: ["python", "numpy"]
  permissions: ["file_read"]
  resources:
    memory_mb: 256
    cpu_cores: 1
compatibility:
  min_version: "0.4.0"
quality_thresholds:
  min_test_coverage: 0.8
  min_success_rate: 0.7
---

## Purpose
Brief description of what the skill does (min 10 chars).

## Description
Detailed explanation of the skill's functionality, use cases, and multi-surface approach.

## Implementation

### Python Core

```python
# Core algorithm implementation
def execute(data):
    # Your code here
    return {"result": processed_data}
```

### Prolog Logic (if applicable)

```prolog
% Logical constraints and validation rules
valid_input(Data) :-
    length(Data, Len),
    Len > 0.
```

### Hy Adaptive Logic (if applicable)

```hy
(defn adapt-parameters [context]
  "Adapt execution based on context"
  (let [params (get context "parameters")]
    (adjust-for-conditions params)))
```

## Testing

```python
# Unit tests for your skill
def test_my_skill():
    result = execute({"test": "data"})
    assert result["status"] == "ok"
```

## Usage

```python
from em_cubed import search_registry

# Find and use the skill
results = search_registry("my skill", "registry.json")
```
```

#### Skill Quality Standards

All skills MUST meet minimum quality thresholds before being accepted:

- **Structure Validation**:
  - Required fields present (name, Domain, surfaces)
  - Purpose ≥10 chars, Description ≥20 chars
  - At least 1 surface implementation with code
  - Valid YAML frontmatter

- **Code Quality**:
  - Python code must be syntactically valid
  - Prolog rules must be well-formed
  - Hy code (if present) must compile
  - All surfaces must have executable code blocks

- **Testing**:
  - Include at least 1 test case in Testing section
  - Tests should cover primary functionality
  - Aim for 80%+ test coverage

- **Documentation**:
  - Clear purpose and description
  - Surface implementations explained
  - Usage examples provided

#### Skill Review Process

1. **Automated Validation**: CI runs `em3 quality` to check skill quality
2. **Manual Review**: Maintainer reviews code quality, security, and design
3. **Integration Testing**: Verify skill composes well with others
4. **Performance Check**: Ensure skill meets timing/resource requirements
5. **Final Approval**: Merge after addressing all feedback

#### Quality Gates

- **Gate 1 (Pre-commit)**: Ruff linting, mypy type checking, basic syntax
- **Gate 2 (CI Validation)**: `em3 validate` ensures all skills pass structure checks
- **Gate 3 (Quality Pipeline)**: `em3 quality` runs full validation, testing, and benchmarking
- **Gate 4 (Integration)**: Verify skill works in compositions and with API

### Skill Composition

Skills can be composed together using the composer framework:

```python
from em_cubed.skills import SkillComposer, CompositionStep

composer = SkillComposer(plugin_manager, registry)

# Sequential pipeline
plan = composer.create_pipeline([
    CompositionStep(
        skill_id="NLP/text-preprocessor",
        input_mapping={"text": "input.text"},
        output_mapping={"tokens": "data.tokens"}
    ),
    CompositionStep(
        skill_id="NLP/sentiment-analyzer",
        input_mapping={"tokens": "data.tokens"},
        output_mapping={"sentiment": "output.score"}
    ),
])

result = await composer.compose(plan, {"input": {"text": "Hello world"}})
```

### Telemetry and Metrics

Em-Cubed automatically tracks skill usage and performance:

- Execution counts (success/failure)
- Execution time statistics
- Token usage estimation
- Error tracking and classification

This data feeds into quality scores and recommendations.

## 🌍 Community

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/SpectreDeath/Em-Cubed/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SpectreDeath/Em-Cubed/discussions)
- **Documentation**: [README.md](README.md) and [docs/](docs/)

### Communication

- Be respectful and constructive
- Use clear, descriptive language
- Provide context and examples
- Help others when possible

### Recognition

Contributors are recognized in:
- GitHub repository contributors
- CHANGELOG.md for significant contributions
- Release notes for major features

## 🎯 Areas for Contribution

### High Priority
- [ ] Additional execution surfaces (JavaScript, SQL, Shell)
- [ ] Performance optimizations
- [ ] Enhanced security features
- [ ] Plugin system for custom surfaces

### Medium Priority
- [ ] Web UI for skill browsing
- [ ] VS Code extension
- [ ] Docker integration
- [ ] Skill marketplace

### Good for Beginners
- [ ] Documentation improvements
- [ ] Example skill creation
- [ ] Test coverage expansion
- [ ] Code refactoring

---

Thank you for contributing to Em-Cubed! Your efforts help make multi-surface programming more accessible and powerful. 🚀

## 📦 Surface Integration Guidelines

When developing skills, **always** use the Em-Cubed surface abstractions (`em_cubed.surfaces`) instead of direct library imports. This ensures consistency, security, and portability across environments.

### ❌ Don't

```python
# Direct library access - not portable
from pyswip import Prolog
prolog = Prolog()
```

### ✅ Do

```python
# Use framework-provided surface
from em_cubed.surfaces import PrologSurface
# Or better: obtain via PluginManager
result = await plugin_manager.get("prolog").execute("...", context)
```

### Migration Checklist

- [ ] Replace direct imports of `pyswip`, `hy`, `z3`, `pyDatalog` with corresponding `em_cubed.surfaces.*Surface` usage.
- [ ] Update skill code to execute via `surface.execute(code, context)`.
- [ ] Remove initialization of external libraries inside skill code.
- [ ] Test skill with the updated surface abstraction.

Skills that continue to use direct imports will be deprecated in a future release. See the full migration guide in `docs/SURFACE_MIGRATION.md` for detailed patterns and examples.</content>
<parameter name="filePath">D:\GitHub\projects\em-cubed\CONTRIBUTING.md