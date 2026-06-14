import random


class BootstrapAnalyzer:
    def __init__(self, data, n_bootstrap=10000):
        self.data = list(data)
        self.n_bootstrap = n_bootstrap
        self.bootstrap_samples = None

    def bootstrap_sample(self, statistic=None):
        statistic = statistic or self._mean
        self.bootstrap_samples = [
            statistic(self._resample()) for _ in range(self.n_bootstrap)
        ]
        return self.bootstrap_samples

    def _resample(self):
        return [random.choice(self.data) for _ in range(len(self.data))]

    @staticmethod
    def _mean(sample):
        return sum(sample) / len(sample)

    @staticmethod
    def _variance(sample):
        mean = sum(sample) / len(sample)
        return sum((x - mean) ** 2 for x in sample) / len(sample)

    def confidence_interval(self, alpha=0.05):
        if self.bootstrap_samples is None:
            self.bootstrap_sample()
        sorted_samples = sorted(self.bootstrap_samples)
        lower_idx = int(len(sorted_samples) * alpha / 2)
        upper_idx = int(len(sorted_samples) * (1 - alpha / 2)) - 1
        return (sorted_samples[lower_idx], sorted_samples[upper_idx])


class TestBootstrapAnalyzer:
    def test_bootstrap_sample_returns_correct_length(self):
        random.seed(42)
        data = [1, 2, 3, 4, 5]
        analyzer = BootstrapAnalyzer(data, n_bootstrap=1000)
        samples = analyzer.bootstrap_sample()
        assert len(samples) == 1000

    def test_bootstrap_sample_with_custom_statistic(self):
        random.seed(42)
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        analyzer = BootstrapAnalyzer(data, n_bootstrap=1000)
        samples = analyzer.bootstrap_sample(statistic=analyzer._variance)
        assert len(samples) == 1000
        assert all(s >= 0 for s in samples)

    def test_confidence_interval_contains_true_mean_for_normal_data(self):
        random.seed(42)
        data = [random.gauss(50, 10) for _ in range(100)]
        analyzer = BootstrapAnalyzer(data, n_bootstrap=5000)
        ci = analyzer.confidence_interval(alpha=0.05)
        assert ci[0] < 50 < ci[1], f"CI ({ci[0]}, {ci[1]}) should contain true mean 50"

    def test_confidence_interval_narrows_with_more_bootstrap_samples(self):
        random.seed(42)
        data = [random.gauss(50, 10) for _ in range(100)]
        analyzer_small = BootstrapAnalyzer(data, n_bootstrap=1000)
        ci_small = analyzer_small.confidence_interval(alpha=0.05)
        analyzer_large = BootstrapAnalyzer(data, n_bootstrap=10000)
        ci_large = analyzer_large.confidence_interval(alpha=0.05)
        width_small = ci_small[1] - ci_small[0]
        width_large = ci_large[1] - ci_large[0]
        assert width_large < width_small, "More samples should produce narrower CI"

    def test_confidence_interval_for_known_dataset(self):
        random.seed(42)
        data = [1, 2, 3, 4, 5]
        analyzer = BootstrapAnalyzer(data, n_bootstrap=5000)
        ci = analyzer.confidence_interval(alpha=0.05)
        assert ci[0] <= 3 <= ci[1], f"CI ({ci[0]}, {ci[1]}) should contain true mean 3"

    def test_bootstrap_on_constant_data(self):
        random.seed(42)
        data = [5.0] * 100
        analyzer = BootstrapAnalyzer(data, n_bootstrap=100)
        samples = analyzer.bootstrap_sample()
        assert all(s == 5.0 for s in samples), "All samples should equal the constant value"
        ci = analyzer.confidence_interval(alpha=0.05)
        assert ci[0] == ci[1] == 5.0, "CI should be a point for constant data"