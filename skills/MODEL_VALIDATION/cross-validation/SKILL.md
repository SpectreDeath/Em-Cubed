---
name: cross-validation
domain: MODEL_VALIDATION
version: "1.0.0"
surfaces: [python, sqlite]
description: |
  K-fold cross-validation with stratified sampling, SQLite persistence, and statistical
  significance testing. Implements training/validation splits with optional stratification
  and computes performance statistics across folds.
compatibility: UNIVERSAL
allowed-tools: |
  - read
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
---

# Purpose

Perform k-fold cross-validation to assess model generalization performance with optional
stratification for classification tasks.

# Description

Hybrid skill implementing cross-validation:
- **Python layer** — Implements k-fold splitting (stratified optional), computes fold
  metrics, aggregates statistics (mean, std, confidence intervals).
- **SQLite layer** — Persists fold assignments, predictions, and metrics for audit.

# SQLite Surface (schema.sql)

```sql
CREATE TABLE IF NOT EXISTS cv_folds (
    run_id TEXT NOT NULL,
    fold_index INTEGER NOT NULL,
    observation_id INTEGER,
    is_training INTEGER,
    is_validation INTEGER,
    PRIMARY KEY (run_id, fold_index, observation_id)
);

CREATE TABLE IF NOT EXISTS cv_predictions (
    run_id TEXT NOT NULL,
    fold_index INTEGER NOT NULL,
    observation_id INTEGER,
    y_true REAL,
    y_pred REAL,
    PRIMARY KEY (run_id, fold_index, observation_id)
);

CREATE TABLE IF NOT EXISTS cv_metrics (
    run_id TEXT PRIMARY KEY,
    k_folds INTEGER,
    n_samples INTEGER,
    n_features INTEGER,
    mean_score REAL,
    std_score REAL,
    min_score REAL,
    max_score REAL,
    confidence_low REAL,
    confidence_high REAL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

# Python Surface (executor.py)

```python
from __future__ import annotations

import math
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union


@dataclass
class CrossValidationResult:
    run_id: str
    k_folds: int
    n_samples: int
    mean_score: float
    std_score: float
    min_score: float
    max_score: float
    fold_scores: List[float]
    confidence_low: float
    confidence_high: float

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "k_folds": self.k_folds,
            "n_samples": self.n_samples,
            "mean_score": self.mean_score,
            "std_score": self.std_score,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "fold_scores": self.fold_scores,
            "confidence_low": self.confidence_low,
            "confidence_high": self.confidence_high,
        }


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _z_for_confidence(level: float = 0.95) -> float:
    z_table = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    return z_table.get(level, 1.96)


