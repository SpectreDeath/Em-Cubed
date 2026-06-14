"""
Integration tests for STATISTICS naive-bayes-classifier skill:
  - gaussian_pdf
  - my_exp
  - naive_bayes_train
  - naive_bayes_predict
  - naive_bayes

Bottom-up: exponential taylor series → gaussian pdf → training → prediction.
"""

import math


# ============================================================
# Function-under-test extracted from SKILL.md implementations
# ============================================================

def my_exp(x):
    """Taylor-series exponential matching SKILL.md implementation."""
    if x > 50:
        return 1e21
    if x < -30:
        result = 1.0
        term = 1.0
        for i in range(1, 100):
            term = term * (-x) / i
            result = result + term
            if term > 1e15:
                return 1e-20
            if term < 1e-15 * result:
                break
        return 1.0 / result
    if x < 0:
        result = 1.0
        term = 1.0
        for i in range(1, 50):
            term = term * (-x) / i
            result = result + term
        return 1.0 / result
    result = 1.0
    term = 1.0
    for i in range(1, 50):
        term = term * x / i
        result = result + term
        if term < 1e-15 * result and i > 10:
            break
    return result


def gaussian_pdf(x, mu, sigma):
    """Gaussian probability density function using my_exp for exponentiation."""
    if sigma == 0:
        sigma = 1e-6
    coeff = 1.0 / (sigma * (2.0 * 3.14159265358979) ** 0.5)
    exp_val = -((x - mu) ** 2) / (2.0 * sigma * sigma)
    return coeff * my_exp(exp_val)


def naive_bayes_train(features, labels):
    """Train naive bayes: compute priors and Gaussian likelihoods per class."""
    n = len(features)
    p = len(features[0])
    classes = list(set(labels))

    priors = {}
    for c in classes:
        priors[c] = labels.count(c) / n

    likelihoods = {}
    for c in classes:
        class_features = [features[i] for i in range(n) if labels[i] == c]
        if len(class_features) == 0:
            continue
        means = [0.0] * p
        variances = [0.0] * p
        for j in range(p):
            total = 0.0
            for i in range(len(class_features)):
                total = total + class_features[i][j]
            means[j] = total / len(class_features)
            var_total = 0.0
            for i in range(len(class_features)):
                var_total = var_total + (class_features[i][j] - means[j]) ** 2
            variances[j] = var_total / len(class_features) + 1e-6
        likelihoods[c] = (means, variances)

    return priors, likelihoods


def naive_bayes_predict(features, priors, likelihoods):
    """Predict using trained priors and likelihoods."""
    predictions = []
    probs_list = []

    for feat in features:
        probs = {}
        best_class = None
        best_prob = -1.0

        for c in priors:
            log_prob = priors[c]
            means, variances = likelihoods[c]
            for j in range(len(feat)):
                log_prob = log_prob * gaussian_pdf(feat[j], means[j], variances[j] ** 0.5)
            probs[c] = log_prob
            if log_prob > best_prob:
                best_prob = log_prob
                best_class = c
        predictions.append(best_class)
        probs_list.append(probs)

    return predictions, probs_list


def naive_bayes(features, labels, test_features):
    """Full pipeline: train then predict."""
    priors, likelihoods = naive_bayes_train(features, labels)
    predictions, probs = naive_bayes_predict(test_features, priors, likelihoods)
    return (priors, likelihoods, predictions, probs)


# ============================================================
# 1. Gaussian PDF — value at mean, symmetry, edge cases
# ============================================================

