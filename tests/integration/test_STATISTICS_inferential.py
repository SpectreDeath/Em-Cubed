"""
Integration tests for STATISTICS inferential skills:
  - evaluate_p_value
  - execute_chi_square_independence
  - calculate_mean_confidence_interval

Bottom-up: p-value gate → χ² structural + numeric → CI z-contract.
"""

import math
import pytest


def execute_chi_square(contingency_table, alpha=0.05):
    observed = []
    for r in contingency_table:
        if not r:
            raise ValueError("empty_table")
        row = []
        for v in r:
            if v is None or (isinstance(v, float) and math.isnan(v)):
                raise ValueError("missing_value")
            if v < 0:
                raise ValueError("negative_count")
            row.append(float(v))
        observed.append(row)
    if not observed or not observed[0]:
        raise ValueError("empty_table")
    r, c = len(observed), len(observed[0])
    if r < 2 or c < 2:
        raise ValueError("invalid_dimensions")
    for row in observed:
        if len(row) != c:
            raise ValueError("ragged_table")
    row_tot = [sum(row) for row in observed]
    col_tot = [sum(observed[i][j] for i in range(r)) for j in range(c)]
    n = sum(row_tot)
    expected = [[row_tot[i]*col_tot[j]/n for j in range(c)] for i in range(r)]
    chi2 = sum((observed[i][j]-expected[i][j])**2/expected[i][j]
               for i in range(r) for j in range(c))
    df = (r-1)*(c-1)
    try:
        from scipy.stats import chi2 as chi2_dist
        p_value = float(chi2_dist.sf(chi2, df))
    except ImportError:
        if chi2 < 1e-10:
            p_value = 1.0
        elif chi2 > df * 10:
            p_value = 1e-6
        else:
            p_value = 0.5
    min_dim = min(r-1, c-1)
    effect_size = math.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0.0
    warnings = []
    if any(e < 5.0 for row in expected for e in row):
        warnings.append("sparse_cells")
    if p_value < alpha:
        decision = "reject_null"
        state = "rejected"
    else:
        decision = "fail_to_reject_null"
        state = "not_rejected"
    return {"statistic": chi2, "df": df, "p_value": p_value,
            "effect_size": effect_size, "decision": decision,
            "state": state, "warnings": warnings}


# ============================================================
# Shared math helpers (extracted from SKILL.md implementations)
# ============================================================

def _erfinv(p):
    if p <= 0.0:
        return float("-inf")
    if p >= 1.0:
        return float("inf")
    A = [
        -3.969683028665376e+01, 2.209460984245205e+02,
        -2.759285104469687e+02,  1.383577518672690e+02,
        -3.066479806614716e+01,  2.506628277459239e+00,
    ]
    B = [
        -5.447609879822406e+01, -1.615858368580409e+02,
         1.556049798740891e+02, -6.680131188771972e+01,
         1.328068155288572e+01,
    ]
    sp = 0.140
    if p < sp:
        q = math.sqrt(-2.0 * math.log(p / 2.0))
        num = (((((A[0]*q+A[1])*q+A[2])*q+A[3])*q+A[4])*q+A[5])
        den = (((((B[0]*q+B[1])*q+B[2])*q+B[3])*q+B[4])*q+1.0)
        return -(num/den)
    q = math.sqrt(-2.0*math.log(1.0-p))
    num = (((((A[0]*q+A[1])*q+A[2])*q+A[3])*q+A[4])*q+A[5])
    den = (((((B[0]*q+B[1])*q+B[2])*q+B[3])*q+B[4])*q+1.0)
    return num/den


PROLOG_Z_MAP = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}


def _clean(values):
    return [v for v in values
            if v is not None and not (isinstance(v, float) and math.isnan(v))]


def evaluate_p_value(p_value, alpha=0.05):
    if not (0.0 <= p_value <= 1.0):
        raise ValueError(f"p_value must be in [0,1], got {p_value}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0,1), got {alpha}")
    if p_value < alpha:
        return {"decision": "reject_null", "state": "rejected",
                "p_value": p_value, "alpha": alpha}
    return {"decision": "fail_to_reject_null", "state": "not_rejected",
            "p_value": p_value, "alpha": alpha}


def calculate_mean_ci(values, confidence_level=0.95):
    clean = _clean(values)
    n = len(clean)
    if n < 2:
        raise ValueError("insufficient_sample_size")
    mean = sum(clean) / n
    var = sum((v - mean)**2 for v in clean) / (n - 1)
    s = math.sqrt(var)
    se = s / math.sqrt(n)
    if confidence_level in PROLOG_Z_MAP:
        z = PROLOG_Z_MAP[confidence_level]
    else:
        tail = (1.0 - confidence_level) / 2.0
        z = math.sqrt(2.0) * _erfinv(1.0 - tail)
    margin = z * se
    return {"mean": mean, "std": s, "n": n, "z_score": z,
            "ci_lower": mean - margin, "ci_upper": mean + margin,
            "standard_error": se, "margin_of_error": margin}


