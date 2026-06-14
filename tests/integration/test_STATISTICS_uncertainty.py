import random
import math


def _normal_sample(mean, std, n):
    return [random.gauss(mean, std) for _ in range(n)]


def _uniform_sample(low, high, n):
    return [random.uniform(low, high) for _ in range(n)]


def _beta_sample(alpha, beta, n):
    return [random.betavariate(alpha, beta) for _ in range(n)]


def _triangular_sample(left, mode, right, n):
    return [random.triangular(left, mode, right) for _ in range(n)]


def _percentile(sorted_data, q):
    if not sorted_data:
        return 0
    k = (len(sorted_data) - 1) * q / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[int(f)] * (c - k) + sorted_data[int(c)] * (k - f)


def _confidence_belt(estimates, confidence=0.95):
    alpha = 1 - confidence
    sorted_estimates = sorted(estimates)
    lower = _percentile(sorted_estimates, alpha / 2 * 100)
    upper = _percentile(sorted_estimates, (1 - alpha / 2) * 100)
    median = _percentile(sorted_estimates, 50)
    return {"lower": lower, "median": median, "upper": upper}


def _risk_level(probability, impact):
    return probability * impact


def _risk_category(risk):
    if risk > 0.7:
        return "high"
    elif risk > 0.3:
        return "medium"
    else:
        return "low"


def _complementary_confidence(*confidences):
    product = 1.0
    for ci in confidences:
        product *= (1 - ci)
    return 1 - product


class TestUncertaintyDistribution:
    def test_normal_sampling(self):
        random.seed(42)
        n = 1000
        samples = _normal_sample(0, 1, n)
        assert len(samples) == n
        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        std = math.sqrt(variance)
        assert abs(mean) < 0.1, f"Mean {mean} should be ≈ 0"
        assert abs(std - 1) < 0.1, f"Std {std} should be ≈ 1"

    def test_uniform_sampling(self):
        random.seed(42)
        n = 1000
        samples = _uniform_sample(0, 1, n)
        assert len(samples) == n
        assert all(0 <= v <= 1 for v in samples), "All values should be in [0,1]"

    def test_beta_sampling(self):
        random.seed(42)
        n = 1000
        alpha, beta = 2, 5
        samples = _beta_sample(alpha, beta, n)
        assert len(samples) == n
        assert all(0 <= v <= 1 for v in samples), "All values should be in [0,1]"
        mean = sum(samples) / len(samples)
        expected_mean = alpha / (alpha + beta)
        assert abs(mean - expected_mean) < 0.05, f"Mean {mean} should be ≈ {expected_mean}"

    def test_triangular_sampling(self):
        random.seed(42)
        n = 1000
        left, mode, right = 0, 5, 10
        samples = _triangular_sample(left, mode, right, n)
        assert len(samples) == n
        assert all(left <= v <= right for v in samples), "All values should be in [left, right]"
        mean = sum(samples) / len(samples)
        expected_mean = (left + mode + right) / 3
        assert abs(mean - expected_mean) < 0.5, f"Mean {mean} should be ≈ {expected_mean}"


class TestConfidenceBelt:
    def test_percentile_based_ci_computation(self):
        sorted_data = [i for i in range(1, 101)]
        result = _confidence_belt(sorted_data, 0.95)
        assert result["lower"] < result["median"] < result["upper"]
        assert result["median"] == 50.5

    def test_median_is_50th_percentile(self):
        random.seed(42)
        samples = _normal_sample(100, 15, 99)
        result = _confidence_belt(samples, 0.95)
        assert 90 < result["median"] < 110


class TestRiskLevel:
    def test_risk_equals_probability_times_impact(self):
        risk = _risk_level(0.5, 0.8)
        assert risk == 0.4

    def test_high_risk_threshold(self):
        assert _risk_category(0.8) == "high"
        assert _risk_category(0.71) == "high"
        assert _risk_category(0.7) == "medium"

    def test_medium_risk_threshold(self):
        assert _risk_category(0.5) == "medium"
        assert _risk_category(0.31) == "medium"
        assert _risk_category(0.3) == "low"

    def test_low_risk_threshold(self):
        assert _risk_category(0.2) == "low"
        assert _risk_category(0.0) == "low"


class TestComplementaryConfidence:
    def test_single_confidence_unchanged(self):
        result = _complementary_confidence(0.8)
        assert result == 0.8

    def test_two_confidences(self):
        result = _complementary_confidence(0.6, 0.7)
        expected = 1 - (1 - 0.6) * (1 - 0.7)
        assert abs(result - expected) < 1e-10

    def test_three_confidences(self):
        c1, c2, c3 = 0.6, 0.7, 0.5
        result = _complementary_confidence(c1, c2, c3)
        expected = 1 - (1 - c1) * (1 - c2) * (1 - c3)
        assert abs(result - expected) < 1e-10