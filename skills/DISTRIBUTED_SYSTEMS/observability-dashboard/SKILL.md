---
name: observability-dashboard
domain: DISTRIBUTED_SYSTEMS
version: 1.0.0
surfaces:
- python
- sqlite
description: Multi-surface observability dashboard with Python surface for metric collection and SQLite surface for time-series
  storage and alerting. Supports configurable thresholds and stat inspection.
compatibility: PYTHON
allowed-tools: '- read

  - write

  - edit

  - bash

  - glob

  - grep

  - codebase_search

  - task

  - sequentialthinking_sequentialthinking

  - webfetch

  - websearch

  - question

  - suggest

  '
---

# Observability Dashboard

Real-time monitoring and metrics collection for distributed execution workflows.

## Purpose

Collect, aggregate, and query execution metrics for distributed systems observability.

## Description

This skill provides:
- Python: Metric aggregation, time-series analysis, alert detection
- SQLite: Persistent metrics storage and query interface

## Implementation

### Python Metrics Aggregator

```python
import time
from typing import Dict, List, Any, Optional

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, List[Any]] = {}
        self.counters: Dict[str, float] = {}

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        if name not in self.metrics:
            self.metrics[name] = []
        entry = {'value': value, 'timestamp': time.time(), 'tags': tags or {}}
        self.metrics[name].append(entry)

    def get_metric(self, name: str) -> List[Any]:
        return self.metrics.get(name, [])

    def increment_counter(self, name: str, amount: float = 1.0):
        self.counters[name] = self.counters.get(name, 0.0) + amount

    def get_counter(self, name: str) -> float:
        return self.counters.get(name, 0.0)

def calculate_average(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)

def detect_anomaly(values: List[float], threshold: float = 2.0) -> Optional[float]:
    if len(values) < 3:
        return None
    avg = calculate_average(values)
    for v in values[-5:]:
        if abs(v - avg) > threshold * avg:
            return v
    return None

def aggregate_metrics(metrics: Dict[str, List[Any]], window_seconds: int = 60) -> Dict[str, float]:
    now = time.time()
    result = {}
    for name, entries in metrics.items():
        recent = [e['value'] for e in entries if now - e['timestamp'] <= window_seconds]
        result[name] = calculate_average(recent) if recent else 0.0
    return result
```

### SQLite Metrics Store

```sql
CREATE TABLE IF NOT EXISTS execution_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT,
    step_name TEXT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    tags_json TEXT,
    timestamp REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workflow_time ON execution_metrics(workflow_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_metric_name ON execution_metrics(metric_name);

INSERT INTO execution_metrics (workflow_id, step_name, metric_name, metric_value, tags_json, timestamp)
VALUES (?, ?, ?, ?, ?, ?);

SELECT metric_name, AVG(metric_value) as avg_value
FROM execution_metrics 
WHERE workflow_id = ? AND timestamp >= ?
GROUP BY metric_name;

SELECT workflow_id, COUNT(*) as execution_count, AVG(metric_value) as avg_latency
FROM execution_metrics 
WHERE metric_name = 'execution_time' 
GROUP BY workflow_id;
```

### Alert Detection

```python
def check_threshold(metrics: Dict[str, float], thresholds: Dict[str, float]) -> List[str]:
    alerts = []
    for name, value in metrics.items():
        if name in thresholds and value > thresholds[name]:
            alerts.append(f"{name} exceeded threshold: {value} > {thresholds[name]}")
    return alerts

def detect_stale_workflows(metrics: List[Dict], threshold_seconds: int = 300) -> List[str]:
    now = time.time()
    stale = []
    for m in metrics:
        if now - m.get('timestamp', 0) > threshold_seconds:
            stale.append(m.get('workflow_id', 'unknown'))
    return stale
```

## Testing

### Unit Tests

```python
def test_metrics_collector():
    collector = MetricsCollector()
    collector.record_metric('cpu', 0.75)
    collector.increment_counter('executions', 5)
    assert collector.get_counter('executions') == 5
    assert len(collector.get_metric('cpu')) == 1

def test_aggregate_metrics():
    collector = MetricsCollector()
    collector.record_metric('latency', 0.1)
    collector.record_metric('latency', 0.2)
    collector.record_metric('latency', 0.3)
    result = aggregate_metrics({'latency': collector.metrics['latency']})
    assert result['latency'] == 0.2

def test_anomaly_detection():
    values = [0.1, 0.1, 0.1, 0.1, 1.0]
    anomaly = detect_anomaly(values, threshold=2.0)
    assert anomaly == 1.0
```

## Security Considerations

- Metrics are statistical aggregates only
- No PII or sensitive data in metrics
- SQLite for isolated storage