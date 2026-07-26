"""Unit tests for Dual-Engine Integration Benchmarks Engine."""

from em_cubed.benchmarks.dual_engine_benchmark import DualEngineBenchmarkRunner


def test_dual_engine_benchmark_run():
    report = DualEngineBenchmarkRunner.run_benchmark(num_triples=20)
    assert report.total_triples_evaluated == 20
    assert report.triple_throughput_tps > 0.0
    assert report.zkp_generation_ms >= 0.0
    assert report.zkp_verification_ms >= 0.0
    assert report.functor_transformation_ms >= 0.0
    assert report.coherence_score == 1.0
    assert "tps" in report.metrics_summary
