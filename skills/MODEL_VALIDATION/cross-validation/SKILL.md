---
name: cross-validation
domain: MODEL_VALIDATION
version: 1.0.0
surfaces:
  - python
  - sqlite
description: K-fold cross-validation engine supporting standard uniform or stratified sampling for classification tasks. Computes per-fold model performance metrics, aggregates statistical summaries (mean score, standard deviation, min, max), computes Gaussian confidence intervals at specified significance levels (90%, 95%, 99%), and persists fold assignments, true/predicted observations, and run metadata in local SQLite tables for offline auditability. Use when evaluating model generalization error, preventing validation leakage, or auditing cross-validation runs.
purpose: Assess model generalization error with stratified k-fold splits, statistical confidence bounds, and SQLite audit logging.
dependencies: []
tags:
  - cross-validation
  - k-fold
  - stratified-split
  - confidence-intervals
  - sqlite-audit
  - generalization-error
inputs:
  X:
    type: array
    required: true
    description: Feature matrix dataset of shape $(N, P)$ represented as a list of numerical vectors.
  y:
    type: array
    required: true
    description: Target vector of length $N$ with continuous numbers or discrete class labels.
  n_folds:
    type: integer
    required: false
    description: Number of cross-validation folds $K \ge 2$ (default `5`).
  stratified:
    type: boolean
    required: false
    description: Whether to preserve categorical label proportions across validation folds (default `false`).
  confidence_level:
    type: number
    required: false
    description: Significance confidence level for margin-of-error bounds (`0.90`, `0.95`, or `0.99`, default `0.95`).
outputs:
  run_id:
    type: string
    description: Unique identifier assigned to the cross-validation execution run.
  k_folds:
    type: integer
    description: Number of evaluated folds $K$.
  n_samples:
    type: integer
    description: Total sample size $N$ in input feature matrix.
  mean_score:
    type: number
    description: Arithmetic mean of cross-validation metric scores $\bar{S} = \frac{1}{K}\sum S_k$.
  std_score:
    type: number
    description: Sample standard deviation of fold metric scores.
  min_score:
    type: number
    description: Minimum score observed across all folds.
  max_score:
    type: number
    description: Maximum score observed across all folds.
  fold_scores:
    type: array
    description: List of individual metric scores computed for each fold.
  confidence_low:
    type: number
    description: Lower bound of confidence interval $\bar{S} - z_{\alpha/2} \frac{s}{\sqrt{K}}$.
  confidence_high:
    type: number
    description: Upper bound of confidence interval $\bar{S} + z_{\alpha/2} \frac{s}{\sqrt{K}}$.
---

# Cross-Validation Engine

`cross-validation` assesses model generalization capability and guards against overfitting. It generates **stratified or standard $K$-fold data splits**, calculates **fold performance metrics and confidence bounds in Python**, and persists **audit logs in SQLite**:

$$\bar{S} = \frac{1}{K}\sum_{k=1}^K S_k, \quad s = \sqrt{\frac{1}{K-1}\sum_{k=1}^K (S_k - \bar{S})^2}, \quad \text{CI}_{1-\alpha} = \bar{S} \pm z_{1-\alpha/2} \frac{s}{\sqrt{K}}$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Cross-Validation Progression

```
[1. Dataset Ingest & Stratification Audit] → [2. K-Fold Index Partitioning] → [3. Visual Brief] → [4. Checkpoint] → [5. Iterative Evaluation, SQLite & Emit]
```

### Stage 1: Dataset Ingest & Stratification Audit
1. Ingest feature matrix $X$ and target vector $y$.
2. Assert dimension consistency ($|X| = |y| = N \ge K \ge 2$).
3. If `stratified: true`, verify class label distribution across categories.

> **Completion criterion**: Non-empty dataset with compatible fold count verified.

---

### Stage 2: K-Fold Index Partitioning
1. Generate $K$ disjoint validation subsets $V_1, \dots, V_K$ such that $\bigcup V_k = \{0, \dots, N-1\}$.
2. For stratified splitting, partition observations proportionally within each target class label.

> **Completion criterion**: Disjoint partition sets with balanced class counts constructed.

---

### Stage 3: The Visual Brief
For model performance metrics and cross-validation stability, generate an interactive brief:
- **Location**: Write to `%TEMP%\cross-validation-brief-<timestamp>.html` (Windows) or `/tmp/cross-validation-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render per-fold score bar chart, mean score gauge with confidence interval error bars, and SQLite audit record table.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before metric aggregation:
1. Verify fold execution: ensure all $K$ models fit and produce valid finite float scores (no `NaN` or `Inf`).
2. Compute standard error and confidence margin $M = z \cdot s / \sqrt{K}$.

> **Completion criterion**: All fold scores verified finite with confidence bounds computed.

---

### Stage 5: Iterative Evaluation, SQLite & Output Emission
1. Persist fold partition mapping and metric records into SQLite tables `cv_folds` and `cv_metrics`.
2. Emit complete `CrossValidationResult` record.

> **Completion criterion**: Full cross-validation payload emitted.

---

## Surface References

### SQLite Audit Surface

```sql
CREATE TABLE IF NOT EXISTS cv_folds (
    run_id         TEXT NOT NULL,
    fold_index     INTEGER NOT NULL,
    observation_id INTEGER,
    is_training    INTEGER,
    is_validation  INTEGER,
    PRIMARY KEY (run_id, fold_index, observation_id)
);