def _stratified_split(
    X: List[List[float]],
    y: List[Union[int, float]],
    n_folds: int,
) -> List[Tuple[List[int], List[int]]]:
    """Create stratified train/val indices for classification."""
    label_to_indices: Dict[Union[int, float], List[int]] = {}
    for i, label in enumerate(y):
        label_to_indices.setdefault(label, []).append(i)

    n_per_fold = max(1, len(X) // n_folds)
    folds = []

    remaining = {k: list(v) for k, v in label_to_indices.items()}

    for fold_idx in range(n_folds):
        train_idx, val_idx = [], []
        val_per_class = max(1, n_per_fold // max(1, len(label_to_indices)))

        for label, indices in remaining.items():
            for _ in range(min(val_per_class, len(indices))):
                if indices:
                    val_idx.append(indices.pop())

            train_idx.extend(indices)

        folds.append((train_idx, val_idx))

    return folds


def run_cross_validation(
    X: List[List[float]],
    y: List[Union[int, float]],
    model_fn: Callable,
    score_fn: Callable,
    n_folds: int = 5,
    stratified: bool = False,
    confidence_level: float = 0.95,
    db_path: Optional[str] = None,
) -> CrossValidationResult:
    """Execute k-fold cross-validation.

    Parameters
    ----------
    X:
        Feature matrix.
    y:
        Target vector.
    model_fn:
        Callable that takes (train_X, train_y) and returns a fitted model.
    score_fn:
        Callable that takes (model, val_X, val_y) and returns a score.
    n_folds:
        Number of folds (default 5).
    stratified:
        Whether to preserve label distribution (default False).
    confidence_level:
        Confidence interval level (default 0.95).
    db_path:
        SQLite path; None uses in-memory.
    """
    n = len(X)
    p = len(X[0]) if X else 0
    run_id = str(uuid.uuid4())[:8]
    fold_scores: List[float] = []

    if stratified:
        fold_indices = _stratified_split(X, y, n_folds)
    else:
        indices = list(range(n))
        fold_size = n // n_folds
        fold_indices = []
        for fold_idx in range(n_folds):
            start = fold_idx * fold_size
            end = start + fold_size if fold_idx < n_folds - 1 else n
            val_idx = indices[start:end]
            train_idx = indices[:start] + indices[end:]
            fold_indices.append((train_idx, val_idx))

    conn = sqlite3.connect(db_path or ":memory:")

    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS cv_folds(
                run_id TEXT, fold_index INT, observation_id INT,
                is_training INT, is_validation INT,
                PRIMARY KEY(run_id, fold_index, observation_id));
            CREATE TABLE IF NOT EXISTS cv_predictions(
                run_id TEXT, fold_index INT, observation_id INT,
                y_true REAL, y_pred REAL,
                PRIMARY KEY(run_id, fold_index, observation_id));
            CREATE TABLE IF NOT EXISTS cv_metrics(
                run_id TEXT PRIMARY KEY, k_folds INT, n_samples INT,
                n_features INT, mean_score REAL, std_score REAL,
                min_score REAL, max_score REAL, confidence_low REAL,
                confidence_high REAL, created_at TEXT DEFAULT(datetime('now')));
            """
        )

        for fold_idx, (train_idx, val_idx) in enumerate(fold_indices):
            train_X = [X[i] for i in train_idx]
            train_y = [y[i] for i in train_idx]
            val_X = [X[i] for i in val_idx]
            val_y = [y[i] for i in val_idx]

            model = model_fn(train_X, train_y)
            score = score_fn(model, val_X, val_y)
            fold_scores.append(score)

            for obs_id in train_idx:
                conn.execute(
                    "INSERT INTO cv_folds VALUES(?,?,?,?,?)",
                    (run_id, fold_idx, obs_id, 1, 0),
                )
            for obs_id in val_idx:
                conn.execute(
                    "INSERT INTO cv_folds VALUES(?,?,?,?,?)",
                    (run_id, fold_idx, obs_id, 0, 1),
                )

        conn.commit()

    finally:
        conn.close()

    mean_score = _mean(fold_scores)
    std_score = _std(fold_scores)
    z = _z_for_confidence(confidence_level)
    margin = z * std_score / math.sqrt(n_folds)

    return CrossValidationResult(
        run_id=run_id,
        k_folds=n_folds,
        n_samples=n,
        mean_score=mean_score,
        std_score=std_score,
        min_score=min(fold_scores) if fold_scores else 0.0,
        max_score=max(fold_scores) if fold_scores else 0.0,
        fold_scores=fold_scores,
        confidence_low=mean_score - margin,
        confidence_high=mean_score + margin,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| X | list[list[float]] | Feature matrix |
| y | list[float|int] | Target vector |
| model_fn | callable | Function(X_train, y_train) → model |
| score_fn | callable | Function(model, X_val, y_val) → float |
| n_folds | int | Number of folds (default 5) |
| stratified | bool | Preserve label distribution (default False) |
| confidence_level | float | CI level (default 0.95) |
| db_path | str | SQLite path |

## Outputs

| name | type | description |
|---|---|---|
| mean_score | float | Average cross-validation score |
| std_score | float | Standard deviation across folds |
| confidence_low | float | Lower 95% CI bound |
| confidence_high | float | Upper 95% CI bound |
| fold_scores | list[float] | Per-fold scores |

## Example Usage

```python
# Simple regression CV
def train_lr(X, y):
    n = len(X)
    p = len(X[0]) if n else 0
    Xm = [[1.0] + row for row in X]
    Xty = [sum(Xm[i][j] * y[i] for i in range(n)) for j in range(p + 1)]
    XtX = [[sum(Xm[i][a] * Xm[i][b] for i in range(n)) for b in range(p + 1)] for a in range(p + 1)]
    return solve_normal_equations(XtX, Xty)

def score_rmse(model, X, y):
    preds = [sum(w[j+1]*row[j] for j in range(len(row))) for row in X]
    return math.sqrt(sum((y[i]-preds[i])**2 for i in range(len(y)))/len(y))

r = run_cross_validation(X, y, train_lr, score_rmse, n_folds=5)
print(f"CV RMSE: {r.mean_score:.3f} ± {r.std_score:.3f}")
```

## Security Considerations

- SQLite is local and in-process; defaults to in-memory.
- No network I/O.
- Pure Python implementation with no external dependencies.