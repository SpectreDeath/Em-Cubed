"""
Integration tests for STATISTICS descriptive skills:
  - calculate_central_tendency
  - calculate_dispersion

Bottom-up: pure algorithmic units → verified against hand-computed baselines.
"""

import math
import pytest

# ============================================================
# Function-under-test extracted from SKILL.md implementations
# ============================================================

from collections import Counter


def _clean(values):
    out = []
    dropped = 0
    for v in values:
        if v is None:
            dropped += 1
            continue
        if isinstance(v, str):
            try:
                v = float(v)
            except (ValueError, TypeError):
                dropped += 1
                continue
        if isinstance(v, float) and math.isnan(v):
            dropped += 1
            continue
        out.append(float(v))
    return out, dropped


def calculate_central_tendency(values):
    clean, dropped = _clean(values)
    n = len(clean)
    if n == 0:
        raise ValueError("empty_series")
    s = sorted(clean)
    mean = sum(s) / n
    if n % 2 == 1:
        median = s[n // 2]
    else:
        median = (s[n // 2 - 1] + s[n // 2]) / 2.0
    counts = Counter(s)
    max_count = max(counts.values())
    modes = sorted([k for k, v in counts.items() if v == max_count])
    multimodal = len(modes) > 1
    return {
        "mean": mean, "median": median,
        "mode": modes if multimodal else modes[0],
        "multimodal": multimodal,
        "n": n, "n_original": len(values), "n_dropped": dropped,
    }


def _percentile(sorted_values, pct):
    n = len(sorted_values)
    if n == 0:
        raise ValueError("empty_series")
    if n == 1:
        return sorted_values[0]
    rank = (pct / 100.0) * (n - 1)
    lower = int(math.floor(rank))
    upper = int(math.ceil(rank))
    if lower == upper:
        return sorted_values[lower]
    frac = rank - lower
    return sorted_values[lower] * (1 - frac) + sorted_values[upper] * frac


def calculate_dispersion(values):
    clean, dropped = _clean(values)
    n = len(clean)
    if n == 0:
        raise ValueError("empty_series")
    s = sorted(clean)
    range_val = s[-1] - s[0]
    mean_val = sum(s) / n
    sum_sq_diff = sum((v - mean_val) ** 2 for v in s)
    variance_pop = sum_sq_diff / n if n > 0 else 0.0
    variance_samp = sum_sq_diff / (n - 1) if n > 1 else 0.0
    std_pop = math.sqrt(variance_pop)
    std_samp = math.sqrt(variance_samp)
    q75 = _percentile(s, 75.0)
    q25 = _percentile(s, 25.0)
    iqr = q75 - q25
    return {
        "range": range_val, "variance": variance_pop,
        "variance_sample": variance_samp,
        "std": std_pop, "std_sample": std_samp, "iqr": iqr,
        "n": n, "n_original": len(values), "n_dropped": dropped,
    }


# ============================================================
# 1. Central Tendency — odd vs even median branches
# ============================================================

class TestCalculateCentralTendency:
    """Unit tests with hand-verified baselines."""

    def test_odd_count_median(self):
        """Median is the middle element for odd n."""
        result = calculate_central_tendency([1, 3, 5, 7, 9])
        assert result["n"] == 5
        assert result["mean"] == 5.0
        assert result["median"] == 5.0
        assert result["multimodal"] is True
        assert set(result["mode"]) == {1.0, 3.0, 5.0, 7.0, 9.0}

    def test_even_count_median(self):
        """Median is the average of the two middle elements for even n."""
        result = calculate_central_tendency([1, 2, 3, 4])
        assert result["n"] == 4
        assert result["mean"] == 2.5
        assert result["median"] == 2.5  # (2 + 3) / 2

    def test_even_count_median_fractional(self):
        """Even n with non-integer midpoint average."""
        result = calculate_central_tendency([10, 20, 30, 40])
        assert result["median"] == 25.0  # (20 + 30) / 2

    def test_mode_single(self):
        result = calculate_central_tendency([1, 2, 2, 3, 4])
        assert result["mode"] == 2.0
        assert result["multimodal"] is False

    def test_mode_multimodal(self):
        result = calculate_central_tendency([1, 1, 2, 2, 3])
        assert result["mode"] == [1.0, 2.0]
        assert result["multimodal"] is True

    def test_mode_all_unique(self):
        result = calculate_central_tendency([10, 20, 30])
        assert result["multimodal"] is True
        assert set(result["mode"]) == {10.0, 20.0, 30.0}

    def test_mean_basic(self):
        result = calculate_central_tendency([2, 4, 6, 8])
        assert result["mean"] == 5.0

    def test_none_values_dropped(self):
        result = calculate_central_tendency([1, None, 3, None, 5])
        assert result["n"] == 3
        assert result["n_dropped"] == 2
        assert result["mean"] == 3.0

    def test_nan_values_dropped(self):
        result = calculate_central_tendency([1.0, float("nan"), 3.0])
        assert result["n"] == 2
        assert result["mean"] == 2.0

    def test_string_coercion(self):
        result = calculate_central_tendency(["1", "2", "3", "x", "5"])
        assert result["n"] == 4
        assert result["n_dropped"] == 1
        assert result["mean"] == 2.75

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty_series"):
            calculate_central_tendency([])
        with pytest.raises(ValueError, match="empty_series"):
            calculate_central_tendency([None, None, float("nan")])

    def test_negative_values(self):
        result = calculate_central_tendency([-5, -3, -1, 1, 3])
        assert result["mean"] == -1.0
        assert result["median"] == -1.0

    def test_n_original_preserved(self):
        values = [1, 2, None, 4, float("nan"), 6]
        result = calculate_central_tendency(values)
        assert result["n_original"] == 6
        assert result["n"] == 4
        assert result["n_dropped"] == 2


# ============================================================
# 2. Dispersion — verified against standard formulas
# ============================================================

class TestCalculateDispersion:
    """Unit tests with hand-verified baselines."""

    def test_range_basic(self):
        result = calculate_dispersion([10, 20, 30, 40])
        assert result["range"] == 30.0

    def test_population_variance(self):
        """Var([1,2,3,4]) = ((1-2.5)^2 + ... + (4-2.5)^2) / 4 = 1.25."""
        result = calculate_dispersion([1, 2, 3, 4])
        assert abs(result["variance"] - 1.25) < 1e-12
        assert abs(result["std"] - math.sqrt(1.25)) < 1e-12

    def test_sample_variance(self):
        """Var_sample([1,2,3,4]) = sum((x-mean)^2) / 3 = 5/3."""
        result = calculate_dispersion([1, 2, 3, 4])
        assert abs(result["variance_sample"] - 5.0 / 3.0) < 1e-12
        assert abs(result["std_sample"] - math.sqrt(5.0 / 3.0)) < 1e-12

    def test_iqr_basic(self):
        result = calculate_dispersion([10, 20, 30, 40, 50, 60, 70, 80])
        assert abs(result["iqr"] - 35.0) < 0.1

    def test_single_element(self):
        result = calculate_dispersion([42.0])
        assert result["range"] == 0.0
        assert result["variance"] == 0.0
        assert result["std"] == 0.0
        assert result["n"] == 1

    def test_constant_values(self):
        result = calculate_dispersion([7, 7, 7, 7])
        assert result["range"] == 0.0
        assert result["variance"] == 0.0
        assert result["std"] == 0.0

    def test_nan_dropped(self):
        result = calculate_dispersion([1.0, float("nan"), 3.0, 5.0])
        assert result["n"] == 3
        assert result["range"] == 4.0

    def test_n_original_preserved(self):
        values = [1, None, 3, 4]
        result = calculate_dispersion(values)
        assert result["n_original"] == 4
        assert result["n"] == 3
        assert result["n_dropped"] == 1

    def test_population_vs_sample_relationship(self):
        """Population std should be smaller than sample std for same data."""
        result = calculate_dispersion([1, 2, 3, 4, 5])
        assert result["std"] < result["std_sample"]

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty_series"):
            calculate_dispersion([])
        with pytest.raises(ValueError, match="empty_series"):
            calculate_dispersion([None] * 5)

    def test_large_uniform(self):
        """Uniform [0..99]: expected variance ≈ (100^2-1)/12 ≈ 825."""
        values = list(range(100))
        result = calculate_dispersion(values)
        expected_var = (100**2 - 1) / 12.0
        assert abs(result["variance"] - expected_var) < 1.0