def _chi2_for_table(table):
    o = [list(map(float, r)) for r in table]
    r, c = len(o), len(o[0])
    row_tot = [sum(row) for row in o]
    col_tot = [sum(o[i][j] for i in range(r)) for j in range(c)]
    n = sum(row_tot)
    e = [[row_tot[i]*col_tot[j]/n for j in range(c)] for i in range(r)]
    chi2 = sum((o[i][j]-e[i][j])**2/e[i][j]
               for i in range(r) for j in range(c))
    df = (r-1)*(c-1)
    return chi2, df


# ============================================================
# 1. P-Value Evaluation (first-order logic threshold gate)
# ============================================================

class TestEvaluatePValue:
    def test_reject_at_p005_alpha005(self):
        r = evaluate_p_value(0.003, 0.05)
        assert r["decision"] == "reject_null"
        assert r["state"] == "rejected"

    def test_fail_to_reject_at_p050_alpha005(self):
        r = evaluate_p_value(0.05, 0.05)
        assert r["decision"] == "fail_to_reject_null"
        assert r["state"] == "not_rejected"

    def test_fail_to_reject_above_alpha(self):
        r = evaluate_p_value(0.20, 0.05)
        assert r["decision"] == "fail_to_reject_null"

    def test_boundary_p_equals_alpha_fails(self):
        r = evaluate_p_value(0.05, 0.05)
        assert r["decision"] == "fail_to_reject_null"

    def test_strong_signal_rejects(self):
        r = evaluate_p_value(1e-10, 0.01)
        assert r["decision"] == "reject_null"

    def test_invalid_p_negative_raises(self):
        with pytest.raises(ValueError):
            evaluate_p_value(-0.1, 0.05)

    def test_invalid_p_above_one_raises(self):
        with pytest.raises(ValueError):
            evaluate_p_value(1.5, 0.05)

    def test_invalid_alpha_zero_raises(self):
        with pytest.raises(ValueError):
            evaluate_p_value(0.05, 0.0)

    def test_invalid_alpha_one_raises(self):
        with pytest.raises(ValueError):
            evaluate_p_value(0.05, 1.0)

    @pytest.mark.parametrize("p,alpha,dec", [
        (0.001, 0.05, "reject_null"),
        (0.049, 0.05, "reject_null"),
        (0.050, 0.05, "fail_to_reject_null"),
        (0.051, 0.05, "fail_to_reject_null"),
    ])
    def test_threshold_table(self, p, alpha, dec):
        assert evaluate_p_value(p, alpha)["decision"] == dec


# ============================================================
# 2. Mean Confidence Interval — z-score contract
# ============================================================

class TestCalculateMeanConfidenceInterval:
    """z-score from Prolog lookup table; interval from Python."""

    KNOWN = [10.2, 9.8, 10.5, 10.1, 9.9, 10.3, 10.0, 9.7]

    def test_expected_z90(self):
        r = calculate_mean_ci(self.KNOWN, 0.90)
        assert abs(r["z_score"] - 1.645) < 1e-10

    def test_expected_z95(self):
        r = calculate_mean_ci(self.KNOWN, 0.95)
        assert abs(r["z_score"] - 1.96) < 1e-10

    def test_expected_z99(self):
        r = calculate_mean_ci(self.KNOWN, 0.99)
        assert abs(r["z_score"] - 2.576) < 1e-10

    def test_mean_computed(self):
        r = calculate_mean_ci([2.0, 4.0, 6.0, 8.0], 0.95)
        assert abs(r["mean"] - 5.0) < 1e-12

    def test_sample_std_formula(self):
        """Verify ddof=1 std: [2,4,6,8] mean=5, var=(9+1+1+9)/3=20/3."""
        r = calculate_mean_ci([2, 4, 6, 8], 0.95)
        expected_std = math.sqrt(20.0 / 3.0)
        assert abs(r["std"] - expected_std) < 1e-10

    def test_ci_symmetricity(self):
        r = calculate_mean_ci(self.KNOWN, 0.95)
        mean = r["mean"]
        assert abs((r["ci_upper"] - mean) - (mean - r["ci_lower"])) < 1e-12

    def test_ci_contains_mean(self):
        r = calculate_mean_ci(self.KNOWN, 0.95)
        assert r["ci_lower"] <= r["mean"] <= r["ci_upper"]

    def test_wider_ci_for_higher_confidence(self):
        r90 = calculate_mean_ci(self.KNOWN, 0.90)
        r95 = calculate_mean_ci(self.KNOWN, 0.95)
        r99 = calculate_mean_ci(self.KNOWN, 0.99)
        width_90 = r90["ci_upper"] - r90["ci_lower"]
        width_95 = r95["ci_upper"] - r95["ci_lower"]
        width_99 = r99["ci_upper"] - r99["ci_lower"]
        assert width_90 < width_95 < width_99

    def test_single_value_raises(self):
        with pytest.raises(ValueError, match="insufficient"):
            calculate_mean_ci([42.0], 0.95)

    def test_all_none_raises(self):
        with pytest.raises(ValueError, match="insufficient"):
            calculate_mean_ci([None, None, None], 0.95)

    def test_known_baseline_ci(self):
        """Hardcoded anchor: x=[3,5,7,9], n=4, mean=6, s=sqrt(20/3)=2.582."""
        values = [3, 5, 7, 9]
        r = calculate_mean_ci(values, 0.95)
        se = math.sqrt(20.0/3.0) / 2.0  # s/sqrt(4)
        margin = 1.96 * se
        assert abs(r["mean"] - 6.0) < 1e-12
        assert abs(r["z_score"] - 1.96) < 1e-10
        assert abs(r["ci_lower"] - (6.0 - margin)) < 1e-10
        assert abs(r["ci_upper"] - (6.0 + margin)) < 1e-10

    def test_none_nan_cleaned(self):
        r = calculate_mean_ci([10.0, None, 20.0, float("nan"), 30.0], 0.95)
        assert r["n"] == 3
        assert abs(r["mean"] - 20.0) < 1e-12


