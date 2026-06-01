---
Domain: STATISTICS
Version: 1.0.0
Complexity: Medium
Type: Analysis
Category: Statistical Inference Skills
Estimated Execution Time: 5-15 minutes
name: statistical-bootstrap-analyzer
Source: community
surfaces:
  - python
  - prolog
  - hy

---
origin: manual
triggers:
  - bootstrap_analysis
  - confidence_intervals
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0

## Purpose

Multi-surface statistical bootstrap analyzer for confidence interval estimation, hypothesis testing.

## Implementation

### Python Bootstrap Core

```python
import numpy as np

class BootstrapAnalyzer:
    def __init__(self, data, n_bootstrap=10000):
        self.data = np.asarray(data)
        self.n_bootstrap = n_bootstrap
        self.bootstrap_samples = None

    def bootstrap_sample(self, statistic=None):
        statistic = statistic or np.mean
        self.bootstrap_samples = np.array([
            statistic(np.random.choice(self.data, size=len(self.data), replace=True))
            for _ in range(self.n_bootstrap)
        ])
        return self.bootstrap_samples

    def confidence_interval(self, alpha=0.05):
        if self.bootstrap_samples is None:
            self.bootstrap_sample()
        lower = np.percentile(self.bootstrap_samples, 100 * alpha / 2)
        upper = np.percentile(self.bootstrap_samples, 100 * (1 - alpha / 2))
        return (lower, upper)
```

### Prolog Statistical Logic

```prolog
valid_bootstrap(NObs, NBoot) :-
    NBoot >= NObs,
    NBoot =< 100000.

confidence_interval_contains(Lower, Upper, TrueValue) :-
    Lower =< TrueValue,
    TrueValue =< Upper.
```

### Hy Uncertainty Scoring

```hy
(defn bootstrap-quality [n-bootstrap n-original variance]
  (let [ratio (/ n-bootstrap n-original)]
    {:quality_score (min 1.0 (/ ratio 100))}))
```

## Testing

```python
import pytest

@pytest.mark.asyncio
async def test_bootstrap_ci():
    code = '''
import numpy as np
np.random.seed(42)
data = np.random.randn(100) * 10 + 50
boot_means = [np.mean(np.random.choice(data, 100, replace=True)) for _ in range(5000)]
lower = np.percentile(boot_means, 2.5)
upper = np.percentile(boot_means, 97.5)
lower < 50 and upper > 50
'''
    from em_cubed.surfaces import PythonSurface
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
```

## Security Considerations
- Pure numerical operations on in-memory data

## Dependencies
- numpy
- scipy