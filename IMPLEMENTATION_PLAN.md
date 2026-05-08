# Em-Cubed Implementation Plan
## Based on Assessment.md Recommendations

**Plan Created:** 2026-05-06  
**Current Branch:** `master`  
**Version Target:** v0.5.0  
**Total Estimated Effort:** 15-30 hours across 4 phases

---

## PHASE 1: IMMEDIATE STABILIZATION (3-4 hours)
*Goal: Fix critical documentation mismatches and test failures before any release*

### Priority 1: Fix Failing Test (5 minutes)
**File:** `tests/test_concurrent.py:54`  
**Issue:** Prolog assertion bug - using trailing `.` for arithmetic query

**Action:**
```python
# Change from:
tasks.append(surf.execute("X is 1 + 1.", {}))

# To:
tasks.append(surf.execute("X is 1 + 1", {}))
```

**Verification:**
```bash
pytest tests/test_concurrent.py::TestConcurrentExecution::test_concurrent_mixed_surfaces -v
```

---

### Priority 2: Documentation Corrections (2-3 hours)
**Critical mismatches between documentation and implementation**

#### 2.1 Fix API Response Format in `docs/api-reference.md`
**Current (incorrect):**
```json
{
  "results": [{
    "id": "skill_id",
    "name": "...",
    "description": "...",
    "score": 0.95,
    "tags": ["tag1"],
    "surfaces": ["python"],
    "metadata": {...}
  }]
}
```

**Actual implementation:**
```json
{
  "results": [{
    "name": "...",
    "domain": "...",
    "purpose": "...",
    "path": "...",
    "surfaces": [...],
    "logic_tags": [...],
    "heuristic_tags": [...],
    "score": ...
  }]
}
```

**Action:** Replace the "Response" section in the POST /search endpoint (lines 38-51) with actual fields.

**Also add:**
- Error response format: `{"detail": "Error message"}` (currently undocumented)
- Note: API key is optional (only enforced if `EM_CUBED_API_KEY` set)
- Clarify that GET /search returns same format wrapped in `{"results": [...]}`

#### 2.2 Update README.md Statistics (10 minutes)
**Line 16:** `77 tests with 81% coverage` → `219 tests with ~26% coverage`  
**Line 19:** `v0.4.0` → `v0.5.0`  

**Action:** Search for all mentions of test count, coverage, and version; update to reflect current reality.

**Impact:** Badges on line 4 also need updating (though they link to GitHub, may auto-update). Consider replacing with accurate manual text.

#### 2.3 Add Missing Surfaces to README (30 minutes)
**Section:** "Surface Reference" (lines 224-304)  
**Current:** Only documents Python, Prolog, Hy  
**Need to add:** Z3, Datalog, Janus subsections

**Template for each:**
```markdown
### Z3 Surface

**Capabilities**: SMT solving for logical constraints and verification.

```python
from em_cubed.surfaces import Z3Surface

surface = Z3Surface()
if surface.available:
    result = await surface.execute("x + y == 5", {"x": 2, "y": 3})
    print(result['value'])  # True
```

**Requirements**: z3-solver package.
```

Update lines 224-304 to include:
- Z3 (new section after Hy)
- Datalog (new section after Z3)
- Janus (new section after Datalog, note: experimental/optional)

#### 2.4 Add GET /search Example to README (5 minutes)
**Location:** API Documentation section after POST /search (around line 425)  
**Action:** Add GET example:
```bash
curl "http://localhost:8000/search?q=calculator&top=5"
```

---

### Priority 3: Code Quality Quick Wins (30-45 minutes)
#### 3.1 Run Ruff Auto-Fix (5 minutes)
```bash
ruff check --fix src/ tests/
```

**Expected to fix 42 issues automatically:**
- F401: Unused imports
- F541: f-strings without placeholders
- F841: Unused local variables
- F402: Loop variable shadows import

**Then manually review remaining 28 issues.**

#### 3.2 Fix Non-Auto Ruff Issues (20-30 minutes)
**Key files from assessment:**
- `src/em_cubed/skills/testing.py:179` - Invalid escape sequence in f-string
  ```python
  # Current: f"SYNTAX_ERROR: {{e}}"
  # Should be: f"SYNTAX_ERROR: {e}"
  ```

