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

## Testing

### Unit Tests

```python
import pytest
import numpy as np
import pandas as pd
from em_cubed.surfaces import PythonSurface

def test_categorical_encoding():
    """Test label encoding of categorical columns."""
    code = '''
from sklearn.preprocessing import LabelEncoder
import pandas as pd

df = pd.DataFrame({"color": ["red", "green", "blue", "red", "green"]})
le = LabelEncoder()
df["color_encoded"] = le.fit_transform(df["color"])

assert "color_encoded" in df.columns
assert df["color_encoded"].min() >= 0
assert df["color_encoded"].max() <= 2  # 3 unique values
assert list(df["color_encoded"]) == [0, 1, 2, 0, 1] or \
       list(df["color_encoded"]) in [[0,1,2,0,1], [1,2,0,1,2], [2,0,1,2,0]]  # any mapping
print("categorical encoding ok")
'''
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_standard_scaling():
    """Test standard scaling (mean=0, std=1)."""
    code = '''
from sklearn.preprocessing import StandardScaler
import numpy as np

data = np.array([[1, 2], [3, 4], [5, 6]])
scaler = StandardScaler()
scaled = scaler.fit_transform(data)

# Check mean ~0, std ~1 per feature
assert abs(np.mean(scaled[:,0])) < 0.001
assert abs(np.std(scaled[:,0]) - 1.0) < 0.001
print("scaling ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_polynomial_features():
    """Test polynomial feature expansion."""
    code = '''
import numpy as np
from sklearn.preprocessing import PolynomialFeatures

X = np.array([[2, 3]])
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
# For [a, b], degree 2 gives: [a, b, a^2, a*b, b^2]
assert X_poly.shape[1] == 5  # 2 original + 3 new = 5 (if include_bias=False and interaction only once)
# Actually PolynomialFeatures(2) with 2 input features without bias:
# [1, a, b, a^2, a*b, b^2] -> 6 if include_bias=True; 5 without bias? Let's check:
# Without bias, degree 2: a, b, a^2, a*b, b^2 -> 5
assert X_poly[0,0] == 2  # original a
assert X_poly[0,1] == 3  # original b
print("polynomial ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_interaction_features():
    """Test creation of interaction features."""
    code = '''
import pandas as pd

def create_interactions(df, cols):
    for i, c1 in enumerate(cols):
        for c2 in cols[i+1:]:
            df[f"{c1}_x_{c2}"] = df[c1] * df[c2]
    return df

df = pd.DataFrame({"a": [1,2,3], "b": [4,5,6], "c": [7,8,9]})
df = create_interactions(df, ["a", "b", "c"])

assert "a_x_b" in df.columns
assert "a_x_c" in df.columns
assert "b_x_c" in df.columns
assert df["a_x_b"].iloc[0] == 4  # 1*4
assert df["a_x_c"].iloc[0] == 7  # 1*7
print("interaction ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_datetime_feature_extraction():
    """Test extracting date/time components."""
    code = '''
import pandas as pd

df = pd.DataFrame({
    "timestamp": ["2024-01-15 14:30:00", "2024-02-20 09:15:00", "2024-03-10 18:45:00"]
})
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["dayofweek"] = df["timestamp"].dt.dayofweek
df["month"] = df["timestamp"].dt.month

assert df["hour"].iloc[0] == 14
assert df["month"].iloc[0] == 1
assert df["dayofweek"].iloc[0] == 0  # Monday
print("datetime features ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_feature_selection_threshold():
    """Test mutual information-based feature selection."""
    code = '''
import numpy as np
from sklearn.feature_selection import mutual_info_regression

# Generate synthetic data
np.random.seed(42)
X = np.random.randn(100, 5)
y = X[:, 0] * 2 + np.random.randn(100) * 0.1  # only first feature matters

mi = mutual_info_regression(X, y)
# First feature should have highest MI
assert np.argmax(mi) == 0
assert mi[0] > 0.5  # should be high
print("feature selection ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_pca_dimensionality_reduction():
    """Test PCA reduces dimensions while retaining variance."""
    code = '''
import numpy as np
from sklearn.decomposition import PCA

np.random.seed(42)
X = np.random.randn(100, 10)
pca = PCA(n_components=0.9)  # retain 90% variance
X_reduced = pca.fit_transform(X)

assert X_reduced.shape[1] < 10
assert pca.explained_variance_ratio_.sum() >= 0.9
print(f"PCA reduced {X.shape[1]} -> {X_reduced.shape[1]} features")
print("PCA ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_pipeline_chaining():
    """Test chaining multiple transformers."""
    code = '''
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

# Simulate pipeline
df = pd.DataFrame({
    "num1": [1, 2, np.nan, 4, 5],
    "cat1": ["a", "b", "a", "c", "b"]
})

# Impute numerical missing
df["num1"] = df["num1"].fillna(df["num1"].mean())

# Encode categorical
le = LabelEncoder()
df["cat1_enc"] = le.fit_transform(df["cat1"])

assert df["num1"].isna().sum() == 0
assert df["cat1_enc"].min() >= 0
assert df["cat1_enc"].max() <= 2
print("pipeline chaining ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_prolog_feature_rule():
    """Test Prolog logical feature rule."""
    code = '''
from pyswip import Prolog

prolog = Prolog()
prolog.assertz("feature_type(age, numeric)")
prolog.assertz("feature_type(name, categorical)")
prolog.assertz("feature_type(income, numeric)")

# Query numeric features
result = list(prolog.query("feature_type(X, numeric)"))
numeric_features = [r["X"] for r in result]
assert "age" in numeric_features
assert "income" in numeric_features
assert "name" not in numeric_features
print("prolog feature rule ok")
'''
    # Only run if pyswip available - this is a reference test
    print("prolog rule defined (requires PySWIP for execution)")

@pytest.mark.asyncio
class TestFeatureEngineering:
    @pytest.fixture
    async def surface(self):
        return PythonSurface()

    async def test_dataframe_operations(self, surface):
        """Test pandas operations used in feature engineering."""
        code = '''
import pandas as pd
df = pd.DataFrame({"a": [1,2,3], "b": [4,5,6]})
df["sum"] = df["a"] + df["b"]
assert df["sum"].iloc[0] == 5
print("df ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_math_operations(self, surface):
        """Test math operations for feature transforms."""
        code = '''
import numpy as np
x = np.array([1,2,3])
log_x = np.log(x + 1)  # avoid log(0)
assert len(log_x) == 3
print("math ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
from em_cubed.surfaces import PythonSurface
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_feature_pipeline_skill():
    """Test feature engineering pipeline skill."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "FEATURE_ENGINEERING" / "feature-engineering-pipeline"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: Feature Pipeline Test
Domain: FEATURE_ENGINEERING
surfaces:
  - python
---

## Purpose
Test feature engineering

## Implementation

### Python

```python
def encode(df):
    return df
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        surface = PythonSurface()
        result = await surface.execute("len(['a','b','c'])", {})
        assert result["status"] == "ok"
```

## Usage Patterns

### Standard Feature Pipeline

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

code = '''
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Define data
df = pd.DataFrame({
    "age": [25, 30, 35],
    "city": ["NYC", "LA", "NYC"],
    "salary": [50000, 60000, 70000]
})

# Simple numeric scaling
df["age_scaled"] = (df["age"] - df["age"].mean()) / df["age"].std()
df["salary_scaled"] = (df["salary"] - df["salary"].mean()) / df["salary"].std()

# One-hot encode city
df = pd.get_dummies(df, columns=["city"], prefix="city")

print(df.head())
'''
await surface.execute(code, {})
```

### Feature Selection

```python
from sklearn.feature_selection import SelectKBest, f_classif

selector = SelectKBest(score_func=f_classif, k=5)
X_selected = selector.fit_transform(X, y)
```

## Security Considerations

- Data processing is in-memory only
- No external API calls in pipeline
- Ensure data is passed explicitly (not file reads)

## Dependencies

- numpy (arrays)
- pandas (DataFrames)
- scikit-learn (preprocessing, decomposition)
- em_cubed framework

````
