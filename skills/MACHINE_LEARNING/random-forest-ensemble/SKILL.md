---
name: random-forest-ensemble
domain: MACHINE_LEARNING
version: "1.0.0"
surfaces: [python, sqlite]
description: Multi-surface random forest ensemble with Python surface for bagged tree training and SQLite surface for member tracking and ensemble prediction aggregation. Supports configurable tree counts.
compatibility: PYTHON, SQLITE
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
Ensemble classifier combining multiple bootstrap-sampled decision trees with majority voting.

# Description
Core inputs: feature matrix (list of vectors), labels (list), n_estimators (int), max_depth (int), bootstrap_ratio (float). Mechanical steps: draw random bootstrap samples, grow diverse trees on subsets, aggregate predictions via voting, compute ensemble confidence via variance. Expected outputs: forest model (list of trees), predictions (list), confidence scores (list), out-of-bag error estimate (float).

## Python Surface

```python
import random

def my_log2(x):
    if x <= 0:
        return 0.0
    if x == 1.0:
        return 0.0
    result = 0.0
    while x > 1.5:
        x = x / 2.0
        result = result + 1.0
    while x < 0.5:
        x = x * 2.0
        result = result - 1.0
    y = x - 1.0
    log_val = 0.0
    term = y
    sign = 1.0
    for n in range(1, 100):
        log_val = log_val + sign * term / n
        term = term * y
        sign = -sign
        if abs(term / n) < 1e-15:
            break
    return result + log_val / 0.6931471805599453

def compute_entropy(labels):
    count = {}
    for label in labels:
        count[label] = count.get(label, 0) + 1
    total = len(labels)
    if total == 0:
        return 0.0
    entropy = 0.0
    for label, c in count.items():
        p = c / total
        if p > 0:
            entropy = entropy - p * my_log2(p)
    return entropy

def compute_gain(left_labels, right_labels, parent_entropy):
    total = len(left_labels) + len(right_labels)
    if total == 0:
        return 0.0
    n_l = len(left_labels)
    n_r = len(right_labels)
    left_ent = compute_entropy(left_labels)
    right_ent = compute_entropy(right_labels)
    child_ent = (n_l * left_ent + n_r * right_ent) / total
    return parent_entropy - child_ent

def find_best_split(features, labels, feature_indices, n_features_to_try):
    best_gain = -1.0
    best_feature = -1
    best_threshold = 0.0
    parent_ent = compute_entropy(labels)
    
    features_to_check = random.sample(feature_indices, min(n_features_to_try, len(feature_indices)))
    
    for feat_idx in features_to_check:
        values = {}
        for i in range(len(features)):
            val = features[i][feat_idx]
            if val not in values:
                values[val] = []
            values[val].append(labels[i])
        
        for thresh in sorted(values.keys()):
            left_labels = []
            right_labels = []
            for i in range(len(features)):
                if features[i][feat_idx] <= thresh:
                    left_labels.append(labels[i])
                else:
                    right_labels.append(labels[i])
            if len(left_labels) == 0 or len(right_labels) == 0:
                continue
            gain = compute_gain(left_labels, right_labels, parent_ent)
            if gain > best_gain:
                best_gain = gain
                best_feature = feat_idx
                best_threshold = thresh
    
    return (best_feature, best_threshold, best_gain)

def build_tree(features, labels, feature_indices, depth, max_depth, min_samples, n_features_to_try):
    if len(features) < min_samples or depth >= max_depth:
        count = {}
        for label in labels:
            count[label] = count.get(label, 0) + 1
        majority = max(count.items(), key=lambda x: x[1])[0] if count else None
        return {"leaf": True, "prediction": majority, "samples": len(features)}
    
    ent = compute_entropy(labels)
    if ent == 0.0:
        return {"leaf": True, "prediction": labels[0], "samples": len(features)}
    
    feat, thresh, gain = find_best_split(features, labels, feature_indices, n_features_to_try)
    
    if gain <= 0.0:
        count = {}
        for label in labels:
            count[label] = count.get(label, 0) + 1
        majority = max(count.items(), key=lambda x: x[1])[0] if count else None
        return {"leaf": True, "prediction": majority, "samples": len(features)}
    
    left_feat = []
    left_labels = []
    right_feat = []
    right_labels = []
    
    for i in range(len(features)):
        if features[i][feat] <= thresh:
            left_feat.append(features[i])
            left_labels.append(labels[i])
        else:
            right_feat.append(features[i])
            right_labels.append(labels[i])
    
    left_tree = build_tree(left_feat, left_labels, feature_indices, depth + 1, max_depth, min_samples, n_features_to_try)
    right_tree = build_tree(right_feat, right_labels, feature_indices, depth + 1, max_depth, min_samples, n_features_to_try)
    
    return {
        "leaf": False,
        "feature": feat,
        "threshold": thresh,
        "gain": gain,
        "left": left_tree,
        "right": right_tree,
        "samples": len(features)
    }

def predict_tree(tree, sample, feature_indices):
    if tree.get("leaf", False):
        return tree["prediction"]
    if sample[tree["feature"]] <= tree["threshold"]:
        return predict_tree(tree["left"], sample, feature_indices)
    return predict_tree(tree["right"], sample, feature_indices)

def bootstrap_sample(features, labels, ratio=0.8):
    n = len(features)
    sample_size = max(1, int(n * ratio))
    indices = [random.randint(0, n - 1) for _ in range(sample_size)]
    boot_features = [features[i] for i in indices]
    boot_labels = [labels[i] for i in indices]
    return boot_features, boot_labels, indices

def random_forest_classifier(features, labels, n_estimators=5, max_depth=5, min_samples=2, bootstrap_ratio=0.8):
    if len(features) == 0:
        return ([], [], [])
    
    n_features = len(features[0]) if len(features) > 0 else 0
    feature_indices = list(range(n_features))
    n_features_to_try = max(1, int(n_features ** 0.5))
    
    forest = []
    oob_predictions = {i: [] for i in range(len(features))}
    
    for tree_idx in range(n_estimators):
        boot_features, boot_labels, sample_indices = bootstrap_sample(features, labels, bootstrap_ratio)
        
        tree = build_tree(boot_features, boot_labels, feature_indices, 0, max_depth, min_samples, n_features_to_try)
        forest.append({
            "tree": tree,
            "sample_indices": sample_indices
        })
        
        for i in range(len(features)):
            if i not in sample_indices:
                pred = predict_tree(tree, features[i], feature_indices)
                oob_predictions[i].append(pred)
    
    predictions = []
    confidences = []
    
    for i in range(len(features)):
        tree_preds = []
        for tree_model in forest:
            pred = predict_tree(tree_model["tree"], features[i], feature_indices)
            tree_preds.append(pred)
        
        pred = tree_preds[0] if tree_preds else None
        predictions.append(pred)
        
        unique_preds = {}
        for p in tree_preds:
            unique_preds[p] = unique_preds.get(p, 0) + 1
        confidence = max(unique_preds.values()) / len(tree_preds) if tree_preds else 0.0
        confidences.append(confidence)
    
    oob_error = 0.0
    oob_count = 0
    for i in range(len(features)):
        if oob_predictions[i]:
            majority = max(set(oob_predictions[i]), key=oob_predictions[i].count) if oob_predictions[i] else labels[i]
            if majority != labels[i]:
                oob_error = oob_error + 1
            oob_count = oob_count + 1
    oob_error = oob_error / oob_count if oob_count > 0 else 0.0
    
    return (forest, predictions, confidences, oob_error)

def forest_predict(forest, features, feature_indices):
    predictions = []
    confidences = []
    
    for sample in features:
        tree_preds = []
        for tree_model in forest:
            pred = predict_tree(tree_model["tree"], sample, feature_indices)
            tree_preds.append(pred)
        
        pred = tree_preds[0] if tree_preds else None
        predictions.append(pred)
        
        unique_preds = {}
        for p in tree_preds:
            unique_preds[p] = unique_preds.get(p, 0) + 1
        confidence = max(unique_preds.values()) / len(tree_preds) if tree_preds else 0.0
        confidences.append(confidence)
    
    return predictions, confidences
```

