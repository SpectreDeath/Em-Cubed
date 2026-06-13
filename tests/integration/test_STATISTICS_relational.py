"""
Integration tests for STATISTICS relational skills:
  - calculate_correlation_profile
  - fit_linear_regression

Bottom-up: Pearson r → Spearman rho → OLS regression with R² and t-stat.
"""

import math
import pytest


# ============================================================
# Shared math helpers
# ============================================================

def _clean_pairs(x, y):
    dropped = 0
    cx, cy = [], []
    for a, b in zip(x, y):
        a_ok = a is not None and not (isinstance(a, float) and math.isnan(a))
        b_ok = b is not None and not (isinstance(b, float) and math.isnan(b))
        if a_ok and b_ok:
            cx.append(float(a))
            cy.append(float(b))
        else:
            dropped += 1
    return cx, cy, dropped


def _pearson_r(x, y):
    n = len(x)
    if n < 2:
        return float("nan")
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx)*(yi - my) for xi, yi in zip(x, y))
    dx = math.sqrt(sum((xi - mx)**2 for xi in x))
    dy = math.sqrt(sum((yi - my)**2 for yi in y))
    denom = dx * dy
    if denom == 0:
        return 0.0
    return num / denom


def _spearman_rho(x, y):
    def rank(v):
        indexed = sorted(enumerate(v), key=lambda p: p[1])
        ranks = [0.0] * len(v)
        i = 0
        while i < len(indexed):
            j = i
            while j < len(indexed)-1 and indexed[j+1][1] == indexed[j][1]:
                j += 1
            avg = sum(range(i+1, j+2)) / (j-i+1)
            for k in range(i, j+1):
                ranks[indexed[k][0]] = avg
            i = j + 1
        return ranks
    rx, ry = rank(x), rank(y)
    return _pearson_r(rx, ry)


_MAGNITUDE_BANDS = [
    (0.90, "very_strong"), (0.70, "strong"), (0.40, "moderate"),
    (0.10, "weak"), (0.00, "negligible"),
]

def _magnitude_band(abs_r):
    for threshold, label in _MAGNITUDE_BANDS:
        if abs_r >= threshold:
            return label
    return "negligible"


def _r_pvalue(r, n):
    if n < 3:
        return 1.0
    denom = 1.0 - r*r
    if denom <= 0:
        return 0.0
    t_stat = abs(r * math.sqrt((n-2) / denom))
    try:
        from scipy.stats import t as t_dist
        return float(2.0 * t_dist.sf(t_stat, n-2))
    except ImportError:
        return 2.0 * (1.0 - _normal_cdf(t_stat, 0.0, 1.0))


def _normal_cdf(x, mu, sigma):
    return 0.5 * (1.0 + math.erf((x-mu)/(sigma*math.sqrt(2.0))))


def calculate_correlation_profile(x, y, method="pearson"):
    if method not in ("pearson", "spearman"):
        raise ValueError(f"method must be pearson or spearman")
    cx, cy, dropped = _clean_pairs(x, y)
    n_used = len(cx)
    if n_used < 3:
        raise ValueError("insufficient_pairs")
    if method == "pearson":
        r_val = _pearson_r(cx, cy)
    else:
        r_val = _spearman_rho(cx, cy)
    r_val = max(-1.0, min(1.0, r_val))
    p_val = _r_pvalue(r_val, n_used)
    mag = _magnitude_band(abs(r_val))
    return {"method": method, "r": r_val, "rho": r_val,
            "p_value": p_val, "magnitude": mag,
            "n": len(x), "n_used": n_used, "n_dropped": dropped}


