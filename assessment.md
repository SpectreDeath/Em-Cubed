# Em-Cubed Repository Assessment and Improvement Plan

**Assessment Date:** 2026-05-10
**Branches Analyzed:** `master` (primary)
**Codebase Version:** 0.5.0 (`src/em_cubed/__init__.py`)
**Python Version:** 3.14.2
**Status:** Phase 1 (Stabilization) and Phase 2 (Cleanup) technically complete, but new architectural bottlenecks and regressions identified.

---

## Executive Summary

The emergency stabilization (Phase 1) and architectural cleanup (Phase 2) successfully resolved critical bugs (missing imports, surface initialization). However, a deep-dive audit has revealed a fundamental architectural bottleneck: **the mismatch between async surfaces and synchronous skill execution (asteval)**. This prevents true cross-surface orchestration from within Python-based skills. Additionally, some "showcase" skills contain logical errors and the PluginManager has a test regression due to lazy loading.

**Current Key Findings:**

| Area           | Status           | Notes                                                     |
| -------------- | ---------------- | --------------------------------------------------------- |
| Python Surface | ✅ Fixed         | `import asyncio` added                                    |
| PluginManager  | ⚠️ Regression    | Lazy loading broke `list_plugins` tests                   |
| Test Pass Rate | ❌ 99% (137/141) | 1 failure, 3 skips in core tests                          |
| Architecture   | ⚠️ Bottleneck    | Sync/Async mismatch in skill orchestration                |
| Skill Library  | ⚠️ Improved      | 84 skill tests pass, but mostly syntax/metadata checks    |
| Docs           | ⚠️ Misleading    | Showcase examples don't match implementation              |
| Agent Skills   | ❌ Broken        | `prompt-quality-evaluator` logic calls async methods sync |

---

## 1. Newly Identified Issues

### 🔴 Issue 1: Sync/Async Orchestration Mismatch

**Status:** CRITICAL.
Python-based skills run in `asteval` (synchronous). Surfaces like `PrologSurface` and `HySurface` are `async`. When a Python skill tries to call `context["surfaces"]["prolog"].execute()`, it receives a coroutine but cannot `await` it. This makes integrated orchestration currently impossible without an architectural bridge.

### 🔴 Issue 2: Showcase Skill Logic Errors

**Status:** HIGH.
The `prompt-quality-evaluator` skill (the flagship showcase) uses `.query()` and `.assertz()` methods which do not exist on `PrologSurface` (it uses `.execute()`). Furthermore, the skill's logic attempts to run async surface methods synchronously, leading to runtime failures.

### 🟡 Issue 3: PluginManager Test Regression

**Status:** MEDIUM.
The introduction of lazy loading for heavy surfaces (Z3, Datalog) broke `test_discover_builtin_handles_missing_surfaces` because `list_plugins()` only returns already-loaded plugins.

### 🟡 Issue 4: Misleading Skill Testing

**Status:** MEDIUM.
The `SkillTestGenerator` primarily generates syntax and metadata checks. The "100% pass rate" for skills does not reflect logical correctness, as evidenced by the broken integrated skills passing their generated tests.

---

## 2. Architecture Assessment

### Modular Multilogic Architecture: 6/10 (downgraded)

While the design is sound on paper, the implementation has a major gap:

- ✅ 6 execution surfaces with unified interface
- ✅ Context injection in `SkillExecutor`
- ❌ **Missing Sync Bridge**: No mechanism for synchronous surface calls from within worker threads (where skills execute).
- ⚠️ **Lazy Loading Consistency**: `PluginManager` state is inconsistent between eager and lazy plugins for introspection methods.

---

## 3. Skills Assessment

### Flagship Skill: `prompt-quality-evaluator`

**Status:** ❌ LOGICALLY BROKEN.

- Calls `prolog.query()` instead of `prolog.execute()`.
- Ignores async nature of surface execution.
- Pass rate is 100% only because tests only check syntax.

### Example Skill: `python-prolog-pipeline`

**Status:** ⚠️ MISMATCH.

- Documentation claims it's a pipeline.
- Implementation is two separate, independent language versions.

---

## 4. Test Suite — Current Status

### Core Test Results (2026-05-10 run)

- **PASSED**: 137 tests
- **FAILED**: 1 test (`test_plugin_manager.py`)
- **SKIPPED**: 3 tests (Janus)
- **TOTAL**: 141 tests

### Coverage (Actual)

