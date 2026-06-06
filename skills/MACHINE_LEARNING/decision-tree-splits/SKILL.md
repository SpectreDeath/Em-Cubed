---
name: decision-tree-splits
domain: MACHINE_LEARNING
version: "1.0.0"
surfaces: [python, prolog]
---

# Purpose
Recursive binary partitioning to learn decision rules and classify data via axis-aligned splits.

# Description
Core inputs: feature matrix (list of vectors), labels (list of discrete classes), max depth (int), min samples (int). Mechanical steps: compute entropy for each feature, find best split by information gain, partition data left/right, recursively build subtrees, prune by depth constraints. Expected outputs: tree structure (nested dict), predicted classes (list), feature importances (dict mapping feature index to gain).

## Python Surface

```python
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
    # ln(1+y) = y - y^2/2 + y^3/3 - y^4/4 + ...
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

def find_best_split(features, labels, feature_indices):
    best_gain = -1.0
    best_feature = -1
    best_threshold = 0.0
    parent_ent = compute_entropy(labels)
    
    for feat_idx in feature_indices:
        values = []
        for i in range(len(features)):
            values.append(features[i][feat_idx])
        values_sorted = sorted(set(values))
        
        for thresh in values_sorted:
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

def build_tree(features, labels, feature_indices, depth, max_depth, min_samples):
    if len(features) < min_samples or depth >= max_depth:
        count = {}
        for label in labels:
            count[label] = count.get(label, 0) + 1
        majority = max(count.items(), key=lambda x: x[1])[0] if count else None
        return {"leaf": True, "prediction": majority, "samples": len(features)}
    
    ent = compute_entropy(labels)
    if ent == 0.0:
        return {"leaf": True, "prediction": labels[0], "samples": len(features)}
    
    feat, thresh, gain = find_best_split(features, labels, feature_indices)
    
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
    
    left_tree = build_tree(left_feat, left_labels, feature_indices, depth + 1, max_depth, min_samples)
    right_tree = build_tree(right_feat, right_labels, feature_indices, depth + 1, max_depth, min_samples)
    
    return {
        "leaf": False,
        "feature": feat,
        "threshold": thresh,
        "gain": gain,
        "left": left_tree,
        "right": right_tree,
        "samples": len(features)
    }

def predict_tree(tree, sample):
    if tree.get("leaf", False):
        return tree["prediction"]
    if sample[tree["feature"]] <= tree["threshold"]:
        return predict_tree(tree["left"], sample)
    return predict_tree(tree["right"], sample)

def decision_tree_classifier(features, labels, max_depth=5, min_samples=2):
    n_features = len(features[0]) if len(features) > 0 else 0
    feature_indices = list(range(n_features))
    
    tree = build_tree(features, labels, feature_indices, 0, max_depth, min_samples)
    
    predictions = []
    for sample in features:
        predictions.append(predict_tree(tree, sample))
    
    importances = {}
    def compute_importances(node, total_samples):
        if node.get("leaf", False):
            return
        feat = node["feature"]
        importances[feat] = importances.get(feat, 0.0) + node["gain"]
        compute_importances(node.get("left", {}), total_samples)
        compute_importances(node.get("right", {}), total_samples)
    
    compute_importances(tree, len(features))
    if len(features) > 0:
        for feat in importances:
            importances[feat] = importances[feat] / len(features)
    
    return (tree, predictions, importances)

def classify_with_tree(tree, samples):
    return [predict_tree(tree, s) for s in samples]
```

## Prolog Surface

```prolog
% Decision tree node traversal rules
leaf_node(Tree, Prediction) :-
    get_dict(leaf, Tree, true),
    get_dict(prediction, Tree, Prediction).

internal_node(Tree, Feature, Threshold) :-
    get_dict(leaf, Tree, false),
    get_dict(feature, Tree, Feature),
    get_dict(threshold, Tree, Threshold).

% Route sample through tree based on feature values
tree_route(Tree, Sample, Prediction) :-
    leaf_node(Tree, Prediction), !.

tree_route(Tree, Sample, Prediction) :-
    internal_node(Tree, Feature, Threshold),
    nth0(Feature, Sample, Value),
    (Value =< Threshold ->
        get_dict(left, Tree, Left),
        tree_route(Left, Sample, Prediction)
    ;
        get_dict(right, Tree, Right),
        tree_route(Right, Sample, Prediction)
    ).

% Classification for multiple samples
classify_all(Tree, Samples, Predictions) :-
    findall(Pred, (member(Sample, Samples), tree_route(Tree, Sample, Pred)), Predictions).

% Feature importance aggregation
feature_importance(Tree, Feature, Importance) :-
    get_dict(feature, Tree, Feature),
    get_dict(gain, Tree, Gain),
    get_dict(samples, Tree, Samples),
    Importance is Gain / Samples.

all_feature_importances(Tree, Importances) :-
    findall(F-I, feature_importance(Tree, F, I), Importances).

% Split validity constraints
valid_split(Threshold, FeatureValues) :-
    length(FeatureValues, Count),
    Count > 0,
    min_list(FeatureValues, Min),
    max_list(FeatureValues, Max),
    Min =< Threshold,
    Threshold =< Max.

% Entropy consistency check
entropy_consistent(Labels, LeftLabels, RightLabels) :-
    length(Labels, Total),
    length(LeftLabels, LeftLen),
    length(RightLabels, RightLen),
    LeftLen + RightLen =:= Total.

% Tree depth constraint
within_max_depth(Tree, MaxDepth) :-
    tree_depth(Tree, Depth),
    Depth =< MaxDepth.

tree_depth(Tree, Depth) :-
    leaf_node(Tree, _),
    Depth = 1.

tree_depth(Tree, Depth) :-
    internal_node(Tree, _, _),
    get_dict(left, Tree, Left),
    get_dict(right, Tree, Right),
    tree_depth(Left, LeftDepth),
    tree_depth(Right, RightDepth),
    Depth is 1 + max(LeftDepth, RightDepth).

% Classification purity constraints
pure_leaf(Tree) :-
    leaf_node(Tree, _).

mixed_leaf(Tree) :-
    \+ pure_leaf(Tree).

% Path extraction for explanation
decision_path(Tree, Sample, Path) :-
    decision_path(Tree, Sample, [], Path).

decision_path(Tree, _, Path, Path) :-
    leaf_node(Tree, _).

decision_path(Tree, Sample, Acc, Path) :-
    internal_node(Tree, Feature, Threshold),
    nth0(Feature, Sample, Value),
    (Value =< Threshold ->
        get_dict(left, Tree, Left),
        NewAcc = [feature_less_equal(Feature, Threshold) | Acc],
        decision_path(Left, Sample, NewAcc, Path)
    ;
        get_dict(right, Tree, Right),
        NewAcc = [feature_greater(Feature, Threshold) | Acc],
        decision_path(Right, Sample, NewAcc, Path)
    ).
```