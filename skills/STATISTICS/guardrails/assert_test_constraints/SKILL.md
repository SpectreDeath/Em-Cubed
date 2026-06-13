---
name: assert_test_constraints
domain: STATISTICS
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Guardrail skill enforcing measurement-level, sample-size, and
  distribution-shape constraints before any inferential test is
  dispatched.  Prolog layer routes parametric vs non-parametric
  families via first-order logic; Python layer quantifies n,
  normality (Shapiro-Wilk), and variance homogeneity (Levene).
compatibility: PYTHON, PROLOG
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

# Assert Test Constraints

## Purpose
Gate any statistical test execution through hierarchical symbolic (Prolog) and numeric (Python) constraint checks: measurement level, sample size, normality, and variance homogeneity.

## Description
Implements a two-layer guardrail:
- **Prolog layer** — Pure first-order logic routing. Enforces Stevens’ measurement hierarchy, sample-size minima, parametric-vs-non-parametric family permission, and formal hypothesis-state transitions (reject_null, fail_to_reject_null).
- **Python layer** — Numerical diagnostics: sample-size count, Shapiro-Wilk normality flag, Levene variance-homogeneity flag. Returns a constraint_bundle consumed by Prolog.

## Prolog Surface (prelude.pl)

```prolog
:- module(test_router, [
    % Public predicates
    permitted_test/3,
    formal_conclusion/3,
    select_test/3,
    valid_measurement_for/2,
    dominates/2,
    ci_z/2
]).

% ============================================================
% 1. Stevens' measurement hierarchy
% ============================================================
dominates(ratio, interval).
dominates(interval, ordinal).
dominates(ordinal, nominal).

% ============================================================
% 2. Test families
% ============================================================
parametric_test(t_test_independent).
parametric_test(t_test_paired).
parametric_test(pearson_r).
parametric_test(one_way_anova).
parametric_test(linear_regression).

non_parametric_test(mann_whitney_u).
non_parametric_test(wilcoxon_signed_rank).
non_parametric_test(spearman_rho).
non_parametric_test(kruskal_wallis).
non_parametric_test(friedman).

% chi_square accepts nominal (categorical)
chi_square_test(chi_square).

% ============================================================
% 3. Measurement-level gate
% ============================================================
valid_measurement_for(Test, Level) :-
    ( parametric_test(Test)
    -> (Level = interval ; Level = ratio)
    ;  non_parametric_test(Test)
    -> (Level = ordinal ; Level = interval ; Level = ratio)
    ;  Test = chi_square
    -> Level = nominal
    ).

% ============================================================
% 4. Minimum sample-size table
% ============================================================
min_n(t_test_independent,   2).
min_n(t_test_paired,        2).
min_n(pearson_r,            3).
min_n(spearman_rho,         3).
min_n(one_way_anova,       3).
min_n(linear_regression,   3).
min_n(chi_square,           5).
min_n(kruskal_wallis,      3).
min_n(mann_whitney_u,      2).
min_n(wilcoxon_signed_rank, 2).
min_n(friedman,            3).

sample_size_ok(N, Test) :-
    min_n(Test, Min),
    N >= Min.

% ============================================================
% 5. Normality requirement table
% ============================================================
requires_normality(t_test_independent).
requires_normality(t_test_paired).
requires_normality(pearson_r).
requires_normality(one_way_anova).
requires_normality(linear_regression).
requires_normality(kruskal_wallis).
requires_normality(mann_whitney_u).
requires_normality(wilcoxon_signed_rank).
% chi_square and spearman_rho do NOT require normality
% (no clause for them -> defaults to false via negation below)

% ============================================================
% 6. Python numeric bridge
% ============================================================
% call_python/3 is orchestrated by the runtime.
:- meta_predicate call_python(+, +, -).

% ============================================================
% 7. Main permission gate
% ============================================================
permitted_test(Dataset, Columns, Test, allowed) :-
    % (a) measurement level
    forall(
        member(C, Columns),
        validate_level(Dataset, C, hint(_), Level)
    ),
    valid_measurement_for(Test, Level),
    % (b) sample size
    call_python(sample_size, [Dataset, Columns], N),
    sample_size_ok(N, Test),
    % (c) normality (parametric only)
    ( requires_normality(Test)
    -> call_python(normal_flag, [Dataset, Columns], true)
    ; true
    ),
    !.

permitted_test(Dataset, _Columns, _Test, blocked(insufficient_sample_size)) :-
    call_python(sample_size, [Dataset, _], N),
    N < 2.

permitted_test(Dataset, Columns, Test, blocked(normality_violation)) :-
    requires_normality(Test),
    call_python(normal_flag, [Dataset, Columns], false).

permitted_test(Dataset, _Columns, Test, blocked(measurement_level_too_low)) :-
    valid_measurement_for(Test, _), fail.

permitted_test(_, _, _, blocked(unknown)).

% ============================================================
% 8. Formal hypothesis-state transitions (first-order logic)
% ============================================================
formal_conclusion(reject_null,       state(rejected),       'Reject H0 at α').
formal_conclusion(fail_to_reject_null, state(not_rejected), 'Fail to reject H0 at α').

% ============================================================
% 9. Deterministic test-selection decision tree
%     (used after Prolog receives the saved constraint bundle)
% ============================================================
% select_test(+Groups, +IsIndependent, +IsNormal, -Test)
select_test(2, true,  true,  independent_t) :- !.
select_test(2, true,  false, mann_whitney_u) :- !.
select_test(2, false, true,  paired_t)      :- !.
select_test(2, false, false, wilcoxon_signed_rank) :- !.

select_test(G, true,  true,  one_way_anova) :-
    G > 2, !.
select_test(G, true,  false, kruskal_wallis) :-
    G > 2, !.
select_test(_, false, true,  dependent_t).
select_test(_, false, false, friedman).

% ============================================================
% 10. Confidence-level -> z-score lookup table
% ============================================================
ci_z(0.90, 1.645).
ci_z(0.95, 1.960).
ci_z(0.99, 2.576).

% Fallback: arbitrary confidence level (interpolated by Python)
ci_z(Level, Z) :-
    Level > 0, Level < 1,
    \+ ci_z(Level, _),          % not in table
    call_python(interpolate_z, [Level], Z).
```