- `src/em_cubed/__init__.py` - Unused imports (Z3Surface, DatalogSurface)
- `src/em_cubed/skills/benchmark.py` - Undefined names (SkillRegistry, SkillMetadata)
- `src/em_cubed/skills/composer.py` - Missing imports for SkillRegistry, CompositionResult
- `src/em_cubed/skills/quality_pipeline.py` - Missing imports for BenchmarkResult
- `src/em_cubed/skills/recommender.py` - Undefined SkillRegistry, tuple type syntax error

**Strategy:** Add proper imports (see Phase 2 for detailed import fixes).

#### 3.3 Validate All Fixes (10 minutes)
```bash
ruff check src/ tests/
mypy src/ --show-error-codes
pytest -x
```

---

## PHASE 2: ARCHITECTURAL INTEGRITY (4-8 hours)
*Goal: Ensure type safety, fix broken imports, and validate surface architecture*

### Priority 4: Type Safety - Missing Imports (2-3 hours)
**All quality modules have undefined names that would cause NameError if executed.**

#### 4.1 Fix `src/em_cubed/skills/benchmark.py`
**Problem:** Lines 148, 158, 207 use `SkillRegistry`, `SkillMetadata` without imports.

**Fix:**
```python
# Add to top of file (after line 7):
from .registry import SkillRegistry
from .metadata import SkillMetadata
```

#### 4.2 Fix `src/em_cubed/skills/composer.py`
**Problem:** Line 17 imports `SkillMetadata` but not `CompositionResult` (used line 183, 204, etc.)

**Fix:** Add to line 17:
```python
from .metadata import SkillMetadata, CompositionResult
# Or if CompositionResult defined elsewhere:
# from .composer import CompositionResult  # but same file - need to check location
```

**Check:** CompositionResult defined in composer.py line 407. So `CompositionResult` is in same file - no import needed. The actual error may be missing `.registry` import for `SkillRegistry` on line 17.

**Action:** Ensure both are imported:
```python
from .registry import SkillRegistry
from .metadata import SkillMetadata
```

#### 4.3 Fix `src/em_cubed/skills/quality_pipeline.py`
**Problem:** Line 16 imports `BenchmarkResult` but line 110, 111 may need it.

**Already has:** `from .benchmark import SkillBenchmark, BenchmarkConfig`

**Fix:** Ensure BenchmarkResult imported:
```python
from .benchmark import SkillBenchmark, BenchmarkConfig, BenchmarkResult
```

#### 4.4 Fix `src/em_cubed/skills/recommender.py`
**Problem:** Line 69 uses `SkillRegistry` without import. Line 105 has invalid tuple type annotation `(float, List[str])`

**Fix:**
```python
# Add import at top:
from .registry import SkillRegistry

# Fix line 105 return type annotation:
def _score_skill(self, skill, requirement: TaskRequirement) -> tuple[float, List[str]]:
```
- Change `(float, List[str])` → `tuple[float, List[str]]` (or import `Tuple` from typing and use `Tuple[float, List[str]]`)

#### 4.5 Fix `src/em_cubed/skills/testing.py`
**Problem:** Lines 244-250 assign int/bool/list[Never] to str fields in TestResult.

**Review:** `result.get("value")` returns `Any`. Need to cast or adjust `TestResult.output` optional type.

**Check:** TestResult dataclass defines `output: Optional[Any] = None` (line 52). But the error is about assigning `int`/`bool`/`list[Never]` to `str` fields. Likely incompatible assignments in `to_dict()` method where `str(self.output)[:200]` expects string conversion.

**Action:** Change type of `output` in `TestResult` to `Any` or accept string conversion. Review mypy error lines 244-250 precisely by running mypy.

#### 4.6 Fix `src/em_cubed/skills/telemetry.py`
**Problem:** Optional chaining on `Path | None` without null checks.

**Action:** Add null checks before accessing `.parent` on optional paths. Run mypy to identify exact lines.

#### 4.7 Fix Invalid Tuple Type Annotations (1 hour)
**Search for:** `-> (T1, T2)` syntax  
**Replace with:** `-> Tuple[T1, T2]` (import from typing) or Python 3.11+ native `tuple[T1, T2]`

---

### Priority 5: Surface Context Injection Verification (2-3 hours)
**Framework feature exists but skills don't use it.**