def fit_linear_regression(x, y):
    cx, cy, dropped = _clean_pairs(x, y)
    n = len(cx)
    if n < 3:
        raise ValueError("insufficient_sample")
    x_bar = sum(cx) / n
    y_bar = sum(cy) / n
    ss_xy = sum((xi-x_bar)*(yi-y_bar) for xi, yi in zip(cx, cy))
    ss_xx = sum((xi-x_bar)**2 for xi in cx)
    if ss_xx == 0:
        raise ValueError("zero_variance")
    beta_1 = ss_xy / ss_xx
    beta_0 = y_bar - beta_1 * x_bar
    ss_yy = sum((yi-y_bar)**2 for yi in cy)
    r_squared = (ss_xy**2) / (ss_xx * ss_yy) if ss_yy != 0 else 0.0
    residuals = [yi - (beta_0 + beta_1*xi) for xi, yi in zip(cx, cy)]
    ss_res = sum(e*e for e in residuals)
    df = n - 2
    mse = ss_res / df if df > 0 else 0.0
    se_b1 = math.sqrt(mse / ss_xx)
    t_stat = beta_1 / se_b1 if se_b1 > 0 else 0.0
    try:
        from scipy.stats import t as t_dist
        p_value = float(2.0 * t_dist.sf(abs(t_stat), df))
    except ImportError:
        p_value = 2.0 * (1.0 - _normal_cdf(abs(t_stat), 0.0, 1.0))
    return {"beta_0": beta_0, "beta_1": beta_1, "r_squared": r_squared,
            "std_err_beta1": se_b1, "t_stat": t_stat, "p_value": p_value,
            "n": len(x), "df": df, "n_used": n, "n_dropped": dropped,
            "residuals": residuals}


# ============================================================
# 1. Pearson r
# ============================================================