## Python Surface (executor.py)

```python
"""
assert_test_constraints
========================
Hybrid guardrail: Python computes numeric flags consumed by Prolog.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class ConstraintBundle:
    dataset_ref: str
    columns: Tuple[str, ...]
    n: int
    independent: bool
    normal: bool
    equal_variance: bool
    measurement_levels: Tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "dataset_ref":       self.dataset_ref,
            "columns":           list(self.columns),
            "n":                 self.n,
            "independent":       self.independent,
            "normal":            self.normal,
            "equal_variance":    self.equal_variance,
            "measurement_levels": list(self.measurement_levels),
        }


def _clean(values: List[float]) -> List[float]:
    return [
        v for v in values
        if v is not None and not (isinstance(v, float) and math.isnan(v))
    ]


def sample_size(dataset_ref: str, columns: List[str], data: dict) -> int:
    """Count non-missing observations across all target columns.

    Parameters
    ----------
    dataset_ref : str
    columns : list of column names participating in the test
    data : dict  {column_name: [values]}
    """
    if not columns:
        return 0
    col_vectors = [data.get(c, []) for c in columns]
    n = 0
    for row in zip(*col_vectors):
        if all(
            v is not None and not (isinstance(v, float) and math.isnan(v))
            for v in row
        ):
            n += 1
    return n


def normal_flag(
    dataset_ref: str,
    columns: List[str],
    data: dict,
    method: str = "shapiro-wilk",
) -> bool:
    """Return True if all groups pass normality test (Shapiro-Wilk or fallback)."""
    col_vectors = [data.get(c, []) for c in columns]
    for vec in col_vectors:
        clean = _clean(vec)
        n = len(clean)
        if n < 3:
            return False
        if method == "shapiro-wilk":
            try:
                from scipy.stats import shapiro
                _, p = shapiro(clean)
                if p < 0.05:
                    return False
            except ImportError:
                if not _approx_normal_numpy(clean):
                    return False
        else:
            if not _approx_normal_numpy(clean):
                return False
    return True


def _approx_normal_numpy(values: List[float]) -> bool:
    """Approximate normality via skewness and kurtosis (D'Agostino-style)."""
    import numpy as np
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n < 8:
        return False
    mean = arr.mean()
    std  = arr.std(ddof=1)
    if std == 0:
        return False
    z = (arr - mean) / std
    skew = float(np.mean(z ** 3))
    kurt = float(np.mean(z ** 4)) - 3.0
    return abs(skew) < 1.0 and abs(kurt) < 2.0


def equal_variance_flag(
    dataset_ref: str,
    columns: List[str],
    data: dict,
) -> bool:
    """Return True if Levene test does not reject equal variances."""
    col_vectors = [_clean(data.get(c, [])) for c in columns]
    col_vectors = [v for v in col_vectors if len(v) >= 2]
    if len(col_vectors) < 2:
        return True
    try:
        from scipy.stats import levene
        stat, p = levene(*col_vectors)
        return p >= 0.05
    except ImportError:
        vars_ = [
            sum((x - sum(x)/len(x))**2 for x in v) / (len(v)-1)
            for v in col_vectors
        ]
        ratio = max(vars_) / min(vars_) if min(vars_) > 0 else 1.0
        return ratio < 4.0


def interpolate_z(confidence_level: float) -> float:
    """Numerical fallback for unregistered confidence levels.

    Uses inverse-error-function approximation of the standard-normal
    quantile.  Kept in Python so Prolog can call it via
    call_python(interpolate_z, [Level], Z).
    """
    if not (0.0 < confidence_level < 1.0):
        raise ValueError("confidence_level must be in (0,1)")
    tail_area = (1.0 - confidence_level) / 2.0
    target = 1.0 - tail_area  # = (1 + L) / 2
    p = 2.0 * target - 1.0
    z = math.sqrt(2.0) * _erfinv(p)
    return z


_ERFINV_COEFFS = [
    -3.969683028665376e+01,  2.209460984245205e+02,
    -2.759285104469687e+02,  1.383577518672690e+02,
    -3.066479806614716e+01,  2.506628277459239e+00,
]
_ERFINV_POLY_COEFFS = [
    -5.447609879822406e+01, -1.615858368580409e+02,
     1.556049798740891e+02, -6.680131188771972e+01,
     1.328068155288572e+01,
]

def _erfinv(p: float) -> float:
    if p <= 0.0: return float("-inf")
    if p >= 1.0: return float("inf")
    split = 0.140
    if p < split:
        q = math.sqrt(-2.0 * math.log(p / 2.0))
        num = (((((_ERFINV_COEFFS[0]*q + _ERFINV_COEFFS[1])*q
                + _ERFINV_COEFFS[2])*q + _ERFINV_COEFFS[3])*q
                + _ERFINV_COEFFS[4])*q + _ERFINV_COEFFS[5])
        den = (((((_ERFINV_POLY_COEFFS[0]*q + _ERFINV_POLY_COEFFS[1])*q
                + _ERFINV_POLY_COEFFS[2])*q + _ERFINV_POLY_COEFFS[3])*q
                + _ERFINV_POLY_COEFFS[4])*q + 1.0)
        return -(num / den)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        num = (((((_ERFINV_COEFFS[0]*q + _ERFINV_COEFFS[1])*q
                + _ERFINV_COEFFS[2])*q + _ERFINV_COEFFS[3])*q
                + _ERFINV_COEFFS[4])*q + _ERFINV_COEFFS[5])
        den = (((((_ERFINV_POLY_COEFFS[0]*q + _ERFINV_POLY_COEFFS[1])*q
                + _ERFINV_POLY_COEFFS[2])*q + _ERFINV_POLY_COEFFS[3])*q
                + _ERFINV_POLY_COEFFS[4])*q + 1.0)
        return num / den


# ---- Orchestration -------------------------------------------------------

def assert_test_constraints(
    dataset_ref: str,
    columns: List[str],
    test: str,
    data: dict,
    independent: bool = True,
) -> ConstraintBundle:
    """Evaluate all constraints; return immutable ConstraintBundle.

    Parameters
    ----------
    dataset_ref : str
        Logical identifier for the dataset.
    columns : list of str
        Columns involved in the intended test.
    test : str
        Atom naming the intended test (must match Prolog `min_n/2` keys).
    data : dict
        {column_name: list of numbers or None}
    independent : bool
        Flag set by user (True if groups are independent, False if paired/repeated).

    Returns
    -------
    ConstraintBundle
    """
    n          = sample_size(dataset_ref, columns, data)
    normal     = normal_flag(dataset_ref, columns, data)
    eq_var     = equal_variance_flag(dataset_ref, columns, data)
    meas_levels = tuple(columns)  # symbolic validation handled by Prolog

    return ConstraintBundle(
        dataset_ref        = dataset_ref,
        columns            = tuple(columns),
        n                  = n,
        independent        = independent,
        normal             = normal,
        equal_variance     = eq_var,
        measurement_levels = meas_levels,
    )
```