#### 5.1 Verify Context Injection Works
**Location:** `src/em_cubed/skills/executor.py` lines 136-141  
**Action:** Read executor.py to confirm context injection mechanism provides `context["surfaces"]` dict.

```python
# Expected pattern:
context = {
    "variables": {...},
    "surfaces": {
        "python": python_surface_instance,
        "prolog": prolog_surface_instance,
        ...
    }
}
```

#### 5.2 Audit Multi-Surface Skills (1 hour)
**Target skills:**
- `skills/OPTIMIZATION/pathfinding-with-constraints/SKILL.md`
- `skills/DECISION_MAKING/multi-surface-decision-tree/SKILL.md`

**Current problem:** Testing sections use raw imports:
```python
from pyswip import Prolog  # Bypasses framework, fails in asteval
```

**Required fix:** Either:
1. Update to use `context["surfaces"]["prolog"]` injected by SkillExecutor
2. Change testing to call `SkillExecutor` instead of direct surface execution
3. Document that testing sections are illustrative only (not meant to run standalone)

**Recommendation:** Option 3 with a note in testing section:
```markdown
## Testing

*Note: These tests use direct imports for illustration. In production,
use the SkillExecutor which injects surface plugins via context.*
```

OR convert to framework-based tests:
```python
from em_cubed.skills.executor import SkillExecutor

executor = SkillExecutor(plugin_manager)
result = await executor.execute("skill_id", {"input": data})
```

#### 5.3 Document Context Injection Pattern
**Create:** `docs/MULTI_SURFACE_GUIDE.md`  
**Content:**
- How to access `context["surfaces"]` in Python skills
- Example: Python preprocessing → Prolog query → Hy post-processing
- Pattern for returning combined results
- Limitations (each surface still isolated, no shared state beyond context dict)

---

### Priority 6: Manifest-Driven Validation (1 hour)
**Validator should read `skills/manifest.yaml` for thresholds.**

#### 6.1 Review Current Implementation
**File:** `src/em_cubed/skills/validator.py`  
**Check:** Does it read `manifest.yaml`? Assessment says "already mostly done in skills-library branch."

**Action:** Compare with skills-library branch version if needed. Ensure:
- All hardcoded thresholds replaced with manifest values
- Domain list sourced from manifest
- Quality thresholds (min_success_rate, min_coverage) from manifest

#### 6.2 Document Manifest Fields
**File:** `docs/SKILLS_QUALITY.md`  
**Add:** Section explaining all `manifest.yaml` keys:
```yaml
domains: [...]                    # Allowed skill domains
quality_thresholds:
  min_success_rate: 0.7
  min_test_coverage: 0.8
  max_execution_time: 30.0
...
```

---

## PHASE 3: QUALITY & ECOSYSTEM (1 week)
*Goal: Improve test coverage, fix benchmark implementation, add lazy loading*

### Priority 7: Test Coverage Expansion (2-3 days)
**Current:** ~26% overall (quality modules very low)  
**Target:** 60% overall

#### 7.1 Benchmark Module Coverage (currently 25%)
**Add tests for:**
- `test_benchmark_config_serialization()`
- `test_benchmark_result_from_timing_data()`
- `test_benchmark_surface_execution()`
- `test_benchmark_timeout_handling()`
- `test_memory_profiling()`
- `test_benchmark_export()`

**Location:** `tests/test_benchmark.py` (create)

#### 7.2 Recommender Module Coverage (currently 21%)
**Add tests for:**
- `test_recommend_score_skill_domain_match()`
- `test_recommend_score_surface_preference()`
- `test_recommend_quality_threshold_filter()`
- `test_get_similar_skills()`
- `test_recommend_chain_bfs()`
- `test_extract_keywords_from_description()`

**Location:** `tests/test_recommender.py` (create)

#### 7.3 Quality Pipeline Coverage (currently 15%)
**Add tests for:**
- `test_validate_all_skills()`
- `test_test_all_skills()`
- `test_benchmark_all_skills()`
- `test_get_quality_report()`
- `test_pipeline_end_to_end()`

**Location:** `tests/test_quality_pipeline.py` (create)

#### 7.4 Composer Module Coverage (~28% → 60%)
**Add integration tests:**
- Sequential composition
- Parallel composition
- Conditional branching
- Pipeline with error handling
- Context data flow between steps

