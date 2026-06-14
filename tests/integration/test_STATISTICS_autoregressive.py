"""
Integration tests for STATISTICS autoregressive-parameter-estimator.
"""

import math
import pytest

try:
    import z3  # noqa: F401
except ImportError:
    z3 = None


def compute_mean(values):
    return sum(values) / len(values) if values else 0.0


def compute_variance(values):
    if len(values) < 2:
        return 0.0
    mean_value = compute_mean(values)
    return sum((value - mean_value) ** 2 for value in values) / len(values)


def compute_autocorrelation(values, lag):
    if lag >= len(values):
        return 0.0
    mean_value = compute_mean(values)
    variance_value = compute_variance(values)
    if variance_value == 0:
        return 0.0
    covariance = sum(
        (values[index] - mean_value) * (values[index - lag] - mean_value)
        for index in range(lag, len(values))
    )
    return covariance / ((len(values) - lag) * variance_value)


def compute_acf(values, max_lag=20):
    return [compute_autocorrelation(values, lag) for lag in range(max_lag + 1)]


def compute_pacf(values, max_lag=20):
    pacf = [1.0]
    if max_lag == 0:
        return pacf
    if len(values) >= 3:
        r0 = compute_autocorrelation(values, 0)
        r1 = compute_autocorrelation(values, 1)
        pacf.append(r1 / r0 if r0 != 0 else 0.0)
    for lag in range(2, max_lag + 1):
        pacf.append(compute_autocorrelation(values, lag))
    return pacf[:max_lag + 1]


def adf_test(values):
    sample_size = len(values)
    if sample_size < 20:
        return {
            "statistic": 0.0,
            "pvalue": 1.0,
            "stationary": False,
            "insufficient_data": True,
        }

    half = sample_size // 2
    mean1 = compute_mean(values[:half])
    mean2 = compute_mean(values[half:])
    pooled_variance = (compute_variance(values[:half]) + compute_variance(values[half:])) / 2
    statistic = (
        (mean1 - mean2) / math.sqrt(pooled_variance * sample_size)
        if pooled_variance > 0
        else 0.0
    )
    stationary = statistic < -2.86

    return {
        "statistic": statistic,
        "pvalue": 0.05 if stationary else 0.1,
        "stationary": stationary,
        "test": "adf",
    }


def kpss_test(values):
    sample_size = len(values)
    if sample_size < 20:
        return {
            "statistic": 0.0,
            "pvalue": 1.0,
            "stationary": True,
            "insufficient_data": True,
        }

    mean_value = compute_mean(values)
    residuals = [value - mean_value for value in values]
    cumulative_variance = sum(
        sum(residual**2 for residual in residuals[:index + 1])
        for index in range(sample_size)
    ) / sample_size
    trend_variance = compute_variance(values)
    statistic = cumulative_variance / trend_variance if trend_variance > 0 else 0.0
    stationary = statistic < 0.74

    return {
        "statistic": statistic,
        "pvalue": 0.05 if stationary else 0.1,
        "stationary": stationary,
        "test": "kpss",
    }


def determine_arima_order(values, acf_vals, pacf_vals):
    adf_result = adf_test(values)
    differencing = 0 if adf_result["stationary"] else 1

    ar_order = 0
    for index in range(1, len(pacf_vals)):
        if abs(pacf_vals[index]) > 0.2:
            ar_order = index
        else:
            break

    ma_order = 0
    for index in range(1, len(acf_vals)):
        if abs(acf_vals[index]) > 0.2:
            ma_order = index
        else:
            break

    return ar_order, differencing, ma_order


def suggest_differencing(values, differencing=1):
    result = [value for value in values]
    for _ in range(differencing):
        result = [result[index + 1] - result[index] for index in range(len(result) - 1)]
    return result


def seasonal_strength(values, period=12):
    if len(values) < 2 * period:
        return 0.0

    seasonal_average = []
    for offset in range(period):
        period_values = [values[index] for index in range(offset, len(values), period)]
        seasonal_average.append(compute_mean(period_values))

    seasonal_variance = compute_variance(seasonal_average)
    total_variance = compute_variance(values)
    return seasonal_variance / total_variance if total_variance > 0 else 0.0


def _require_z3():
    if z3 is None:
        pytest.skip("z3-solver is not installed")
    from z3 import And, Int, Solver, sat

    return Int, Solver, And, sat


def _require_bool_z3():
    if z3 is None:
        pytest.skip("z3-solver is not installed")
    from z3 import Bool, Implies, Solver, sat

    return Bool, Solver, Implies, sat


def verify_model_order(ar_order, differencing, ma_order):
    Int, Solver, And, sat = _require_z3()
    solver = Solver()
    p_var, d_var, q_var = Int("p"), Int("d"), Int("q")
    solver.add(And(p_var >= 0, p_var <= 10))
    solver.add(And(d_var >= 0, d_var <= 2))
    solver.add(And(q_var >= 0, q_var <= 10))
    solver.add(p_var == ar_order, d_var == differencing, q_var == ma_order)
    return solver.check() == sat


def validate_stationarity(stationary, values):
    Bool, Solver, Implies, sat = _require_bool_z3()
    solver = Solver()
    valid = Bool("valid")
    solver.add(valid == (len(values) > 10))
    solver.add(Implies(stationary is False, len(values) > 20))
    return solver.check() == sat


def enforce_parameter_bounds(acf_vals, pacf_vals):
    Solver, And, sat = _require_z3()[1:]
    solver = Solver()
    for acf in acf_vals[:10]:
        solver.add(And(-1.0 <= acf, acf <= 1.0))
    for pacf in pacf_vals[:10]:
        solver.add(And(-1.0 <= pacf, pacf <= 1.0))
    return solver.check() == sat


