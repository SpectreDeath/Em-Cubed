# Changelog

All notable changes to Em-Cubed will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Logic surfaces**: `KanrenSurface` (MiniKanren relational logic) and `ClingoSurface` (Answer Set Programming via `clingo`)

### Removed
- **Cangjie surface**: removed due to missing compiler/runtime dependency and low usage; all `SKILL_CANGJIE.md` artifacts deleted from skills and tests

## [0.7.0] - 2026-05-15

### Added
- **Ecosystem**: `SQLiteSurface` with session-persistent in-memory execution
- **Ecosystem**: `QuickJSSurface` for JavaScript execution via `pyquickjs` (lazy-loaded)
- **CLI**: `em3 surfaces` — list all registered surfaces with availability and load status
- **CLI**: `em3 skill-info <skill_id>` — display full metadata and quality metrics for a skill
- **Templates**: three new skill templates: `sqlite_analysis`, `z3_optimization`, `quickjs_transform`
- **Skills**: four new example skills: `sql-aggregator`, `z3-schedule-solver`, `js-text-transformer`, `sqlite-pipeline`
- **Docs**: two new ADRs: `004-plugin-discovery-mechanisms.md`, `005-surface-isolation-and-bridge.md`

### Changed
- **CLI**: `em3 create-skill` now uses Jinja2 for robust template rendering
- **Surface registration**: `SQLiteSurface` registered as core (eager); `QuickJSSurface` registered as lazy
- **Cangjie surface**: context is now piped to stdin instead of passing a JSON file path as an argument
- **Validation**: `SkillValidator` now acknowledges `cangjie`, `sqlite`, and `quickjs` as valid surfaces

### Fixed
- **Entry point discovery**: replaced deprecated `import entry_points` with `from importlib.metadata import entry_points`
- **QuickJS compatibility**: context injection switched from `ctx.parse_json` to `ctx.eval()` for broader pyquickjs compatibility
- **Surfaces**: `SQLiteSurface` and `QuickJSSurface` are properly exported from `surfaces/__init__.py`

## [0.6.0] - 2026-05-14

### Added
- **Efficiency**: "Shared Substrate" for efficient zero-copy data exchange between surfaces.
- **DX**: `em3 create-skill` CLI command for instant multi-surface skill generation from templates.
- **Ecosystem**: `SQLiteSurface` for in-memory relational querying within skill pipelines.
- **Ecosystem**: `QuickJSSurface` for high-performance JavaScript execution via `pyquickjs`.
- **Observability**: Enhanced trace visualization in `em3 trace-view` showing data flow and serialization sizes.
- **Boilerplate**: Standardized skill templates for basic Python and Python-Prolog bridge patterns.

### Changed
- **Telemetry**: Standardized all timestamps to timezone-aware UTC objects to prevent runtime errors in mixed environments.
- **Orchestration**: `TelemetryProxy` now supports proxying properties like `substrate`.
- **CLI**: Improved `run --trace` output with data size reporting.

### Fixed
- **execute_sync**: Resolved `RuntimeError` when calling synchronous surfaces from within threaded execution environments.
- **Telemetry persistence**: Fixed mixed naive/aware datetime subtraction bug during metric aggregation.

## [0.5.0] - 2026-05-14

### Added
- Optional API key authentication (`X-API-Key` header) via `EM_CUBED_API_KEY`
- JanusSurface fully integrated and registered in PluginManager
- `asyncio_mode = "auto"` in pytest configuration for seamless async tests
- Surface migration guide (`docs/SURFACE_MIGRATION.md`)
- Explicit surface usage policy in `CONTRIBUTING.md`

### Changed
- **Architecture**: Merged `SurfaceBase` into `SurfacePlugin`; `SurfaceBase` now a deprecated alias for backward compatibility
- **Validation**: `SkillValidator` now reads `skills/manifest.yaml` for authoritative domain list and quality thresholds
- **Inheritance**: All surfaces now inherit exclusively from `SurfacePlugin` (single inheritance)
- **Version**: Unified version numbers to `0.5.0` across `__init__.py`, `api/main.py`, and `pyproject.toml`
- **Dependency**: `asteval` used for Z3 and Datalog execution, replacing unsafe `exec`/`eval`