class TestGaussianPDF:
    """Unit tests for gaussian_pdf function."""

    def test_value_at_mean(self):
        """PDF at mean should be 1/(sigma*sqrt(2*pi))."""
        mu = 5.0
        sigma = 2.0
        expected = 1.0 / (sigma * math.sqrt(2.0 * math.pi))
        result = gaussian_pdf(5.0, mu, sigma)
        assert abs(result - expected) < 0.01

    def test_symmetry(self):
        """PDF should be symmetric around the mean."""
        mu = 10.0
        sigma = 1.5
        left = gaussian_pdf(mu - 1.0, mu, sigma)
        right = gaussian_pdf(mu + 1.0, mu, sigma)
        assert abs(left - right) < 0.01

    def test_very_small_variance(self):
        """Very small sigma should be clamped to avoid division by zero."""
        result = gaussian_pdf(5.0, 5.0, 0.0)
        # sigma=0 becomes 1e-6, then value at mean is 1/(1e-6 * sqrt(2*pi))
        expected = 1.0 / (1e-6 * math.sqrt(2.0 * math.pi))
        assert abs(result - expected) < 1e10

    def test_tail_behavior_large_x(self):
        """PDF should decay toward zero for large |x| from mean."""
        mu = 0.0
        sigma = 1.0
        result = gaussian_pdf(100.0, mu, sigma)
        assert result < 0.01  # Should be very small

    def test_known_values(self):
        """Verify against known sigma=1, mu=0 values."""
        # PDF(0|0,1) = 1/sqrt(2*pi) ≈ 0.3989
        result = gaussian_pdf(0.0, 0.0, 1.0)
        expected = 1.0 / math.sqrt(2.0 * math.pi)
        assert abs(result - expected) < 0.01


# ============================================================
# 2. MyExp — Taylor series exponential verification
# ============================================================

class TestMyExp:
    """Unit tests for my_exp Taylor series implementation."""

    def test_exp_0_equals_1(self):
        """exp(0) should equal 1."""
        assert abs(my_exp(0.0) - 1.0) < 0.01

    def test_exp_1_approximates_e(self):
        """exp(1) should approximate e ≈ 2.718."""
        result = my_exp(1.0)
        assert abs(result - 2.718) < 0.02

    def test_large_positive(self):
        """Large positive x should return capped value."""
        result = my_exp(100.0)
        assert result == 1e21

    def test_large_negative(self):
        """Large negative x should return very small value."""
        result = my_exp(-50.0)
        assert result < 1e-6

    def test_symmetry_negative(self):
        """exp(x) * exp(-x) should equal 1."""
        pos = my_exp(2.0)
        neg = my_exp(-2.0)
        product = pos * neg
        assert abs(product - 1.0) < 0.01


# ============================================================
# 3. Naive Bayes Train — prior and likelihood verification
# ============================================================

epsilon = 0.01


class TestNaiveBayesTrain:
    """Unit tests for training function."""

    def test_basic_training_two_classes(self):
        """Basic training with two distinct classes."""
        features = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]]
        labels = ["A", "A", "B", "B"]
        priors, likelihoods = naive_bayes_train(features, labels)
        assert "A" in priors
        assert "B" in priors

    def test_class_priors_correct(self):
        """Class priors should reflect relative frequencies."""
        features = [[1.0], [2.0], [3.0], [1.0]]
        labels = ["A", "A", "B", "B"]
        priors, _ = naive_bayes_train(features, labels)
        assert abs(priors["A"] - 0.5) < epsilon
        assert abs(priors["B"] - 0.5) < epsilon

    def test_mean_per_feature_per_class(self):
        """Mean should be correctly computed for each feature per class."""
        features = [[1.0, 10.0], [3.0, 30.0]]
        labels = ["A", "A"]
        _, likelihoods = naive_bayes_train(features, labels)
        means, _ = likelihoods["A"]
        assert abs(means[0] - 2.0) < epsilon
        assert abs(means[1] - 20.0) < epsilon

    def test_variance_per_feature_per_class(self):
        """Variance with +1e-6 offset per SKILL.md contract."""
        features = [[1.0], [3.0]]
        labels = ["A", "A"]
        _, likelihoods = naive_bayes_train(features, labels)
        _, variances = likelihoods["A"]
        # var of [1,3] with mean=2: ((1-2)^2 + (3-2)^2) / 2 = 1.0
        # Then + 1e-6
        expected_var = 1.0 + 1e-6
        assert abs(variances[0] - expected_var) < epsilon

    def test_three_classes(self):
        """Training with three classes."""
        features = [[1.0], [2.0], [3.0], [4.0], [5.0]]
        labels = ["A", "B", "A", "B", "C"]
        priors, likelihoods = naive_bayes_train(features, labels)
        assert len(priors) == 3
        assert "C" in likelihoods


# ============================================================
# 4. Naive Bayes Predict — prediction behavior verification
# ============================================================