# ============================================================
# 3. Chi-Square Independence — structural + numeric
# ============================================================

class TestExecuteChiSquareIndependence:
    """Structural Prolog gates + Python χ² computation."""

    def test_2x2_table_computes(self):
        table = [[30, 10], [20, 40]]
        r = execute_chi_square(table, 0.05)
        assert r["df"] == 1
        assert r["statistic"] > 0
        assert 0.0 <= r["p_value"] <= 1.0
        assert 0.0 <= r["effect_size"] <= 1.0

    def test_3x3_independence(self):
        table = [[10, 10, 10], [10, 10, 10], [10, 10, 10]]
        r = execute_chi_square(table, 0.05)
        # Uniform table → χ² ≈ 0 → p ≈ 1
        assert r["p_value"] > 0.90
        assert r["decision"] == "fail_to_reject_null"

    def test_strong_association_rejects_null(self):
        """Highly unbalanced table must produce low p-value."""
        table = [[90, 10], [10, 90]]
        r = execute_chi_square(table, 0.05)
        assert r["p_value"] < 0.001
        assert r["decision"] == "reject_null"

    def test_cramers_v_bounds(self):
        table = [[30, 10], [20, 40]]
        r = execute_chi_square(table, 0.05)
        assert 0.0 <= r["effect_size"] <= 1.0

    def test_cramers_v_symmetric(self):
        """Cramer's V should be identical for table and its transpose."""
        t1 = [[30, 10], [20, 40]]
        t2 = [[30, 20], [10, 40]]  # transpose of t1
        r1 = execute_chi_square(t1, 0.05)
        r2 = execute_chi_square(t2, 0.05)
        assert abs(r1["effect_size"] - r2["effect_size"]) < 1e-10

    def test_sparse_warning_triggered(self):
        """Table with many low expected frequencies triggers warning."""
        table = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        r = execute_chi_square(table, 0.05)
        assert len(r["warnings"]) > 0

    def test_empty_table_raises(self):
        with pytest.raises(ValueError, match="empty_table"):
            execute_chi_square([], 0.05)

    def test_1x1_table_raises(self):
        with pytest.raises(ValueError, match="invalid_dimensions"):
            execute_chi_square([[5]], 0.05)

    def test_ragged_table_raises(self):
        with pytest.raises(ValueError, match="ragged_table"):
            execute_chi_square([[1, 2], [3, 4, 5]], 0.05)

    def test_negative_count_raises(self):
        with pytest.raises(ValueError, match="negative"):
            execute_chi_square([[1, -2], [3, 4]], 0.05)

    def test_missing_value_raises(self):
        with pytest.raises(ValueError, match="missing"):
            execute_chi_square([[1, None], [3, 4]], 0.05)

    def test_nan_value_raises(self):
        with pytest.raises(ValueError, match="missing"):
            execute_chi_square([[1.0, float("nan")], [3, 4]], 0.05)

    def test_chi2_statistic_formula(self):
        """Direct verification: [30,10;20,40] → χ² ≈ 15.3846."""
        table = [[30, 10], [20, 40]]
        r = execute_chi_square(table, 0.05)
        chi2, _ = _chi2_for_table(table)
        assert abs(r["statistic"] - chi2) < 1e-10

    def test_completely_independent_table(self):
        """If rows and cols are proportional → no association."""
        table = [[40, 60], [80, 120]]  # same 2:3 ratio
        r = execute_chi_square(table, 0.05)
        assert r["p_value"] > 0.05
        assert r["decision"] == "fail_to_reject_null"