### Fixed
- **entry_points import**: corrected to `from importlib.metadata import entry_points` with function call syntax for Python 3.11+
- **Z3Surface test_health bug**: fixed accidental use of `DatalogSurface` in test (line 273)
- **DatalogSurface security**: removed `exec`/`eval`; now uses asteval.Interpreter with pyDatalog module injection
- **Z3Surface security**: removed `exec`; now uses asteval.Interpreter with Z3 symbols pre-injected
- **Benchmark psutil**: wrapped import with try/except and graceful degradation when psutil unavailable
- **Plugin discovery**: JanusSurface now properly included in `_discover_builtin()` registrations
- **API documentation**: Fixed search response format to include domain, purpose, logic_tags, heuristic_tags, and tags
- **Documentation**: Updated README test count (77→219) and coverage (81%→~26%)
- **Documentation**: Added Z3, Datalog, Janus surfaces to README reference
- **Prolog**: Fixed assertion bug in test_concurrent_mixed_surfaces (removed trailing period)
- **Types**: Added missing imports in benchmark.py, composer.py, quality_pipeline.py, recommender.py
- **Ruff**: Fixed 70 lint warnings (42 auto, 28 manual)
- **Testing**: Fixed invalid f-string escape sequence in testing.py:179

### Security
- Eliminated all direct `exec`/`eval` calls in surface implementations
- API optional authentication prevents unauthorized access when configured
- Surface executions remain sandboxed via asteval (Python, Z3, Datalog)

## [0.4.0] - 2026-04-29

### Added
- **Async timeouts** - Configurable execution timeouts across all surfaces (default 30s)
- **Incremental indexing** - Only re-index changed skill files (10x+ performance boost)
- **Plugin system** - Extensible surface architecture with 3 discovery mechanisms
- **SurfacePlugin interface** - Abstract base class for custom surface implementations
- **PluginManager** - Manages surface plugins with automatic discovery
- **EM_CUBED_TIMEOUT** environment variable support
- **--timeout flag** for em3 run command
- **Timeout parameter** for API /execute endpoint
- **--incremental flag** for em3 index command
- **Registry schema v2** with modification time tracking

### Changed
- **All surface execute() methods now async** - Breaking change for API clients
- **CLI uses PluginManager** - No more hardcoded surface imports
- **API uses PluginManager** - Dynamic surface loading and health checks
- **Registry format extended** - Includes last_modified timestamps
- **Test suite updated** - All surface tests now async, improved mocking

### Performance
- **10x+ faster incremental indexing** for large skill collections
- **Timeout protection** prevents hanging on infinite loops
- **Lazy plugin loading** reduces startup time

### Breaking Changes
- Surface execute() methods are now async and must be awaited
- API clients must update to handle async responses
- Registry schema upgraded to v2 (backward compatible)

## [0.3.0] - 2026-04-28

### Added
- **CLI entrypoint (em3)** with four subcommands: index, search, serve, run
- **Whoosh full-text search** with BM25F scoring and fuzzy matching
- **GET /search endpoint** for simpler client usage
- **Persistent Prolog interpreter** for multi-step workflows
- **Schema versioning** (v1) for future migrations
- **Comprehensive CLI test suite** (tests/test_cli.py, 15 test cases)

### Changed
- **Whoosh index caching** - 100× faster searches with persistent index
- **PrologSurface** - assert vs query mode detection, lazy interpreter init
- **HySurface** - Fixed deprecated hy.read() -> hy.read_many()
- **Version bumped** to 0.3.0 in __init__.py and api/main.py

### Security
- **Prolog context injection** - Patched with _prolog_safe_value() method
- **Prolog query timeout** - 10-second timeout prevents resource exhaustion
- **Prolog result limiting** - Automatic truncation to 1000 solutions
- **Dependency cleanup** - Removed unused packages (pydantic-settings, httpx, python-multipart)