- **Overall**: ~71% (Significant improvement from previous 32% estimate)
- **Surfaces**: 80-90% (Excellent)
- **Core Orchestration**: 50-80% (Good)
- **Skills System**: 14-30% (Needs improvement)

---

## 5. Prioritized Action Plan (Updated)

### Phase 2.5: Orchestration Bridge (Next 48h) [DONE]

- [x] **Fix 1**: Implement `execute_sync()` in `SurfaceBase` to allow synchronous calling from worker threads.
- [x] **Fix 2**: Update `PluginManager.list_plugins()` to include lazy surfaces.
- [x] **Fix 3**: Update `prompt-quality-evaluator` to use `.execute_sync()` and the unified orchestration pattern.
- [x] **Fix 4**: Fix relative import regression in `quality_pipeline.py` test generation.

### Phase 4: True Showcase Implementation [DONE]

- [x] Refactored `Integrated Logic Solver` to use the new `execute_sync()` bridge.
- [x] Converted `python-prolog-pipeline` into a functional multi-surface orchestration example.
- [x] Verified orchestration bridge with new integration tests ([test_orchestration_logic.py](file:///D:/GitHub/projects/em-cubed/tests/test_orchestration_logic.py)).

### Phase 5: v0.5.0 Final Polish [UPCOMING]

- [ ] Increase `quality_pipeline.py` and `validator.py` coverage.
- [ ] Finalize Janus surface stability.
- [ ] All core tests passing (100% target).
- [ ] Tag v0.5.0 release.

---

## 6. Conclusion

Em-Cubed has the foundations of a powerful polyglot framework, but the current "integrated" skills are non-functional due to the async barrier. Fixing this bridge and updating the showcase skills to use the correct API is the immediate priority for the 0.5.0 release.

---

**Assessment prepared by:** Antigravity (AI coding assistant)
**Methodology:** Comprehensive core test run, skill testing audit, orchestration pattern analysis.

Em-Cubed v0.6.0 Roadmap: Scaling & Integration
Following the stabilization of the core polyglot orchestration bridge in v0.5.0, the next development cycle focuses on making the framework production-ready for complex, high-performance agentic workflows.

🎯 Primary Objectives
Observability: Implement a "Multi-Surface Trace" system to visualize and debug cross-paradigm execution.
Efficiency: Introduce a "Shared Substrate" for data exchange between surfaces to reduce serialization overhead.
DX (Developer Experience): Streamline the creation and testing of multi-surface skills.
Extensibility: Finalize the Janus (Datalog) surface and add a high-performance JavaScript (QuickJS) surface.
🛠️ Proposed Workstreams

1. Observability: Logical Tracing System
   Currently, debugging a Python skill that calls Prolog and Hy is difficult. We need a unified telemetry layer.

Task: Extend SkillTelemetry to capture sub-surface calls.
Output: A hierarchical JSON trace showing exactly what was sent to and received from each surface.
Integration: Add a --trace flag to the em3 run CLI command. 2. Efficiency: The Shared Substrate
Moving large datasets between Python (asteval) and Prolog (PySWIP) via JSON strings is inefficient.

Task: Explore shared_memory or a unified "Substrate" object that surfaces can access.
Initial Step: Implement "Referential Context" where surfaces can read from a common data store without re-serialization. 3. DX: CLI Tooling & Templates
Make it trivial to start a new multi-surface project.

Task: em3 create-skill <name> command.
Task: Provide boilerplate templates for "Python-Prolog-Bridge" and "Python-Z3-Optimization" patterns.
Task: VS Code extension support for .agents/skills/ syntax highlighting. 4. Ecosystem Expansion
Janus Integration: Move Janus (Prolog-Python bridge) from experimental to stable.
JS Surface: Add QuickJSSurface for executing logic-heavy JavaScript snippets (useful for web-oriented skills).
SQL Surface: Add an in-memory SQLiteSurface for declarative data querying within skills.
📅 Timeline & Milestones
Week 1: Observability & Janus Stability
Implement hierarchical tracing in SkillExecutor.
Resolve memory reclamation issues in JanusSurface.
Add em3 trace-view CLI utility.
Week 2: DX & New Surfaces
Implement em3 create-skill command.
Add QuickJSSurface (via pyquickjs).
Complete the "Skill Composition" pattern documentation.
Week 3: Efficiency & v0.6.0 Release
Prototype "Referential Context" for large data transfers.
Full integration testing of all 8 surfaces.
Documentation overhaul for v0.6.0.
