"""Tests for PolyglotWorker process."""

from em_cubed.workflow.worker import PolyglotWorker


def test_polyglot_worker_init_and_clean_run():
    worker = PolyglotWorker(surfaces=["python", "polars"], skills_dir="skills")
    assert "polars" in worker.surfaces
    # Execute single poll iteration
    worker.run(poll_interval=0.01, max_tasks=1)