### Fixed
- **Prolog double-execute bug** - Fixed with proper assert/query mode separation
- **CLI run_async bug** - Fixed unreachable code for non-Python surfaces
- **Whoosh index rebuild** - Fixed by tracking registry hash changes
- **JanusSurface cleanup** - Removed from public API exports

---

## [0.2.0] - 2026-03-15

### Added
- **54/54 tests passing** with ruff clean, mypy clean
- **Quality gate** - All tests passing, linting clean, types clean
- **Pushed to GitHub** (commit d6ad6ac)

### Changed
- **Python surface** - Enhanced security with asteval
- **Prolog surface** - Improved query execution and error handling
- **Logging** - Added structured logging with structlog throughout
- **Dependencies** - Consolidated to single pyproject.toml

### Fixed
- **HTTPException handling** in API endpoints
- **Prolog tag extraction** regex for proper predicate matching
- **Python surface error handling** with asteval exceptions

---

## [0.1.0] - 2026-04-28

### Added
- Initial multi-surface framework architecture
- Core execution surfaces: Python, Prolog, Hy, Janus (placeholder)
- Skill indexing and search with multi-surface scoring
- REST API with FastAPI for skill execution
- Basic testing infrastructure
- Project structure and configuration

### Security
- Safe Python execution via asteval
- Input validation on all API endpoints
- Restricted execution environments

### Documentation
- Basic README with setup instructions
- API endpoint documentation
- Surface reference guides

---

## Release Process

### Pre-release Checklist
- [ ] All tests passing (54/54)
- [ ] Code coverage ≥76%
- [ ] Ruff linting clean
- [ ] MyPy type checking clean
- [ ] Documentation complete
- [ ] CHANGELOG.md updated
- [ ] Version updated in pyproject.toml
- [ ] Release notes prepared

### Release Steps
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Commit changes: `git commit -m "release: v0.2.0"`
4. Create git tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
5. Push to GitHub: `git push origin master --tags`
6. Create GitHub release with release notes
7. Optionally publish to PyPI: `python -m build && twine upload dist/*`

### Version Format
Em-Cubed follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Types
- **Alpha/Beta**: Pre-release versions (e.g., `0.2.0-alpha.1`)
- **Release Candidate**: Final testing (e.g., `0.2.0-rc.1`)
- **Stable**: Production ready (e.g., `0.2.0`)

---

## Development Milestones

### Completed ✅
- **Month 1**: Code consolidation and stabilization
- **Month 2**: Testing & Quality (54 tests, 76% coverage)
- **Month 3**: Documentation & Polish (4 example skills, comprehensive docs)

### Future Releases
- **v0.3.0**: Additional surfaces (JavaScript, SQL, Shell)
- **v0.4.0**: Web UI and skill marketplace
- **v0.5.0**: Performance optimizations and enterprise features
- **v1.0.0**: Production-ready multi-surface framework

---

## Contributors

- **SpectreDeath**: Project creator and maintainer
- **Community**: Bug reports, feature requests, and contributions welcome!

For more information about contributing, see [CONTRIBUTING.md](CONTRIBUTING.md).
## [0.8.0] - 2026-05-29

### Added
- **Optimization Skills**: Completed P2 and P3 optimization algorithm skills
  - Dialectic Search (DA): Thesis-antithesis-synthesis thinker types - 8/8 tests
  - Chaos Optimization (COA): Logistic/Tent/Sinusoidal chaotic maps - 9/9 tests
  - Fractal-Based Algorithm (FBA): Hierarchical space partitioning - 7/7 tests
  - Central Force Optimization (CFO): Gravitational attraction between probes - 9/9 tests
  - Spiral Dynamics Optimization (SDO): Damped harmonic oscillations - 7/7 tests
- **Multi-Surface Implementation**: All optimization skills include Python core, Prolog validation, and Hy helpers
- **SKILL_CANGJIE.md**: Cangjie orchestrator files for all optimization algorithms

### Changed
- **Test Suite**: Updated to 57 optimization skill tests (all passing)

### Notes
- NOA2 (Neuroboids Optimization 2) NOT implemented - requires deep learning/PyTorch (outside scope)