**Location:** `tests/test_composer.py` (add to existing if present)

#### 7.5 Telemetry & Executor Coverage
**Add tests for:**
- Telemetry: execution recording, aggregation
- Executor: skill loading, surface selection, timeout handling

#### 7.6 Expand Integration Tests
**File:** `tests/test_integration.py`  
**Add:** Full workflow: index → search → execute → compose

---

### Priority 8: Implement Real Benchmarking (2-3 hours)
**Current:** `_execute_skill_once` returns `{"status": "ok", "value": "mock result"}`  
**Required:** Integrate with actual `SkillExecutor`

**Action (in `benchmark.py` line 248-256):**

```python
async def _execute_skill_once(self, skill: SkillMetadata, plugin, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a skill once for benchmarking."""
    from .executor import SkillExecutor

    # Resolve skill path
    skill_path = Path(skill.path) if skill.path else None
    if not skill_path or not skill_path.exists():
        raise ValueError(f"Skill path not found: {skill.path}")

    # Load and execute via SkillExecutor
    executor = SkillExecutor(plugin_manager=self.plugin_manager)
    result = await executor.execute_skill(
        skill_path=skill_path,
        surface=plugin.name,
        input_data=input_data,
        timeout=self.config.timeout
    )
    return result
```

**Also:**
- Add memory profiling with `psutil` (already imported, needs implementation at line 216-227)
- Add warmup iterations (already present in config, line 31)
- Document benchmark metrics (create `docs/BENCHMARKING.md`)

---

### Priority 9: Surface Lazy Loading (2-3 hours)
**Current:** All surfaces loaded eagerly at startup (`PluginManager.__init__`)  
**Impact:** Z3 and Datalog heavy even if unused.

**Implementation:**

#### 9.1 Modify `PluginManager` (`src/em_cubed/plugin_manager.py`)

Add lazy initialization flag and factory method:
```python
class PluginManager:
    def __init__(self):
        self._plugins: Dict[str, SurfacePlugin] = {}
        self._lazy_surfaces = ["z3", "datalog"]  # Heavy surfaces to defer
        self._initialized = False

    def get(self, name: str) -> Optional[SurfacePlugin]:
        if not self._initialized:
            self._initialize_core_surfaces()  # Python, Prolog, Hy
        if name in self._lazy_surfaces and name not in self._plugins:
            self._initialize_surface(name)  # On-demand
        return self._plugins.get(name)
```

#### 9.2 Refactor `_discover_builtin()`
Separate into:
- `_initialize_core_surfaces()` - Python, Prolog, Hy (eager)
- `_initialize_heavy_surfaces()` - Z3, Datalog (lazy)
- `_initialize_optional_surfaces()` - Janus (on demand)

#### 9.3 Measure Impact
Add logging for initialization times. No tests needed if logic is straightforward.

---

### Priority 10: Documentation Expansion (2-3 hours)
#### 10.1 Developer Guide for New Surfaces
**Create:** `docs/SURFACE_DEVELOPMENT.md`
**Content:**
- Subclass `SurfacePlugin` (or `SurfaceBase`)
- Implement required methods: `name`, `description`, `available`, `execute`, `extract_tags`
- Register via `PluginManager` (built-in or entry point)
- Security considerations (sandboxing, timeouts)
- Testing requirements

#### 10.2 SKILL.md Frontmatter Reference
**File:** `docs/SKILLS_QUALITY.md`  
**Expand:** Document all frontmatter fields:
```
name: (required) Skill name
Domain: (required) From manifest.yaml allowed list
Version: (required) Semver
surfaces: (required) List of surface names
Type: (optional) Process/Function/Cognitive/etc.
Category: (optional) Classification
Complexity: (optional) Low/Medium/High
Estimated Execution Time: (optional) Human-readable estimate
triggers: (optional) List of trigger keywords
quality: (optional)
  applied_count, success_count, completion_rate, token_savings_avg
created_at, updated_at: (auto) ISO timestamps
origin: (optional) manual/auto/community
```

#### 10.3 Multi-Surface Integration Examples
**Create:** `skills/EXAMPLES/true-multi-surface/` with 3-5 skills:
1. **python→prolog→hy pipeline**: Python preprocesses data → Prolog validates constraints → Hy optimizes weights
2. **z3→python**: Z3 solves constraint → Python formats solution
3. **datalog→python**: Datalog extracts graph facts → Python analyzes paths

