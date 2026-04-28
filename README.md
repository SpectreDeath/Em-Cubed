# Em-Cubed (em-cubed)

A multi-surface Python platform for unified indexing, search, and skill execution across Python, Prolog, and Hy.

## Overview

Em-Cubed integrates multiple execution surfaces (Python, Prolog, Hy) with a core search/indexing engine.
Skills are bundled as composable units that can run across different surfaces.

## Directory Structure

- `src/em_cubed/` — Core package (indexer, search, surfaces)
  - `indexer.py` — Skill indexing and metadata extraction
  - `search.py` — Registry search with multi-surface scoring
  - `surfaces/` — Execution surfaces: Python, Prolog, Hy, Janus (Prolog bridge)
- `skills/` — Bundled example skills including POC
- `docs/` — Documentation (MULTI_SURFACE.md spec)
- `tests/` — Test suite

## Quick Start

```bash
# Install package and dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Index skills
python -m em_cubed.indexer skills/ registry.json

# Search registry
python -m em_cubed.search registry.json "query"

# Start API server
uvicorn api.main:app --reload

# API will be available at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

## Surface Reference

### Python
- Native Python execution with context injection
- Safe evaluation via restricted globals

### Prolog
- Integration via pyswip/SWI-Prolog
- Predicate extraction from source

### Hy
- Hy Lisp execution
- Function extraction from defn forms

### Janus
- Python-Prolog bridge via SWI-Prolog
- Shared memory context between Python and Prolog

## Testing

- All tests: `pytest`
- Coverage report: `pytest --cov=em_cubed`
- Linting: `ruff check .`
- Type checking: `mypy src/`

## License

MIT