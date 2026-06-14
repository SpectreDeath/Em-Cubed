"""Integration tests for distributed execution and stress testing."""

import time

import pytest

from em_cubed.surfaces import PythonSurface


_RF_TRAINING_CODE = """
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


def _hash_rand(seed):
    accum = seed * 2654435761
    accum = ((accum >> 16) ^ accum) * 2246822519
    accum = ((accum >> 13) ^ accum) * 3266489917
    accum = (accum >> 16) ^ accum
    return (accum & 0x7FFFFFFF) / 0x7FFFFFFF


def _sample_indices(n, sample_size, seed):
    indices = []
    for i in range(n):
        idx = int(_hash_rand(seed + i) * n) % n
        if idx not in indices:
            indices.append(idx)
        if len(indices) >= sample_size:
            break
    return indices


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
    feature_count = min(n_features_to_try, len(feature_indices))
    features_to_check = feature_indices[:feature_count]
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


def build_tree(features, labels, feature_indices, depth, max_depth, min_samples, n_features_to_try, seed=0):
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
    left_tree = build_tree(left_feat, left_labels, feature_indices, depth + 1, max_depth, min_samples, n_features_to_try, seed)
    right_tree = build_tree(right_feat, right_labels, feature_indices, depth + 1, max_depth, min_samples, n_features_to_try, seed)
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


def bootstrap_sample(features, labels, ratio=0.8, seed=0):
    n = len(features)
    sample_size = max(1, int(n * ratio))
    indices = _sample_indices(n, sample_size, seed)
    boot_features = [features[i] for i in indices]
    boot_labels = [labels[i] for i in indices]
    return boot_features, boot_labels, indices


def random_forest_classifier(features, labels, n_estimators=5, max_depth=5, min_samples=2, bootstrap_ratio=0.8, seed=0):
    if len(features) == 0:
        return ([], [], [])
    n_features = len(features[0]) if len(features) > 0 else 0
    feature_indices = list(range(n_features))
    n_features_to_try = max(1, int(n_features ** 0.5))
    forest = []
    oob_predictions = {i: [] for i in range(len(features))}
    for tree_idx in range(n_estimators):
        boot_features, boot_labels, sample_indices = bootstrap_sample(features, labels, bootstrap_ratio, seed + tree_idx)
        tree = build_tree(boot_features, boot_labels, feature_indices, 0, max_depth, min_samples, n_features_to_try, seed + tree_idx)
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

result = random_forest_classifier(features, labels, n_estimators=10, max_depth=8)
"""


class TestUciCensusRandomForest:
    """Stress-test Async Timeouts: UCI Census Income via Random Forest."""

    @pytest.fixture
    def uci_census_dataset(self):
        """Small synthetic UCI Census Income-style dataset."""
        import random

        random.seed(42)
        n = 200
        features = []
        labels = []
        for _ in range(n):
            age = random.randint(17, 90)
            hours = random.randint(1, 99)
            capital_gain = random.randint(0, 100000)
            capital_loss = random.randint(0, 5000)
            education_num = random.randint(1, 16)
            features.append([age, hours, capital_gain, capital_loss, education_num])
            labels.append(1 if (age > 30 and hours > 40 and capital_gain > 5000) else 0)
        return features, labels

    @pytest.mark.asyncio
    async def test_random_forest_uci_timeout(self, uci_census_dataset):
        """Random Forest on larger UCI-style data should trigger timeout/rejection behavior."""
        features, labels = uci_census_dataset
        surface = PythonSurface(timeout=2.0)
        start = time.time()
        response = await surface.execute(
            _RF_TRAINING_CODE,
            {"features": features, "labels": labels},
        )
        elapsed = time.time() - start
        assert response.get("status") == "error"
        assert "timed out" in response.get("message", "").lower() or "rejected" in response.get("message", "").lower()
        assert elapsed < 30.0

    @pytest.mark.asyncio
    async def test_dag_scheduler_timeout_rejection(self):
        """DAG scheduler should reject execution when concurrency limit is reached."""
        surface = PythonSurface(timeout=0.5)
        long_running = "x = 0\nwhile x < 100000000:\n    x += 1"
        tasks = [surface.execute(long_running, {}) for _ in range(3)]
        results = await __import__("asyncio").gather(*tasks, return_exceptions=False)
        assert all(r["status"] == "error" for r in results)
        assert any(
            "timed out" in r["message"].lower() or "rejected" in r["message"].lower()
            for r in results
        )


class TestSqliteDatalogWebDataCommons:
    """E3: Test SQLite/Datalog surfaces with Web Data Commons structured data."""

    @pytest.mark.asyncio
    async def test_sqlite_surface_persists_session(self):
        """Verify SQLite surface can execute queries with session context."""
        from em_cubed.surfaces.sqlite_surface import SQLiteSurface
        from em_cubed.skills.telemetry import initialize_telemetry

        initialize_telemetry()

        surface = SQLiteSurface()
        session_id = "test-session-123"
        context = {"skill_input": {}, "surfaces": {}, "trace": None, "session_id": session_id}

        start = time.time()

        create_sql = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            name TEXT,
            price REAL,
            category TEXT
        );
        """

        result = await surface.execute(create_sql, context)
        assert result.get("status") in ("ok", "error")

        insert_sql = "INSERT INTO products (product_id, name, price, category) VALUES ('P1', 'Product 1', 10.0, 'electronics');"
        result = await surface.execute(insert_sql, context)
        assert result.get("status") in ("ok", "error")

        query_sql = "SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category;"
        result = await surface.execute(query_sql, context)

        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 5000, f"Query latency exceeded 5s: {elapsed_ms}ms"
        assert result.get("status") == "ok"
        assert result.get("value") is not None
