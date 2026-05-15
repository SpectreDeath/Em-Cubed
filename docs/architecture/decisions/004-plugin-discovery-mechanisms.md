# ADR 004: Plugin Discovery Mechanisms

## Status

Accepted

## Context

The framework must support a variety of surface plugins. Surfaces might be built-in, provided by optional dependencies, or contributed as third-party packages. The discovery mechanism should be reliable, extensible, and support both eager and lazy loading to minimize startup overhead.

## Decision

Implement a three-tier discovery strategy in `PluginManager`:

1. **Built-in surfaces** — registered directly from the `em_cubed.surfaces` package. Core surfaces (python, prolog, hy, sqlite) are instantiated immediately; heavy surfaces (z3, datalog, cangjie, quickjs) are stored as classes for lazy initialization.
2. **Entry points** — third-party plugins can declare `em_cubed.surfaces` entry points in their `pyproject.toml`/`setup.cfg`. These are discovered via `importlib.metadata.entry_points`.
3. **Directory scan** — for local development, the manager can scan a `plugins/` directory for Python files defining `SurfacePlugin` subclasses and load them dynamically.

The `list_plugins()` method combines eager and lazy registrations. Lazy surfaces are instantiated on first use via `PluginManager.get()`.

## Consequences

### Positive
- Extensible: Third-party packages can contribute surfaces via entry points.
- Fast startup: Core surfaces load quickly; optional heavy surfaces are deferred.
- Flexible: Local plugin development without packaging.
- Backward compatible: Existing code relying on direct imports continues to work.

### Negative
- Complexity: Three different discovery paths increase code complexity.
- Dependency management: Heavy surfaces may fail to load; code must handle missing dependencies gracefully.
- discoverability: Errors in entry point groups may be silent or hard to debug.

## Alternatives Considered

1. Only built-in registration — No extensibility.
2. Pure entry points — Require packaging for every new surface (overhead for development).
3. Class-path scanning — Fragile, no standard mechanism.