Each SKILL.md must:
- Use `context["surfaces"]` in Python code
- Show data passing between surfaces in context dict
- Include comprehensive tests using injected surfaces

#### 10.4 Update ADRs
**Directory:** `docs/architecture/decisions/`  
**Action:** Bring back concise ADRs (assessment says removed in skills-library, but useful):
- 001: Multi-surface architecture rationale
- 002: Safe Python execution via asteval
- 003: Skill metadata format design
- 004: Plugin discovery mechanisms
- 005: Surface isolation vs integration trade-offs

Keep each < 200 words. Link from README.

---

## PHASE 4: RELEASE PREPARATION (1-2 hours)

### Priority 41: Branch Consolidation
**Assessment says:** `skills-library` is cleaner (-600 lines, refactored).  
**Decision point:** Merge or rebase?

**Option A - Merge skills-library into master:**
```bash
git checkout master
git merge skills-library --no-ff
# Resolve any conflicts, test
```

**Option B - Rebase master onto skills-library:**
```bash
git checkout master
git rebase skills-library
# Rewrite history but cleaner base
```

**Recommendation:** Merge skills-library → master to preserve history, then master becomes single source of truth.

**After merge:**
- Run full test suite
- Run ruff check
- Run mypy
- Verify all skills still work

---

### Priority 42: Update CHANGELOG.md
**Add unreleased section with all Phase 1-3 fixes:**

```markdown
## [0.5.0] - Unreleased

### Fixed
- **docs**: API response format mismatch (lines X-Y)
- **docs**: README test count (77→219) and coverage (81%→26%)
- **docs**: Added Z3, Datalog, Janus to surface reference
- **docs**: Added GET /search example
- **Prolog**: Fixed assertion bug in test_concurrent_mixed_surfaces
- **Types**: Added missing imports in benchmark, composer, quality_pipeline, recommender
- **Ruff**: Fixed 70 lint warnings (42 auto, 28 manual)
- **Testing**: test_concurrent_mixed_surfaces now passes

### Changed
- **Validation**: Manifest-driven thresholds fully implemented
- **Benchmark**: Mock execution replaced with real SkillExecutor integration
- **PluginManager**: Lazy loading for Z3 and Datalog surfaces
- **Documentation**: Added MULTI_SURFACE_GUIDE.md, SURFACE_DEVELOPMENT.md

### Added
- 5 new true multi-surface example skills in skills/EXAMPLES/
- Comprehensive test coverage for quality modules (benchmark, recommender, pipeline)
- Type annotations for all public APIs
```

---

### Priority 43: Tag Release v0.5.0
```bash
git tag -a v0.5.0 -m "Release v0.5.0 - Documentation fixes, type safety, multi-surface examples"
git push origin v0.5.0
```

**Pre-tag verification checklist:**
- [ ] All tests passing (219/219)
- [ ] Ruff linting passes clean (`ruff check src/ tests/`)
- [ ] MyPy passes with 0 errors (except type ignore comments)
- [ ] README badges and stats accurate
- [ ] API docs match implementation
- [ ] CHANGELOG updated
- [ ] Version in `pyproject.toml` is `0.5.0`
- [ ] No `print()` debugging left in code
- [ ] Git working tree clean (no uncommitted changes except release commit)

---

### Priority 44: Create GitHub Release
```bash
gh release create v0.5.0 \
  --title "v0.5.0 - Multi-Surface Framework Stabilization" \
  --notes "Major documentation and quality improvements:
- Fixed critical API documentation mismatch
- Corrected test count (219) and coverage (~26%)
- Added type safety across quality modules
- Created multi-surface integration guide and examples
- Lazy loading for heavy surfaces
- 219 tests passing"
```

---

### Priority 45: Publish to PyPI (if applicable)
```bash
python -m build
twine upload dist/*
```

**Note:** Only if package already published. If not, skip.

---

## WEEKLY SPRINT BREAKDOWN

### Week 1 Tasks (8-12 hours)
**Days 1-2:** Phase 1 (Immediate Stabilization)
- Day 1 AM: Fix test failure + API docs rewrite
- Day 1 PM: README updates (stats, version, surfaces)
- Day 2 AM: Ruff fix + manual lint issues
- Day 2 PM: Missing type imports (benchmark, composer, recommender, quality_pipeline)

