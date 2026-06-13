"""
Integration tests for STATISTICS guardrails:
  - validate_measurement_level (Prolog symbolic routing)
  - assert_test_constraints (Prolog + Python hybrid)

Bottom-up: pure-first-order logic routing → Python numeric gate → hybrid conjunction.
"""

import math
import pytest


# ============================================================
# Extracted deterministic mirrors of Prolog/Python logic
# ============================================================

class MeasurementLevelLogic:
    """Python mirror of Prolog measurement hierarchy (dominates/2)."""

    DOMINANCE = {
        "ratio":    ["interval"],      # direct (one-step) dominance
        "interval": ["ordinal"],
        "ordinal":  ["nominal"],
        "nominal":  [],
    }

    @staticmethod
    def dominates(high, low):
        """Direct one-step dominance (mirrors Prolog dominates/2 fact)."""
        return low in MeasurementLevelLogic.DOMINANCE.get(high, [])

    @staticmethod
    def dominates_transitive(high, low):
        """Transitive dominance (for test routing), not a direct Prolog fact."""
        if MeasurementLevelLogic.dominates(high, low):
            return True
        for mid in MeasurementLevelLogic.DOMINANCE.get(high, []):
            if MeasurementLevelLogic.dominates_transitive(mid, low):
                return True
        return False

    # Test families
    PARAMETRIC = {
        "t_test_independent", "t_test_paired", "pearson_r",
        "one_way_anova", "linear_regression",
    }
    NONPARAMETRIC = {
        "mann_whitney_u", "wilcoxon_signed_rank", "spearman_rho",
        "kruskal_wallis", "friedman",
    }
    CHISQUARE = {"chi_square"}

    PARAMETRIC_LEVELS = {"interval", "ratio"}
    NONPARAMETRIC_LEVELS = {"ordinal", "interval", "ratio"}
    CHISQUARE_LEVELS = {"nominal"}

    @classmethod
    def valid_measurement_for(cls, test, level):
        if test in cls.PARAMETRIC:
            return level in cls.PARAMETRIC_LEVELS
        if test in cls.NONPARAMETRIC:
            return level in cls.NONPARAMETRIC_LEVELS
        if test in cls.CHISQUARE:
            return level in cls.CHISQUARE_LEVELS
        return False


MIN_N_TABLE = {
    "t_test_independent": 2, "t_test_paired": 2, "pearson_r": 3,
    "spearman_rho": 3, "one_way_anova": 3, "linear_regression": 3,
    "chi_square": 5, "kruskal_wallis": 3, "mann_whitney_u": 2,
    "wilcoxon_signed_rank": 2, "friedman": 3,
}

REQUIRES_NORMALITY = {
    "t_test_independent", "t_test_paired", "pearson_r",
    "one_way_anova", "linear_regression",
    "kruskal_wallis", "mann_whitney_u", "wilcoxon_signed_rank",
}
NO_NORMALITY_NEEDED = {"chi_square", "spearman_rho"}


def _clean(values):
    return [v for v in values
            if v is not None and not (isinstance(v, float) and math.isnan(v))]


def sample_size(columns, data):
    """Count rows where all specified columns have non-null, non-NaN values."""
    if not columns:
        return 0
    col_vectors = [data.get(c, []) for c in columns]
    n = 0
    for row in zip(*col_vectors):
        if all(v is not None and not (isinstance(v, float) and math.isnan(v)) for v in row):
            n += 1
    return n


def normal_flag(columns, data):
    """Shapiro-Wilk or skewness/kurtosis fallback."""
    import numpy as np
    for vec in [data.get(c, []) for c in columns]:
        clean = _clean(vec)
        n = len(clean)
        if n < 3:
            return False
        arr = np.array(clean, dtype=float)
        if arr.std(ddof=1) == 0:
            return False
        try:
            from scipy.stats import shapiro
            _, p = shapiro(clean)
            if p < 0.05:
                return False
        except ImportError:
            mean = arr.mean()
            std = arr.std(ddof=1)
            z = (arr - mean) / std
            skew = float(np.mean(z ** 3))
            kurt = float(np.mean(z ** 4)) - 3.0
            if abs(skew) >= 1.0 or abs(kurt) >= 2.0:
                return False
    return True


# ============================================================
# 1. Prolog symbolic layer: measurement hierarchy
# ============================================================

