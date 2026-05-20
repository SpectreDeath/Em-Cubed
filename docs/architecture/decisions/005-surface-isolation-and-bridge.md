# ADR 005: Surface Isolation and Bridge Pattern

## Status

Accepted

## Context

Different execution surfaces have varying synchronous and asynchronous requirements. Some skills need to call into one surface from another (e.g., Python orchestrating Prolog). We need a clean pattern for cross-surface invocation that preserves isolation and supports telemetry.

## Decision

1. Each surface implements `SurfaceBase` with `execute()` (async) and a private `_execute_impl()` for the core logic.
2. A synchronous convenience method `execute_sync()` is provided in `SurfaceBase` to block on the async execution from synchronous call sites (e.g., skill code running under asteval). It reuses running event loops or falls back to a new loop, ensuring thread safety.
3. Cross-surface isolation is maintained by returning opaque dictionaries (`{"status": ..., "value": ...}`) rather than raw Python objects.
4. For multi-surface skills, `SkillExecutor` wraps surfaces in a `TelemetryProxy` that records trace spans. This proxy forwards calls transparently while tracking duration, input/output sizes, and success status.
5. The executor builds a `context` dict containing `"surfaces"` (a map of name → proxy) that is passed into each surface call, enabling skills to call other surfaces via `context["surfaces"]["surface_name"].execute_sync(code)`.

## Consequences

### Positive
- Explicit boundary between surfaces avoids accidental tight coupling.
- Trace annotations for free via proxy.
- Ability to enforce timeouts at the bridge level (`execute_with_timeout`).
- Works in both async and sync contexts.

### Negative
- Dictionary-based communication is low-level; type checking and structural guarantees are limited.
- Execution path adds layers (proxy → base → impl), which could impact performance for very small calls.
- Historical versions had thread-safety concerns addressed by creating isolated event loops for `execute_sync`.

## Alternatives Considered

1. Direct function calls across surfaces — Breaks isolation.
2. Shared objects with shared memory — Not applicable across language boundaries.
3. JSON-RPC or other IPC — Too heavy for in-process execution.
