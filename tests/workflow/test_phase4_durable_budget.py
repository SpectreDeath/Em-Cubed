"""Unit tests for Phase 4: Durable execution checkpointing & Budget circuit breaker."""

import tempfile
from pathlib import Path

from em_cubed.telemetry.budget_circuit_breaker import BudgetCircuitBreaker, CircuitState
from em_cubed.workflow.durable_execution import DurableExecutionManager


def test_durable_execution_checkpointing():
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "checkpoints.db"
        mgr = DurableExecutionManager(db_path=db_path)

        # Save step checkpoints
        ok1 = mgr.save_step_checkpoint("wf1", "step1", "completed", {"result": 42})
        ok2 = mgr.save_step_checkpoint("wf1", "step2", "running", {})
        assert ok1 is True
        assert ok2 is True

        # Retrieve completed steps for resume recovery
        completed = mgr.get_completed_steps("wf1")
        assert "step1" in completed
        assert completed["step1"]["output"]["result"] == 42
        assert "step2" not in completed  # step2 was 'running', not 'completed'


def test_budget_circuit_breaker():
    cb = BudgetCircuitBreaker(max_budget_dollars=5.0)

    # Initial state
    assert cb.state == CircuitState.CLOSED
    res = cb.check_execution_allowed("llm")
    assert res["allowed"] is True

    # Record cost under threshold
    cb.record_cost(3.0)
    assert cb.state == CircuitState.CLOSED

    # Record cost exceeding threshold
    cb.record_cost(2.5)
    assert cb.state == CircuitState.OPEN

    # Verify execution block for expensive LLM surface with fallback
    res_blocked = cb.check_execution_allowed("llm")
    assert res_blocked["allowed"] is False
    assert res_blocked["recommended_fallback"] == "python"

    # Reset
    cb.reset()
    assert cb.state == CircuitState.CLOSED