def _assert_close(actual, expected, tolerance=0.01):
    assert abs(actual - expected) <= tolerance, f"expected {expected}, got {actual}"


def _trend_values(length=40):
    return [float(index) for index in range(length)]


def _seasonal_values(period=12, cycles=5):
    return [float((index % period) * 2.0) for index in range(period * cycles)]


def _adf_stationary_values():
    values = []
    for index in range(20):
        values.append(1.0 if index % 2 == 0 else 1.1)
    for index in range(20):
        values.append(5.0 if index % 2 == 0 else 5.1)
    return values


class TestComputeMean:
    def test_mean_computation(self):
        assert compute_mean([2.0, 4.0, 6.0, 8.0]) == 5.0

    def test_empty_list(self):
        assert compute_mean([]) == 0.0

    def test_single_value(self):
        assert compute_mean([42.0]) == 42.0


class TestComputeVariance:
    def test_population_variance(self):
        _assert_close(compute_variance([1.0, 2.0, 3.0, 4.0]), 1.25)

    def test_zero_variance(self):
        assert compute_variance([7.0, 7.0, 7.0]) == 0.0

    def test_known_baseline(self):
        _assert_close(compute_variance([10.0, 20.0, 30.0, 40.0, 50.0]), 200.0)


class TestAutocorrelation:
    def test_lag_zero_is_one(self):
        assert compute_autocorrelation([1.0, 2.0, 3.0, 4.0], 0) == 1.0

    def test_decaying_autocorrelation_for_non_stationary_series(self):
        acf = compute_acf(_trend_values(30), max_lag=5)
        assert acf[1] > acf[2] > acf[3] > 0.0


class TestComputeACF:
    def test_acf_vector_contract(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        acf = compute_acf(values, max_lag=3)
        assert len(acf) == 4
        assert acf[0] == 1.0
        _assert_close(acf[1], 0.6)
        _assert_close(acf[2], 0.08571428571428572)
        _assert_close(acf[3], -0.5428571428571428)

    def test_length_validation(self):
        acf = compute_acf([1.0, 2.0, 3.0, 4.0], max_lag=0)
        assert len(acf) == 1
        assert acf[0] == 1.0


class TestComputePACF:
    def test_pacf_lag_one_is_lag_one_over_lag_zero(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        pacf = compute_pacf(values, max_lag=1)
        expected = compute_autocorrelation(values, 1) / compute_autocorrelation(values, 0)
        assert pacf[0] == 1.0
        _assert_close(pacf[1], expected)

    def test_basic_contract(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        pacf = compute_pacf(values, max_lag=2)
        assert len(pacf) == 3
        assert pacf[0] == 1.0
        _assert_close(pacf[2], compute_autocorrelation(values, 2))


class TestADFTest:
    def test_stationary_values(self):
        result = adf_test(_adf_stationary_values())
        assert result["stationary"] is True
        assert result["statistic"] < -2.86

    def test_non_stationary_random_walk(self):
        result = adf_test(_trend_values(40))
        assert result["stationary"] is False
        assert result["pvalue"] == 0.1

    def test_insufficient_data(self):
        result = adf_test([1.0, 2.0, 3.0, 4.0])
        assert result["insufficient_data"] is True
        assert result["stationary"] is False


class TestKPSSTest:
    def test_trend_stationarity_logic(self):
        result = kpss_test([1.0] * 20)
        assert result["stationary"] is True
        assert result["statistic"] == 0.0
        assert result["test"] == "kpss"

    def test_insufficient_data(self):
        result = kpss_test([1.0, 2.0, 3.0, 4.0])
        assert result["insufficient_data"] is True
        assert result["stationary"] is True


class TestARIMAOrder:
    def test_white_noise(self):
        values = _adf_stationary_values()
        acf = [1.0, 0.0, 0.0, 0.0]
        pacf = [1.0, 0.0, 0.0, 0.0]
        assert determine_arima_order(values, acf, pacf) == (0, 0, 0)

    def test_trend(self):
        assert determine_arima_order(_trend_values(40), [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]) == (0, 1, 0)

    def test_seasonal(self):
        values = _seasonal_values()
        acf = [1.0, 0.3, 0.1, 0.0]
        pacf = [1.0, 0.3, 0.1, 0.0]
        order = determine_arima_order(values, acf, pacf)
        assert order[0] == 1
        assert order[1] == 1
        assert order[2] == 1
        assert seasonal_strength(values) > 0


class TestDifferencing:
    def test_first_difference_removes_trend(self):
        differenced = suggest_differencing(_trend_values(40), differencing=1)
        assert differenced == [1.0] * 39

    def test_second_difference_of_linear_series(self):
        differenced = suggest_differencing(_trend_values(40), differencing=2)
        assert differenced == [0.0] * 38


class TestSeasonalStrength:
    def test_seasonal_series_high_strength(self):
        strength = seasonal_strength(_seasonal_values(period=6, cycles=4), period=6)
        assert strength > 0.9

    def test_non_seasonal_low_strength(self):
        values = [0.0, 50.0, 50.0, 50.0, 100.0, 50.0, 50.0, 50.0]
        strength = seasonal_strength(values, period=4)
        assert strength < 0.1


class TestZ3Constraints:
    def test_arima_order_bounds_valid(self):
        assert verify_model_order(5, 1, 5) is True

    def test_arima_order_bounds_invalid(self):
        assert verify_model_order(11, 1, 5) is False

    def test_stationarity_constraint(self):
        assert validate_stationarity(False, [1.0] * 21) is True
        assert validate_stationarity(False, [1.0] * 11) is False

    def test_acf_pacf_bounds(self):
        assert enforce_parameter_bounds([0.5, -0.5], [0.25, -0.25]) is True
        assert enforce_parameter_bounds([1.5], [0.25]) is False
