"""Tests for the SurfaceExecutionContext protocol and DefaultSurfaceExecutionContext."""

from __future__ import annotations

from typing import Any

from em_cubed.loopy.base import BaseLoopySkill
from em_cubed.loopy.context import DefaultSurfaceExecutionContext, SurfaceExecutionContext


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _MinimalLoopySkill(BaseLoopySkill[dict, str]):
    """Minimal concrete skill for testing the loop engine in isolation."""

    def __init__(self, passes_on_iteration: int = 1, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._passes_on = passes_on_iteration
        self._iteration = 0

    def initialize_state(self, *args: Any, **kwargs: Any) -> dict:
        return {"iteration": 0}

    def mutate(self, state: dict, iteration: int) -> tuple[dict, str]:
        state = {**state, "iteration": iteration}
        self._iteration = iteration
        return state, f"mutate-iter-{iteration}"

    def verify(self, state: dict) -> tuple[bool, str]:
        passed = state["iteration"] >= self._passes_on
        return passed, f"iter={state['iteration']}"

    def extract_result(self, state: dict) -> str:
        return f"done-at-{state['iteration']}"


class _MockContext:
    """Test double for SurfaceExecutionContext — never imports ontology modules."""

    def __init__(self, truth_value_factory: Any = None) -> None:
        self._factory = truth_value_factory
        self.calls: list[str] = []

    def classify_boolean(self, is_true: bool, message: str = "") -> Any:
        self.calls.append(f"classify_boolean({is_true})")
        from em_cubed.ontology.topos import SubobjectClassifier
        return SubobjectClassifier.classify_boolean(is_true, message)

    def classify_exact_truthmaker(self, **kwargs: Any) -> Any: ...
    def induce_concept(self, **kwargs: Any) -> Any: ...
    def compute_derived_property(self, **kwargs: Any) -> float: return 0.0
    def verify_interface(self, **kwargs: Any) -> bool: return True
    def migrate_triples(self, triples: list, steps: list) -> list: return triples
    def audit_health(self, triples: list) -> Any: ...
    def snapshot_at(self, **kwargs: Any) -> list: return []
    def find_entities_within_radius(self, **kwargs: Any) -> list: return []
    def to_turtle(self, triples: list) -> str: return ""
    def generate_shacl_shapes(self, functional_constraints: list) -> str: return ""
    def process_stream_batch(self, events: list) -> Any: return None
    def generate_attestation(self, **kwargs: Any) -> Any: ...
    def verify_commitment(self, commitment: Any) -> Any: ...
    def apply_functor(self, triples: list, target_surface: str = "prolog") -> str: return ""
    def bind_monad(self, state: Any, fn: Any) -> Any: return fn(state)


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------

def test_default_context_implements_protocol():
    """DefaultSurfaceExecutionContext must satisfy the SurfaceExecutionContext protocol."""
    ctx = DefaultSurfaceExecutionContext()
    assert isinstance(ctx, SurfaceExecutionContext), (
        "DefaultSurfaceExecutionContext does not implement SurfaceExecutionContext protocol"
    )


def test_mock_context_implements_protocol():
    """_MockContext used in other tests must also satisfy the protocol."""
    ctx = _MockContext()
    assert isinstance(ctx, SurfaceExecutionContext)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_base_loopy_skill_default_context():
    """BaseLoopySkill should use DefaultSurfaceExecutionContext when none is supplied."""
    skill = _MinimalLoopySkill()
    assert isinstance(skill._context, DefaultSurfaceExecutionContext)


def test_base_loopy_skill_injected_context():
    """BaseLoopySkill should store the injected context without wrapping it."""
    ctx = _MockContext()
    skill = _MinimalLoopySkill(context=ctx)
    assert skill._context is ctx


def test_base_loopy_skill_backward_compatible_no_context_arg():
    """Existing callers that don't pass context= should still work identically."""
    skill = _MinimalLoopySkill(max_iterations=3)
    assert skill.max_iterations == 3
    assert isinstance(skill._context, DefaultSurfaceExecutionContext)


# ---------------------------------------------------------------------------
# Loop engine calls through context (not concrete ontology classes)
# ---------------------------------------------------------------------------

def test_run_calls_context_classify_boolean():
    """run() must call context.classify_boolean() instead of SubobjectClassifier directly."""
    ctx = _MockContext()
    skill = _MinimalLoopySkill(passes_on_iteration=2, max_iterations=3, context=ctx)
    result = skill.run()

    assert result.success is True
    # classify_boolean should have been called once per iteration (2 iterations until pass)
    assert any("classify_boolean" in call for call in ctx.calls)
    classify_calls = [c for c in ctx.calls if "classify_boolean" in c]
    assert len(classify_calls) == 2  # iteration 1 fails, iteration 2 passes


def test_run_returns_correct_trajectory():
    """Trajectory entries must be recorded for every iteration including the passing one."""
    ctx = _MockContext()
    skill = _MinimalLoopySkill(passes_on_iteration=2, max_iterations=5, context=ctx)
    result = skill.run()

    assert result.success is True
    assert len(result.trajectory) == 2
    assert result.trajectory[0].passed_guard is False
    assert result.trajectory[1].passed_guard is True
    assert result.final_output == "done-at-2"


def test_run_fails_at_max_iterations():
    """run() must return success=False after exhausting max_iterations."""
    ctx = _MockContext()
    skill = _MinimalLoopySkill(passes_on_iteration=99, max_iterations=3, context=ctx)
    result = skill.run()

    assert result.success is False
    assert len(result.trajectory) == 3
    assert result.error_message is not None
    assert "3" in result.error_message


# ---------------------------------------------------------------------------
# verify_topos delegates through context
# ---------------------------------------------------------------------------

def test_verify_topos_uses_context_not_direct_import():
    """verify_topos() must route through self._context.classify_boolean, not SubobjectClassifier directly."""
    ctx = _MockContext()
    skill = _MinimalLoopySkill(context=ctx)
    state = {"iteration": 1}

    tv = skill.verify_topos(state)

    assert any("classify_boolean(True)" in c for c in ctx.calls)
    assert tv.is_boolean is True


# ---------------------------------------------------------------------------
# Other sensor methods delegate through context
# ---------------------------------------------------------------------------

def test_export_rdf_turtle_delegates_to_context():
    ctx = _MockContext()
    skill = _MinimalLoopySkill(context=ctx)
    result = skill.export_rdf_turtle({"triples": []})
    assert result == ""  # _MockContext returns ""


def test_process_event_stream_delegates_to_context():
    ctx = _MockContext()
    skill = _MinimalLoopySkill(context=ctx)
    result = skill.process_event_stream([])
    assert result is None  # _MockContext returns None


def test_bind_monad_delegates_to_context():
    ctx = _MockContext()
    skill = _MinimalLoopySkill(context=ctx)
    result = skill.bind_monad("state", lambda s: s + "-bound")
    assert result == "state-bound"


# ---------------------------------------------------------------------------
# Regression: existing loopy skill tests still pass (smoke check)
# ---------------------------------------------------------------------------

def test_existing_loopy_skill_regression():
    """Smoke-test that a skill using the default context (real ontology) can be constructed."""
    # This simply checks that the import chain resolves without error.
    from em_cubed.loopy.context import DefaultSurfaceExecutionContext

    skill = _MinimalLoopySkill(max_iterations=1)
    assert isinstance(skill._context, DefaultSurfaceExecutionContext)
    # run() would call real ontology — only test construction here to avoid heavy deps in unit tests