CREATE TABLE IF NOT EXISTS cv_metrics (
    run_id          TEXT PRIMARY KEY,
    k_folds         INTEGER,
    n_samples       INTEGER,
    mean_score      REAL,
    std_score       REAL,
    min_score       REAL,
    max_score       REAL,
    confidence_low  REAL,
    confidence_high REAL,
    created_at      TEXT DEFAULT (datetime('now'))
);
```

### Python Cross-Validation Surface

```python
import math
import sqlite3
import uuid
from typing import Dict, List, Any, Optional, Callable, Union

def run_cross_validation(
    X: List[List[float]],
    y: List[Union[int, float]],
    model_fn: Optional[Callable] = None,
    score_fn: Optional[Callable] = None,
    n_folds: int = 5,
    stratified: bool = False,
    confidence_level: float = 0.95,
    db_path: str = ":memory:"
) -> Dict[str, Any]:
    n = len(X)
    if n != len(y) or n < n_folds or n_folds < 2:
        raise ValueError(f"invalid_cv_dimensions: N={n}, folds={n_folds}.")
        
    run_id = str(uuid.uuid4())[:8]
    
    # Partition indices
    if stratified:
        label_to_idx = {}
        for i, label in enumerate(y):
            label_to_idx.setdefault(label, []).append(i)
        fold_indices = [([], []) for _ in range(n_folds)]
        for label, idxs in label_to_idx.items():
            for i, idx in enumerate(idxs):
                val_fold = i % n_folds
                for f in range(n_folds):
                    if f == val_fold:
                        fold_indices[f][1].append(idx)
                    else:
                        fold_indices[f][0].append(idx)
    else:
        fold_size = n // n_folds
        fold_indices = []
        indices = list(range(n))
        for k in range(n_folds):
            start = k * fold_size
            end = start + fold_size if k < n_folds - 1 else n
            val_idx = indices[start:end]
            train_idx = indices[:start] + indices[end:]
            fold_indices.append((train_idx, val_idx))
            
    # Default model / score if omitted (baseline regression test)
    default_model = model_fn or (lambda tr_x, tr_y: sum(tr_y) / len(tr_y) if tr_y else 0.0)
    default_score = score_fn or (lambda m, v_x, v_y: 1.0 - (sum((v - m)**2 for v in v_y) / max(1e-6, sum((v - sum(v_y)/len(v_y))**2 for v in v_y))))
    
    fold_scores = []
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cv_folds (
            run_id TEXT, fold_index INT, observation_id INT, is_training INT, is_validation INT,
            PRIMARY KEY (run_id, fold_index, observation_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cv_metrics (
            run_id TEXT PRIMARY KEY, k_folds INT, n_samples INT, mean_score REAL, std_score REAL,
            min_score REAL, max_score REAL, confidence_low REAL, confidence_high REAL, created_at TEXT DEFAULT(datetime('now'))
        )
    """)
    
    for k, (train_idx, val_idx) in enumerate(fold_indices):
        tr_X = [X[i] for i in train_idx]
        tr_y = [y[i] for i in train_idx]
        v_X = [X[i] for i in val_idx]
        v_y = [y[i] for i in val_idx]
        
        m = default_model(tr_X, tr_y)
        sc = default_score(m, v_X, v_y)
        fold_scores.append(float(sc))
        
        for obs_id in train_idx:
            conn.execute("INSERT OR REPLACE INTO cv_folds VALUES (?, ?, ?, 1, 0)", (run_id, k, obs_id))
        for obs_id in val_idx:
            conn.execute("INSERT OR REPLACE INTO cv_folds VALUES (?, ?, ?, 0, 1)", (run_id, k, obs_id))
            
    mean_s = sum(fold_scores) / len(fold_scores)
    var_s = sum((s - mean_s) ** 2 for s in fold_scores) / (len(fold_scores) - 1)
    std_s = math.sqrt(var_s)
    
    z_val = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence_level, 1.96)
    margin = z_val * (std_s / math.sqrt(n_folds))
    
    conn.execute(
        "INSERT INTO cv_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
        (run_id, n_folds, n, mean_s, std_s, min(fold_scores), max(fold_scores), mean_s - margin, mean_s + margin)
    )
    conn.commit()
    conn.close()
    
    return {
        "run_id": run_id,
        "k_folds": n_folds,
        "n_samples": n,
        "mean_score": round(mean_s, 4),
        "std_score": round(std_s, 4),
        "min_score": round(min(fold_scores), 4),
        "max_score": round(max(fold_scores), 4),
        "fold_scores": [round(s, 4) for s in fold_scores],
        "confidence_low": round(mean_s - margin, 4),
        "confidence_high": round(mean_s + margin, 4)
    }
```

---

## Anti-Patterns & Guardrails

- **Information Leakage via Unsegregated Preprocessing** — Performing global feature scaling or imputation across the full dataset before splitting into cross-validation folds.
- **Unstratified Imbalanced Classification** — Using random splits on rare class datasets, resulting in validation folds with zero positive class samples.
- **Fold Count Oversizing** — Setting $K > N$, which causes empty fold errors or excessive compute latency.