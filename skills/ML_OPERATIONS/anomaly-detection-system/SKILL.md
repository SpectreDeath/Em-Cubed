---
Domain: ML_OPERATIONS
Version: 1.0.0
Complexity: Medium
Type: Analysis
Category: Monitoring Skills
Estimated Execution Time: 2-5 minutes
name: anomaly-detection-system
Source: community
---
origin: manual
triggers:
  - anomaly_detection
  - monitoring
  - outlier_analysis
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:00:00Z"
updated_at: "2026-05-02T13:00:00Z"

## Purpose

Multi-surface anomaly detection system that uses Python for statistical methods and ML, Prolog for logical anomaly rules, and Hy for fuzzy anomaly scoring and temporal pattern detection.

## Description

This skill detects anomalies by:
- Python for statistical detection, isolation forests, and reconstruction error
- Prolog for logical anomaly rules and business constraint validation
- Hy for fuzzy anomaly confidence and adaptive threshold adjustment

## Implementation

### Python Anomaly Detection

```python
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AnomalyDetector:
    """Multi-method anomaly detection."""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=contamination)
    
    def fit(self, X: np.ndarray) -> None:
        """Fit the detector."""
        X_scaled = self.scaler.fit_transform(X)
        self.isolation_forest.fit(X_scaled)
    
    def detect(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies, return predictions and scores."""
        X_scaled = self.scaler.transform(X)
        predictions = self.isolation_forest.predict(X_scaled)
        scores = self.isolation_forest.decision_function(X_scaled)
        return predictions, scores
    
    def statistical_zscore(self, X: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Z-score based anomaly detection."""
        mean = np.mean(X, axis=0)
        std = np.std(X, axis=0) + 1e-10
        z_scores = np.abs((X - mean) / std)
        return (z_scores > threshold).any(axis=1)
    
    def statistical_iqr(self, X: np.ndarray, k: float = 1.5) -> np.ndarray:
        """IQR-based anomaly detection."""
        q1 = np.percentile(X, 25, axis=0)
        q3 = np.percentile(X, 75, axis=0)
        iqr = q3 - q1
        lower = q1 - k * iqr
        upper = q3 + k * iqr
        return ((X < lower) | (X > upper)).any(axis=1)

def reconstruction_error_anomaly(autoencoder, X: np.ndarray, 
                                 threshold_percentile: float = 95) -> np.ndarray:
    """Use autoencoder reconstruction error for anomaly detection."""
    reconstructed = autoencoder.predict(X)
    errors = np.mean((X - reconstructed) ** 2, axis=1)
    threshold = np.percentile(errors, threshold_percentile)
    return errors > threshold

def temporal_anomaly_detection(time_series: np.ndarray, 
                               window_size: int = 30) -> np.ndarray:
    """Detect temporal anomalies using rolling statistics."""
    mean = np.convolve(time_series, np.ones(window_size)/window_size, mode='valid')
    std = np.array([np.std(time_series[i:i+window_size]) 
                    for i in range(len(time_series) - window_size + 1)])
    
    anomalies = np.abs(time_series[window_size-1:] - mean) > (3 * std + 1e-10)
    result = np.zeros(len(time_series), dtype=bool)
    result[window_size-1:] = anomalies
    return result
```

### Prolog Anomaly Logic

```prolog
% Anomaly definition
anomaly(DataPoint, Type) :-
    outside_normal_range(DataPoint, Upper, Lower),
    classify_anomaly(Type).

% Statistical anomaly
outside_normal_range(Value, Mean, Std, Threshold) :-
    abs(Value - Mean) > (Threshold * Std).

% Pattern anomaly
pattern_anomaly(Sequence, Pattern) :-
    expected_pattern(Sequence, Expected),
    deviation(Sequence, Expected, Deviation),
    Deviation > threshold.

% Business rule anomaly
business_anomaly(Transaction, Violation) :-
    transaction(Transaction),
    violates_rule(Transaction, Violation).

% Context anomaly
contextual_anomaly(DataPoint, Context) :-
    normal_for_context(DataPoint, NormalContext),
    Context \= NormalContext.

% Correlation anomaly
correlated_anomalies(Point1, Point2, ExpectedCorrelation) :-
    feature_correlation(Point1, Point2, Actual),
    abs(Actual - ExpectedCorrelation) > 0.5.

% Aggregation anomaly
aggregation_anomaly(Batch, ExpectedStats) :-
    batch_statistics(Batch, Stats),
    deviation_from_expected(Stats, ExpectedStats, Deviation),
    Deviation > threshold.
```

### Hy Fuzzy Scoring

```hy
(defn fuzzy-anomaly-score [statistical-score reconstruction-score contextual-score]
  "Combine multiple anomaly signals using fuzzy logic"
  (let [weighted-sum (+ (* statistical-score 0.4)
                        (* reconstruction-score 0.3)
                        (* contextual-score 0.3))
        normalized-score (/ weighted-sum 3)]
    normalized-score))

(defn temporal-anomaly-confidence [detection-history window]
  "Compute confidence based on temporal consistency"
  (let [recent-detections (take window detection-history)
        consistency-rate (/ (sum recent-detections) (len recent-detections))]
    consistency-rate))

(defn adaptive-threshold [historical-data current-anomalies]
  "Adjust threshold based on recent anomaly rate"
  (let [current-rate (/ (sum current-anomalies) (len current-anomalies))
        target-rate 0.05
        adjustment-factor (- 1 (- current-rate target-rate))]
    adjustment-factor))

(defn anomaly-clustering [anomalies feature-weights]
  "Group similar anomalies using fuzzy clustering"
  (let [distances (map (fn [a1]
                        (map (fn [a2] (euclidean-distance a1 a2 feature-weights))
                             anomalies))
                      anomalies)
        clusters (fuzzy-cmeans distances 3)]
    clusters))

(defn severity-composition [impact probability detectability]
  "Compose severity score from multiple factors"
  (let [severity (/ (+ (* impact 0.5) (* probability 0.3) (* detectability 0.2)) 3)]
    severity))
```

## Testing

```python
# Test anomaly detection
from skills.anomaly_detection_system import AnomalyDetector
import numpy as np

detector = AnomalyDetector(contamination=0.1)
X = np.random.randn(100, 5)
X[50] = [10, 10, 10, 10, 10]  # Anomaly

detector.fit(X[:80])
predictions, scores = detector.detect(X[80:])
assert len(predictions) == 20
```