## Testing

```python
def test_sample_size_count():
    data = {"group_a": [1, 2, 3], "group_b": [1, None, 3]}
    assert sample_size("ds", ["group_a", "group_b"], data) == 2

def test_normal_flag_clean_normal():
    import numpy as np
    rng = np.random.default_rng(42)
    clean = rng.normal(0, 1, 50).tolist()
    data = {"x": clean}
    assert normal_flag("ds", ["x"], data) is True

def test_normal_flag_skewed():
    data = {"x": [1, 1, 1, 1, 1000]}
    assert normal_flag("ds", ["x"], data) is False

def test_equal_variance_equal():
    data = {"a": [1,2,3,4,5], "b": [2,3,4,5,6]}
    assert equal_variance_flag("ds", ["a","b"], data) is True

def test_equal_variance_heterogeneous():
    data = {"a": [1,2,3], "b": [10,20,30,40,50]}
    assert equal_variance_flag("ds", ["a","b"], data) is False

def test_bundle_creation():
    data = {"x": [1.0, 2.0, 3.0, None, 5.0]}
    b = assert_test_constraints("ds", ["x"], "pearson_r", data)
    assert b.n == 4

def test_interpolate_z():
    z = interpolate_z(0.95)
    assert abs(z - 1.96) < 0.01

def test_interpolate_z_bounds():
    for bad in [0.0, 1.0, -0.1, 1.5]:
        try:
            interpolate_z(bad)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
```

## Security Considerations
- Pure in-memory computation; no I/O beyond user's data dict.
- No external API calls; scipy usage is optional and gracefully degraded.
- No secrets or credentials handled.
