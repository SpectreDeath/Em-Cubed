# Skill Summary Card: `dual-engine-benchmark-agent`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        dual-engine-benchmark-agent               │
│ Category:    ONTOLOGY / CI/CD Benchmark Profiler       │
│ Invocation:  /dual-engine-benchmark-agent              │
│ Trigger:     "run ontology benchmark", "benchmark tps",│
│              "profile zkp latency", "functor benchmark"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Continuous integration performance and    │
│              latency profiling across validation,      │
│              ZKP generation, and surface functors.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Load Invariant** | Ingest load parameters & init hardware timers | Benchmark Run Config | High-precision timers initialized |
| **2. Graph Gen** | Generate synthetic test triples with DL rules | Synthetic Graph Store | Test graph populated in memory |
| **3. Visual Brief** | Render throughput & latency distribution charts | `%TEMP%\benchmark-brief-*.html`| Dark theme HTML benchmark brief |
| **4. Checkpoint** | Validate system memory & thermal limits | Safety Gate Record | Memory availability certified |
| **5. Timed Execution**| Measure $\mu\text{s}$ durations & assert SLAs | Final Benchmark Report | `benchmark_passed: true` against SLAs |

---

## Invariants & Guardrails

- [ ] **High-Precision Timers**: Must use `time.perf_counter()` or microsecond resolution.
- [ ] **SLA Assertion**: Automatic failure if throughput drops below 1,000 TPS or ZKP verify exceeds 1.0 ms.
- [ ] **Warmup Passes**: Minimum 3 warmup runs before recording official benchmark numbers.