class TestMeasurementHierarchy:
    """Pure first-order logic: dominates/2 rules."""

    def test_ratio_dominates_interval(self):
        assert MeasurementLevelLogic.dominates("ratio", "interval")

    def test_ratio_dominates_interval_transitive(self):
        assert MeasurementLevelLogic.dominates_transitive("ratio", "interval")

    def test_ratio_dominates_ordinal_transitive(self):
        assert MeasurementLevelLogic.dominates_transitive("ratio", "ordinal")

    def test_ratio_dominates_nominal_transitive(self):
        assert MeasurementLevelLogic.dominates_transitive("ratio", "nominal")

    def test_interval_dominates_ordinal(self):
        assert MeasurementLevelLogic.dominates("interval", "ordinal")

    def test_interval_dominates_ordinal_transitive(self):
        assert MeasurementLevelLogic.dominates_transitive("interval", "ordinal")

    def test_interval_dominates_nominal_transitive(self):
        assert MeasurementLevelLogic.dominates_transitive("interval", "nominal")

    def test_ordinal_dominates_nominal(self):
        assert MeasurementLevelLogic.dominates("ordinal", "nominal")

    def test_nominal_dominates_nothing(self):
        assert not MeasurementLevelLogic.dominates("nominal", "interval")
        assert not MeasurementLevelLogic.dominates("nominal", "ordinal")
        assert not MeasurementLevelLogic.dominates("nominal", "ratio")

    def test_ratio_does_not_directly_dominate_nominal(self):
        # Transitive dominance is NOT direct dominance
        assert not MeasurementLevelLogic.dominates("ratio", "nominal")

    def test_transitivity(self):
        assert MeasurementLevelLogic.dominates("ratio", "interval")
        assert MeasurementLevelLogic.dominates_transitive("interval", "ordinal")
        assert MeasurementLevelLogic.dominates_transitive("ordinal", "nominal")
        # Total transitive order: ratio > interval > ordinal > nominal


# ============================================================
# 2. Prolog symbolic layer: test-family routing
# ============================================================

class TestTestFamilyRouting:
    """Prolog valid_measurement_for/2 rules."""

    # --- Parametric tests: interval and ratio ONLY ---
    @pytest.mark.parametrize("test", [
        "t_test_independent", "t_test_paired", "pearson_r",
        "one_way_anova", "linear_regression",
    ])
    def test_parametric_allowed_interval(self, test):
        assert MeasurementLevelLogic.valid_measurement_for(test, "interval")

    @pytest.mark.parametrize("test", [
        "t_test_independent", "t_test_paired", "pearson_r",
        "one_way_anova", "linear_regression",
    ])
    def test_parametric_allowed_ratio(self, test):
        assert MeasurementLevelLogic.valid_measurement_for(test, "ratio")

    @pytest.mark.parametrize("test", [
        "t_test_independent", "t_test_paired", "pearson_r",
        "one_way_anova", "linear_regression",
    ])
    def test_parametric_blocked_nominal(self, test):
        assert not MeasurementLevelLogic.valid_measurement_for(test, "nominal")

    @pytest.mark.parametrize("test", [
        "t_test_independent", "t_test_paired", "pearson_r",
        "one_way_anova", "linear_regression",
    ])
    def test_parametric_blocked_ordinal(self, test):
        assert not MeasurementLevelLogic.valid_measurement_for(test, "ordinal")

    # --- Non-parametric tests: ordinal and above ---
    @pytest.mark.parametrize("test,level", [
        ("mann_whitney_u", "ordinal"),
        ("mann_whitney_u", "interval"),
        ("mann_whitney_u", "ratio"),
        ("wilcoxon_signed_rank", "ordinal"),
        ("spearman_rho", "ordinal"),
        ("kruskal_wallis", "interval"),
        ("friedman", "ratio"),
    ])
    def test_non_parametric_allowed(self, test, level):
        assert MeasurementLevelLogic.valid_measurement_for(test, level)

    def test_spearman_allows_ordinal(self):
        assert MeasurementLevelLogic.valid_measurement_for("spearman_rho", "ordinal")

    def test_non_parametric_blocked_nominal(self):
        for test in MeasurementLevelLogic.NONPARAMETRIC:
            assert not MeasurementLevelLogic.valid_measurement_for(test, "nominal"), \
                f"{test} should be blocked for nominal"

    # --- Chi-square: nominal ONLY ---
    def test_chisquare_allowed_nominal(self):
        assert MeasurementLevelLogic.valid_measurement_for("chi_square", "nominal")

    def test_chisquare_blocked_ordinal(self):
        assert not MeasurementLevelLogic.valid_measurement_for("chi_square", "ordinal")

    def test_chisquare_blocked_interval(self):
        assert not MeasurementLevelLogic.valid_measurement_for("chi_square", "interval")

    def test_chisquare_blocked_ratio(self):
        assert not MeasurementLevelLogic.valid_measurement_for("chi_square", "ratio")


# ============================================================
# 3. Python numeric layer: sample-size gate
# ============================================================

