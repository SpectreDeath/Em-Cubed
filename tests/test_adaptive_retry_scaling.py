"""
Unit Tests for Adaptive Task Retries and Worker Pool Scaling in em-cubed
=========================================================================
Tests AdaptiveWorkerPool calculation and DistributedExecutor exponential retries.
"""

from __future__ import annotations

import time
import pytest

from em_cubed.workflow.distributed import (
    AdaptiveWorkerPool,
    DistributedTask,
    ProcessDistributedExecutor,
    TaskStatus,
)


class TestAdaptiveRetryScaling:
    """Test AdaptiveWorkerPool and retry handling."""

    def test_adaptive_worker_pool_calculation(self):
        pool = AdaptiveWorkerPool(min_workers=2, max_workers=8)
        optimal = pool.calculate_optimal_workers()

        assert isinstance(optimal, int)
        assert 2 <= optimal <= 8

    def test_task_retry_state_transition(self, tmp_path):
        executor = ProcessDistributedExecutor(skills_dir=tmp_path, max_workers=2)

        task = DistributedTask(
            task_id="failing_task",
            skill_id="non_existent_skill",
            max_retries=2,
        )
        executor._tasks[task.task_id] = task

        # Simulate task failure callback
        class MockFuture:
            def result(self):
                return {"success": False, "error": "Simulated failure"}

        executor._task_completed_callback("failing_task", MockFuture())

        assert task.status == TaskStatus.RETRYING
        assert task.retry_count == 1

        # Wait for reset timer
        time.sleep(0.25)
        assert task.status == TaskStatus.PENDING
