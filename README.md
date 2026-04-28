# Em-Cubed (em-cubed)

A multi-surface Python platform for unified indexing, search, and skill execution.

## Overview

Em-Cubed integrates multiple execution surfaces (Prolog via Janus, Hy, Python) with a FastAPI serving layer and a core search/indexing engine. Skills are bundled as composable units that can run across different surfaces.

## Directory Structure

- `core/` — Indexer, search engine, registry
- `surfaces/` — Execution surfaces: Prolog adapter (janus), Hy adapter, Python runner
- `api/` — FastAPI serving layer
- `skills/` — Bundled example skills including POC
- `docs/` — Documentation (MULTI_SURFACE.md spec)
- `tests/` — Test suite

## Quick Start

```bash
pip install -r requirements.txt
# See docs for setup and running surfaces
```

## License

MIT