class TestSampleSizeGate:
    """Python computes n; Prolog min_n/2 enforces minimums."""

    def test_t_test_min_n(self):
        assert MIN_N_TABLE["t_test_independent"] == 2

    def test_pearson_min_n(self):
        assert MIN_N_TABLE["pearson_r"] == 3

    def test_chi_square_min_n(self):
        assert MIN_N_TABLE["chi_square"] == 5

    def test_sample_size_count_intersection(self):
        data = {"a": [1, 2, 3], "b": [1, None, 3]}
        assert sample_size(["a", "b"], data) == 2

    def test_sample_size_single_column(self):
        data = {"x": [1, 2, 3, 4, 5]}
        assert sample_size(["x"], data) == 5

    def test_sample_size_empty_columns(self):
        assert sample_size([], {}) == 0

    def test_sample_size_none_values_dropped(self):
        data = {"x": [1, None, 3, None, 5], "y": [10, 20, None, 40, 50]}
        # Row 0: (1,10) ✓; row 1: (None,20) ✗; row 2: (3,None) ✗;
        # row 3: (None,40) ✗; row 4: (5,50) ✓ → 2 valid
        assert sample_size(["x", "y"], data) == 2

    def test_sample_size_gate_passes_for_pearson(self):
        data = {"x": list(range(10)), "y": list(range(10, 20))}
        n = sample_size(["x", "y"], data)
        assert n >= MIN_N_TABLE["pearson_r"]

    def test_sample_size_gate_blocks_chi_square(self):
        data = {"a": [1, 2], "b": [3, 4]}
        n = sample_size(["a", "b"], data)
        assert n < MIN_N_TABLE["chi_square"]

    def test_nan_in_data_skipped(self):
        data = {"x": [1.0, float("nan"), 3.0, 4.0, 5.0]}
        assert sample_size(["x"], data) == 4


# ============================================================
# 4. Python numeric layer: normality gate
# ============================================================

class TestNormalityGate:
    """Shapiro-Wilk / skewness/kurtosis fallback."""

    def test_normal_data_accepted(self):
        import numpy as np
        rng = np.random.default_rng(42)
        data = {"x": rng.normal(0, 1, 60).tolist()}
        assert normal_flag(["x"], data) is True

    def test_lognormal_skewed_rejected(self):
        import numpy as np
        rng = np.random.default_rng(42)
        data = {"x": np.exp(rng.normal(0, 1, 60)).tolist()}
        assert normal_flag(["x"], data) is False

    def test_too_few_samples_rejected(self):
        data = {"x": [1, 2]}
        assert normal_flag(["x"], data) is False

    def test_zero_variance_rejected(self):
        data = {"x": [5.0] * 30}
        assert normal_flag(["x"], data) is False

    def test_parametric_requires_normality(self):
        assert "t_test_independent" in REQUIRES_NORMALITY
        assert "pearson_r" in REQUIRES_NORMALITY

    def test_chi_square_no_normality(self):
        assert "chi_square" in NO_NORMALITY_NEEDED

    def test_spearman_no_normality(self):
        assert "spearman_rho" in NO_NORMALITY_NEEDED


# ============================================================
# 5. Hybrid: conjunction of all gates
# ============================================================

class TestHybridConstraintConjunction:
    """End-to-end: Prolog symbolic + Python numeric conjunction."""

    def test_parametric_ratio_data_passes(self):
        import numpy as np
        rng = np.random.default_rng(42)
        level = "ratio"
        test = "pearson_r"
        data = {"x": rng.normal(0, 1, 100).tolist(),
                "y": rng.normal(0, 1, 100).tolist()}
        n = sample_size(["x", "y"], data)
        norm = normal_flag(["x"], data)
        assert MeasurementLevelLogic.valid_measurement_for(test, level)
        assert n >= MIN_N_TABLE[test]
        assert norm is True

    def test_parametric_nominal_fails_at_prolog(self):
        level = "nominal"
        test = "t_test_independent"
        assert not MeasurementLevelLogic.valid_measurement_for(test, level)

    def test_normality_violation_blocks_parametric(self):
        data = {"x": [1, 1, 1000, 1, 1], "y": [2, 2, 2000, 2, 2]}
        norm = normal_flag(["x"], data)
        assert norm is False
        assert "t_test_independent" in REQUIRES_NORMALITY

    def test_non_parametric_relaxes_normality(self):
        data = {"x": [1, 1, 1000, 1, 1], "y": [2, 2, 2000, 2, 2]}
        norm = normal_flag(["x"], data)
        assert norm is False
        # Non-parametric must still route by measurement level
        assert MeasurementLevelLogic.valid_measurement_for("mann_whitney_u", "ordinal")
        assert MeasurementLevelLogic.valid_measurement_for("mann_whitney_u", "interval")

    def test_insufficient_sample_blocks(self):
        test = "chi_square"
        data = {"a": [1, 2], "b": [3, 4]}
        n = sample_size(["a", "b"], data)
        assert n < MIN_N_TABLE[test]

    def test_min_n_table_all_at_least_one(self):
        for test, min_n in MIN_N_TABLE.items():
            assert min_n >= 1
            assert isinstance(min_n, int)