**Deliverable:** All critical documentation and tests fixed, mypy errors reduced by 75%.

### Week 2 Tasks (8-12 hours)
**Days 3-5:** Phase 2 (Architectural Integrity) + Phase 3 start
- Day 3: Context injection verification + multi-surface skill audit
- Day 4: Create MULTI_SURFACE_GUIDE.md + update 2 problematic skills
- Day 5: Test coverage expansion (write 5-10 new tests for benchmark/recommender)

**Deliverable:** True multi-surface integration pattern documented, quality module test coverage >40%.

### Week 3 Tasks (8-10 hours)
**Days 6-7:** Phase 3 continued
- Day 6: Real benchmark implementation (replace mock)
- Day 7: Lazy loading for Z3/Datalog surfaces
- Bonus: Create 2-3 true multi-surface example skills

**Deliverable:** Benchmark runs real code, heavy surfaces load lazily, examples demonstrate integration.

### Week 4 Tasks (4-6 hours)
**Days 8-9:** Phase 4 (Release Preparation)
- Day 8: Branch consolidation (merge skills-library)
- Day 9: Full regression test suite, CHANGELOG update, tag v0.5.0

**Deliverable:** v0.5.0 tagged and released.

---

## RISK MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking API change (response format) | Users relying on old format | Keep both formats with deprecation warning OR update all docs immediately with clear migration guide |
| Type errors block mypy clean | Increases technical debt | Address incrementally, use `# type: ignore` as last resort |
| Test coverage too low to trust fixes | May introduce regressions | Add tests alongside every bug fix, focus on quality modules |
| Skills-library merge conflicts | Divergent branches may conflict | Merge soon, resolve conflicts, keep skills-library changes |
| Lazy loading breaks surface discovery | Surfaces not found when needed | Comprehensive testing of PluginManager.get() for all surfaces |

---

## SUCCESS METRICS

**Release readiness criteria:**
- [ ] 219/219 tests passing
- [ ] `ruff check` reports 0 errors
- [ ] `mypy src/` reports 0 errors (excluding optional imports)
- [ ] README test count and coverage accurate
- [ ] API documentation matches implementation 100%
- [ ] All 6 surfaces documented in README
- [ ] Multi-surface guide written and examples provided
- [ ] CHANGELOG complete for v0.5.0
- [ ] Git tag created, GitHub release published

**Quality targets:**
- Overall test coverage: 60% (realistic, not 81%)
- Type coverage: >95% of functions annotated
- Surface lazy loading: Z3/Datalog defer until first use
- Multi-surface skills: 3+ true integrated examples

---

## QUICK START COMMANDS

Initialize work:
```bash
cd D:\GitHub\projects\em-cubed
git checkout master
git pull origin master
```

Start Phase 1:
```bash
# 1. Fix the failing test
code tests/test_concurrent.py  # Edit line 54

# 2. Run tests to confirm fix
pytest tests/test_concurrent.py -v

# 3. Run ruff auto-fix
ruff check --fix src/ tests/

# 4. Update documentation (manual editing)
code README.md
code docs/api-reference.md

# 5. Type check and fix errors
mypy src/ --show-error-codes
# Then edit files to add missing imports
```

Track progress:
```bash
# Run full suite after each phase
pytest --cov=em_cubed --cov-report=term-missing
```

---

## NOTES

- **Assessment source:** `assessment.md` - comprehensive review with 626 lines of analysis
- **Branch status:** `skills-library` contains cleaner code; recommended to merge into `master`
- **Current version:** 0.5.0 declared in `__init__.py` but README says 0.4.0
- **Test count:** 219 total, 218 passing (1 Prolog bug)
- **Coverage:** ~26% actual vs 81% claimed in README
- **Multi-surface skills:** Current examples are siloed, not truly integrated
- **Type errors:** 48 MyPy errors mostly from missing imports in quality modules
- **Lint issues:** 70 Ruff errors (42 auto-fixable, 28 manual)

**Key architectural insight:** Context injection via `context["surfaces"]` is the intended pattern for cross-surface interaction, but example skills use direct imports. Fix by documenting the pattern and updating examples.

**Estimated total time:** 15-30 hours distributed across 3-4 weeks part-time.

---

**End of Implementation Plan**
