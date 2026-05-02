---
Domain: FEATURE_ENGINEERING
Version: 1.0.0
Complexity: Medium
Type: Pipeline
Category: ML Skills
Estimated Execution Time: 5-10 minutes
name: feature-engineering-pipeline
Source: community
---
origin: manual
triggers:
  - feature_engineering
  - preprocessing
  - data_transformation
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:01:00Z"
updated_at: "2026-05-02T13:01:00Z"

## Purpose

Multi-surface feature engineering pipeline with Python for transformations, Prolog for logical feature rules, and Hy for feature importance scoring.

## Implementation

### Python Feature Pipeline

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Callable, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA

class FeaturePipeline:
    def __init__(self):
        self.transformers = {}
        self.feature_names = []
    
    def add_transformer(self, name: str, func: Callable) -> None:
        self.transformers[name] = func
    
    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        result = df.copy()
        for name, transformer in self.transformers.items():
            result = transformer.fit_transform(result) if hasattr(transformer, "fit_transform") else transformer(result)
        return result
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        encoders = {}
        for col in df.select_dtypes(include=["object"]).columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        return df

def polynomial_features(X: np.ndarray, degree: int = 2) -> np.ndarray:
    from sklearn.preprocessing import PolynomialFeatures
    poly = PolynomialFeatures(degree)
    return poly.fit_transform(X)

def interaction_features(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for i, c1 in enumerate(cols):
        for c2 in cols[i+1:]:
            df[f"{c1}_x_{c2}"] = df[c1] * df[c2]
    return df

def datetime_features(df: pd.DataFrame, datetime_col: str) -> pd.DataFrame:
    df[datetime_col] = pd.to_datetime(df[datetime_col])
    df["hour"] = df[datetime_col].dt.hour
    df["dayofweek"] = df[datetime_col].dt.dayofweek
    df["month"] = df[datetime_col].dt.month
    return df
```

### Prolog Feature Logic

```prolog
% Feature validity
valid_feature(Column, Data) :-
    no_missing_values(Column, Data),
    reasonable_range(Column, Data).

% Feature interaction
feature_interaction(F1, F2, CombinedFeature) :-
    correlated(F1, F2, Correlation),
    Correlation > 0.5,
    CombinedFeature is F1 * F2.

% Feature selection
informative_feature(Feature, Target, Threshold) :-
    mutual_information(Feature, Target, MI),
    MI > Threshold.

% Data quality
data_quality(Column, Score) :-
    missing_percentage(Column, Missing),
    unique_ratio(Column, Ratio),
    Score is 1.0 - Missing - (1 - Ratio).
```

### Hy Feature Scoring

```hy
(defn feature-complexity [feature-values]
  "Measure feature complexity"
  (let [unique-count (len (set feature-values))
        entropy (- (sum (map (fn [v] (* v (numpy.log v))) 
                         (normalize (count-values feature-values)))))]
    entropy))

(defn normalization-method [feature-distribution]
  "Choose normalization based on distribution"
  (let [skewness (numpy.mean (map (fn [x] (** (- x) 3)) feature-distribution))]
    (if (> (abs skewness) 1) "robust" "standard")))

(defn feature-pipeline-optimization [current-score]
  "Optimize pipeline based on scores"
  (if (< current-score 0.5)
      ["remove_low_variance" "add_polynomial" "select_k_best"]
      ["pca" "scaling"]))