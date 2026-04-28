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

- **Target**: 80%+ coverage for core modules
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

2. **Update documentation** if needed

3. **Write clear commit messages**:
   ```
   feat: add new surface capability
   fix: resolve memory leak in search engine
   docs: update API documentation
   test: add integration tests for skill execution
   refactor: simplify indexer logic
   ```

4. **Create Pull Request**:
   - Use descriptive title
   - Reference related issues
   - Provide context and testing instructions
   - Request review from maintainers

5. **Address review feedback** and iterate

### Commit Message Format

We follow [Conventional Commits](https://conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

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

Thank you for contributing to Em-Cubed! Your efforts help make multi-surface programming more accessible and powerful. 🚀</content>
<parameter name="filePath">D:\GitHub\projects\em-cubed\CONTRIBUTING.md