## SQLite Surface

```sql
-- Bootstrap sample management table
CREATE TABLE IF NOT EXISTS bootstrap_samples (
    tree_id INTEGER,
    sample_index INTEGER,
    feature_vector TEXT,
    label TEXT,
    session_id TEXT
);

-- Forest state tracking
CREATE TABLE IF NOT EXISTS forest_state (
    iteration INTEGER,
    tree_id INTEGER,
    n_nodes INTEGER,
    n_leaves INTEGER,
    oob_error REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Feature importance aggregation
CREATE TABLE IF NOT EXISTS feature_importance (
    feature_index INTEGER,
    importance_sum REAL,
    tree_count INTEGER,
    session_id TEXT
);

-- Insert bootstrap sample for tree
-- Parameters: ? = tree_id, ? = index, ? = features_json, ? = label, ? = session_id
INSERT INTO bootstrap_samples (tree_id, sample_index, feature_vector, label, session_id)
VALUES (?, ?, ?, ?, ?);

-- Query all samples for a specific tree
SELECT feature_vector, label FROM bootstrap_samples WHERE tree_id = ? AND session_id = ?;

-- Update feature importance
-- Parameters: ? = feature_idx, ? = importance, ? = session_id
INSERT OR REPLACE INTO feature_importance (feature_index, importance_sum, tree_count, session_id)
VALUES (?, 
    COALESCE((SELECT importance_sum FROM feature_importance WHERE feature_index = ? AND session_id = ?) + ?,
    ?),
    COALESCE((SELECT tree_count FROM feature_importance WHERE feature_index = ? AND session_id = ?) + 1, 1),
    ?);

-- Aggregate final importance
SELECT feature_index, importance_sum / tree_count as avg_importance 
FROM feature_importance 
WHERE session_id = ?;
```