class TestCalculateCorrelationProfilePearson:
    """Deterministic hardness: sign, magnitude, p-value contract."""

    X = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    Y = [2.1, 3.9, 6.2, 7.8, 10.1, 11.9, 14.2, 15.8]

    def test_perfect_linear_positive(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        r = calculate_correlation_profile(x, y, method="pearson")
        assert abs(r["r"] - 1.0) < 1e-12

    def test_perfect_linear_negative(self):
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        r = calculate_correlation_profile(x, y, method="pearson")
        assert abs(r["r"] + 1.0) < 1e-12

    def test_no_correlation(self):
        import random
        rng = random.Random(42)
        x = list(range(20))
        y = [rng.gauss(5, 2) for _ in range(20)]
        r = calculate_correlation_profile(x, y, method="pearson")
        assert abs(r["r"]) < 0.5  # random noise → near-zero correlation

    def test_known_strong_correlation(self):
        r = calculate_correlation_profile(self.X, self.Y, method="pearson")
        assert r["r"] > 0.9
        assert r["magnitude"] == "very_strong"

    def test_symmetry(self):
        r_xy = calculate_correlation_profile(self.X, self.Y, method="pearson")
        r_yx = calculate_correlation_profile(self.Y, self.X, method="pearson")
        assert abs(r_xy["r"] - r_yx["r"]) < 1e-12

    def test_p_value_decreases_with_stronger_r(self):
        weak_x = list(range(50))
        weak_y = [v + 0.5*((v % 3)-1) for v in range(50)]
        strong_x = list(range(50))
        strong_y = [2.0*v + 0.01 for v in range(50)]
        r_w = calculate_correlation_profile(weak_x, weak_y, method="pearson")
        r_s = calculate_correlation_profile(strong_x, strong_y, method="pearson")
        assert r_s["p_value"] < r_w["p_value"]

    def test_invalid_method_raises(self):
        with pytest.raises(ValueError, match="method must"):
            calculate_correlation_profile([1, 2], [1, 2], method="invalid")

    def test_insufficient_pairs_raises(self):
        with pytest.raises(ValueError, match="insufficient_pairs"):
            calculate_correlation_profile([1, 2], [1, 2], method="pearson")

    def test_none_cleaned(self):
        x = [1.0, None, 3.0, 4.0, 5.0]
        y = [2.0, 3.0, None, 8.0, 10.0]
        r = calculate_correlation_profile(x, y, method="pearson")
        assert r["n_used"] == 3
        assert r["n_dropped"] == 2


# ============================================================
# 2. Spearman rho
# ============================================================

class TestCalculateCorrelationProfileSpearman:
    def test_monotonic_increasing(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 20.0, 30.0, 40.0, 50.0]
        r = calculate_correlation_profile(x, y, method="spearman")
        assert abs(r["r"] - 1.0) < 1e-12
        assert r["magnitude"] == "very_strong"

    def test_monotonic_decreasing(self):
        x = [5.0, 4.0, 3.0, 2.0, 1.0]
        y = [1.0, 2.0, 3.0, 4.0, 5.0]
        r = calculate_correlation_profile(x, y, method="spearman")
        assert abs(r["r"] + 1.0) < 1e-12
        assert abs(r["rho"] + 1.0) < 1e-12

    def test_spearman_handles_ties(self):
        x = [1.0, 2.0, 2.0, 3.0, 4.0]
        y = [2.0, 4.0, 4.0, 6.0, 8.0]
        r = calculate_correlation_profile(x, y, method="spearman")
        assert abs(r["r"] - 1.0) < 1e-10

    def test_spearman_different_from_pearson_for_nonlinear(self):
        """Monotonic but nonlinear: Spearman should be high, Pearson lower."""
        x = list(range(1, 21))
        y = [v**2 for v in x]
        r_p = calculate_correlation_profile(x, y, method="pearson")
        r_s = calculate_correlation_profile(x, y, method="spearman")
        assert r_s["r"] > r_p["r"]


# ============================================================
# 3. Linear Regression OLS
# ============================================================

class TestFitLinearRegression:
    """OLS: coefficients, R², residual constraints, t-stat."""

    def test_perfect_fit(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        r = fit_linear_regression(x, y)
        assert abs(r["beta_0"]) < 1e-12  # intercept ~0
        assert abs(r["beta_1"] - 2.0) < 1e-12  # slope = 2
        assert abs(r["r_squared"] - 1.0) < 1e-12

    def test_intercept_nonzero(self):
        x = [1, 2, 3, 4, 5]
        y = [3, 5, 7, 9, 11]  # y = 1 + 2x
        r = fit_linear_regression(x, y)
        assert abs(r["beta_0"] - 1.0) < 1e-12
        assert abs(r["beta_1"] - 2.0) < 1e-12
        assert abs(r["r_squared"] - 1.0) < 1e-12

    def test_noisy_data_r_squared_less_than_one(self):
        x = list(range(50))
        y = [2.0*v + 1.0 + 0.5*((v % 3) - 1) for v in range(50)]
        r = fit_linear_regression(x, y)
        assert 0.0 < r["r_squared"] < 1.0
        assert abs(r["beta_1"] - 2.0) < 0.5

    def test_residuals_sum_near_zero(self):
        x = [1, 2, 3, 4, 5]
        y = [2.1, 3.9, 6.2, 7.8, 10.1]
        r = fit_linear_regression(x, y)
        assert abs(sum(r["residuals"])) < 1e-10

    def test_residuals_correctness_perfect(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        r = fit_linear_regression(x, y)
        assert all(abs(e) < 1e-12 for e in r["residuals"])

    def test_slope_sign_matches_correlation(self):
        x = list(range(20))
        y_pos = [v + 0.1 for v in range(20)]
        y_neg = [-v + 20 for v in range(20)]
        r_pos = fit_linear_regression(x, y_pos)
        r_neg = fit_linear_regression(x, y_neg)
        assert r_pos["beta_1"] > 0
        assert r_neg["beta_1"] < 0

    def test_degrees_of_freedom(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8]
        y = [2, 4, 6, 8, 10, 12, 14, 16]
        r = fit_linear_regression(x, y)
        assert r["df"] == 6  # n - 2

    def test_n_used_matches_clean_pairs(self):
        x = [1, None, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        r = fit_linear_regression(x, y)
        assert r["n_used"] == 4
        assert r["n_dropped"] == 1

    def test_insufficient_raises(self):
        with pytest.raises(ValueError, match="insufficient"):
            fit_linear_regression([1, 2], [1, 2])

    def test_zero_variance_raises(self):
        with pytest.raises(ValueError, match="zero_variance"):
            fit_linear_regression([5, 5, 5, 5], [1, 2, 3, 4])

    def test_significant_slope_has_low_pvalue(self):
        x = list(range(100))
        y = [3.0*v + 2.0 + 0.001 for v in range(100)]
        r = fit_linear_regression(x, y)
        assert r["p_value"] < 1e-20

    def test_known_baseline_values(self):
        """Hand-computed OLS: x=[1,2,3,4], y=[2,4,5,4]."""
        x = [1.0, 2.0, 3.0, 4.0]
        y = [2.0, 4.0, 5.0, 4.0]
        r = fit_linear_regression(x, y)
        x_bar, y_bar = 2.5, 3.75
        ss_xy = sum((xi-x_bar)*(yi-y_bar) for xi, yi in zip(x, y))
        ss_xx = sum((xi-x_bar)**2 for xi in x)
        expected_b1 = ss_xy / ss_xx
        expected_b0 = y_bar - expected_b1 * x_bar
        assert abs(r["beta_1"] - expected_b1) < 1e-10
        assert abs(r["beta_0"] - expected_b0) < 1e-10