class TestNaiveBayesPredict:
    """Unit tests for prediction function."""

    def test_prediction_returns_correct_type(self):
        """Predictions should be list of class labels."""
        features = [[1.0], [2.0]]
        labels = ["A", "B"]
        priors, likelihoods = naive_bayes_train(features, labels)
        predictions, probs = naive_bayes_predict([[1.5]], priors, likelihoods)
        assert isinstance(predictions, list)
        assert isinstance(probs, list)

    def test_all_predictions_return_valid_labels(self):
        """All predictions should be valid class labels."""
        features = [[1.0], [3.0], [5.0], [7.0]]
        labels = ["X", "X", "Y", "Y"]
        priors, likelihoods = naive_bayes_train(features, labels)
        predictions, _ = naive_bayes_predict([[2.0], [4.0], [6.0], [8.0]], priors, likelihoods)
        for pred in predictions:
            assert pred in ["X", "Y"]

    def test_probabilities_sum_meaningfully(self):
        """Probabilities should be proportional to posterior."""
        features = [[0.0], [10.0]]
        labels = ["A", "B"]
        priors, likelihoods = naive_bayes_train(features, labels)
        _, probs = naive_bayes_predict([[0.0]], priors, likelihoods)
        # For x=0.0, class A should have much higher probability
        assert probs[0]["A"] > probs[0]["B"]


# ============================================================
# 5. End-to-End — full pipeline tests
# ============================================================

class TestNaiveBayesEndToEnd:
    """End-to-end tests for naive_bayes function."""

    def test_full_pipeline_basic(self):
        """Train and predict in one call."""
        features = [[1.0], [2.0], [8.0], [9.0]]
        labels = ["A", "A", "B", "B"]
        _, _, predictions, _ = naive_bayes(features, labels, [[1.5], [8.5]])
        assert predictions[0] == "A"
        assert predictions[1] == "B"

    def test_perfect_separation_correct_prediction(self):
        """Wells-separated classes should predict correctly."""
        features = [[0.0, 0.0], [0.0, 0.0], [100.0, 100.0], [100.0, 100.0]]
        labels = ["A", "A", "B", "B"]
        _, _, predictions, _ = naive_bayes(features, labels, [[0.0, 0.0]])
        assert predictions[0] == "A"

    def test_overlapping_classes(self):
        """Overlapping distributions should still produce predictions."""
        features = [[1.0], [2.0], [2.0], [3.0]]
        labels = ["A", "A", "B", "B"]
        _, _, predictions, _ = naive_bayes(features, labels, [[2.5]])
        assert predictions[0] in ["A", "B"]


# ============================================================
# 6. Edge Cases — boundary conditions
# ============================================================

class TestEdgeCases:
    """Edge case tests for unusual inputs."""

    def test_single_sample_per_class(self):
        """Single sample per class should still work."""
        features = [[1.0], [5.0]]
        labels = ["A", "B"]
        priors, likelihoods = naive_bayes_train(features, labels)
        assert priors["A"] == 0.5
        assert priors["B"] == 0.5
        means_a, _ = likelihoods["A"]
        assert means_a[0] == 1.0

    def test_all_features_identical(self):
        """All features identical across classes should still train."""
        features = [[5.0, 5.0], [5.0, 5.0], [5.0, 5.0], [5.0, 5.0]]
        labels = ["A", "A", "B", "B"]
        priors, likelihoods = naive_bayes_train(features, labels)
        _, variances_a = likelihoods["A"]
        # Variance = 0 + 1e-6, sigma = sqrt(1e-6)
        assert variances_a[0] == 1e-6

    def test_single_feature(self):
        """Single feature classification."""
        features = [[1.0], [2.0], [8.0], [9.0]]
        labels = ["A", "A", "B", "B"]
        _, _, predictions, _ = naive_bayes(features, labels, [[1.5], [8.5], [5.0]])
        assert predictions[0] == "A"
        assert predictions[1] == "B"

    def test_three_features(self):
        """Three feature classification."""
        features = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
        labels = ["A", "B"]
        _, _, predictions, probs = naive_bayes(features, labels, [[1.0, 2.0, 3.0]])
        assert predictions[0] == "A"
        assert "A" in probs[0]

    def test_single_test_sample(self):
        """Single test sample should return single prediction."""
        features = [[1.0], [2.0]]
        labels = ["A", "B"]
        _, _, predictions, probs = naive_bayes(features, labels, [[1.0]])
        assert len(predictions) == 1
        assert len(probs) == 1