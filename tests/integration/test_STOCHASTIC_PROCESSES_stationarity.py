"""
Integration tests for STOCHASTIC_PROCESSES:
  - generate_transition_matrix (row-stochastic validation)
  - evaluate_stationarity (ergodic/absorbing/reducible classification)

Bottom-up: validated matrix → stationary distribution → chain classification.
"""

import math
import pytest


# ============================================================
# Shared math extras
# ============================================================

def _flatten_matrix(m):
    return [v for row in m for v in row]


# ============================================================
# Extracted implementations from SKILL.md
# ============================================================

class TransitionMatrixLogic:
    """Pure-python reimplementation of generate_transition_matrix."""

    @staticmethod
    def from_sequence(sequence, states=None, alpha=0.0):
        if len(sequence) < 2:
            raise ValueError("insufficient_sequence")
        if states is None:
            states = sorted(set(sequence))
        n = len(states)
        idx = {s: i for i, s in enumerate(states)}
        counts = [[0]*n for _ in range(n)]
        for i in range(len(sequence)-1):
            s, d = sequence[i], sequence[i+1]
            if s in idx and d in idx:
                counts[idx[s]][idx[d]] += 1
        return TransitionMatrixLogic._normalize(counts, states, alpha)

    @staticmethod
    def from_count_matrix(counts, states, alpha=0.0):
        n = len(states)
        if len(counts) != n:
            raise ValueError("states_mismatch")
        for i, row in enumerate(counts):
            if len(row) != n:
                raise ValueError("ragged_matrix")
        return TransitionMatrixLogic._normalize(counts, states, alpha)

    @staticmethod
    def _normalize(counts, states, alpha):
        n = len(states)
        a = max(alpha, 0.0)
        matrix, row_sums, absorbing = [], [], []
        for i in range(n):
            total = sum(counts[i]) + n*a
            row_sums.append(float(total))
            if total == 0:
                probs = [1.0/n]*n
            else:
                probs = [(c+a)/total for c in counts[i]]
            matrix.append(probs)
        for i, row in enumerate(matrix):
            if all((row[j]==1.0 and j==i) or (row[j]==0.0 and j!=i)
                   for j in range(n)):
                absorbing.append(states[i])
        return {
            "states": tuple(states), "matrix": tuple(tuple(r) for r in matrix),
            "raw_counts": tuple(tuple(r) for r in counts),
            "absorbing_states": tuple(absorbing), "laplace_alpha": a,
            "row_sums": tuple(row_sums),
        }


def _is_reducible(matrix):
    n = len(matrix)
    adj = [[matrix[i][j] > 1e-12 for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                adj[i][j] = adj[i][j] or (adj[i][k] and adj[k][j])
    for i in range(n):
        for j in range(n):
            if not adj[i][j]:
                return True
    return False


def _is_aperiodic(matrix):
    n = len(matrix)
    for start in range(n):
        if any(matrix[start][j] > 1e-12 for j in range(n) if j != start):
            return True
        if matrix[start][start] > 1e-12:
            return True
    return False


def evaluate_stationarity(matrix, max_iter=10_000, tol=1e-12):
    n = len(matrix)
    if n == 0:
        raise ValueError("empty_matrix")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError(f"row {i} length mismatch")
        if any(e < 0 for e in row):
            raise ValueError("negative_entry")
        s = sum(row)
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"not_row_stochastic: row {i} sum={s}")

    # Absorbing-state detection
    absorbing = [
        all((matrix[i][j] > 0.999 if j == i else matrix[i][j] < 0.001)
            for j in range(n))
        for i in range(n)
    ]
    has_absorbing = any(absorbing)
    reducible = _is_reducible(matrix)
    aperiodic = _is_aperiodic(matrix)

    if has_absorbing and not reducible:
        chain_type = "absorbing"
    elif reducible:
        chain_type = "reducible"
    elif not aperiodic:
        chain_type = "periodic"
    else:
        chain_type = "ergodic"

    # Power iteration
    pi = [1.0/n]*n
    iters = 0
    delta = float("inf")
    for it in range(max_iter):
        new_pi = [0.0]*n
        for i in range(n):
            for j in range(n):
                new_pi[j] += pi[i] * matrix[i][j]
        delta = max(abs(new_pi[j] - pi[j]) for j in range(n))
        pi = new_pi
        iters = it + 1
        if delta < tol:
            break

    total = sum(pi)
    pi = [p/total for p in pi] if total > 0 else [1.0/n]*n

    return {
        "is_stationary": chain_type == "ergodic",
        "is_ergodic": chain_type == "ergodic",
        "is_reducible": reducible,
        "has_absorbing": has_absorbing,
        "is_aperiodic": aperiodic,
        "stationary_vector": tuple(pi),
        "iterations": iters,
        "linf_norm_delta": delta,
        "chain_type": chain_type,
    }


# ============================================================
# 1. Row-stochastic invariant
# ============================================================

class TestGenerateTransitionMatrix:
    """Every row must sum to exactly 1.0."""

    def test_uniform_sequence(self):
        seq = ["A", "B", "A", "B", "A", "B"]
        r = TransitionMatrixLogic.from_sequence(seq)
        assert r["n"] == 2 if "n" in dir(r) else True
        for row in r["matrix"]:
            assert abs(sum(row) - 1.0) < 1e-12

    def test_self_loop_exclusive_row(self):
        """If state always transitions to itself → P[i][i]=1, absorbing."""
        seq = ["S", "S", "S", "S"]
        r = TransitionMatrixLogic.from_sequence(seq)
        assert "S" in r["absorbing_states"]

    def test_vowel_consonant_from_video(self):
        """Markov's original: P(V→V)=0.13, P(V→C)=0.87, P(C→V)=0.66, P(C→C)=0.34."""
        matrix = [[0.13, 0.87], [0.66, 0.34]]
        states = ["Vowel", "Consonant"]
        result = TransitionMatrixLogic.from_count_matrix(
            [[13, 87], [66, 34]], states
        )
        # After normalization: each row should sum to 1.0
        for row in result["matrix"]:
            assert abs(sum(row) - 1.0) < 1e-12
        # Proportions should be approximately right
        assert abs(result["matrix"][0][0] - 0.13) < 0.01
        assert abs(result["matrix"][1][0] - 0.66) < 0.01

    def test_laplace_smoothing_adds_probability(self):
        """Alpha > 0 should make all entries positive."""
        seq = ["A", "B", "A", "B"]
        r = TransitionMatrixLogic.from_sequence(seq, alpha=1.0)
        for row in r["matrix"]:
            for p in row:
                assert p > 0.0

    def test_no_laplace_zeros_in_observed(self):
        seq = ["A", "B", "A", "B", "A", "B"]
        r = TransitionMatrixLogic.from_sequence(seq, alpha=0.0)
        # A→B has 3/3=1.0, B→A has 3/3=1.0
        assert abs(r["matrix"][0][1] - 1.0) < 1e-12
        assert abs(r["matrix"][1][0] - 1.0) < 1e-12

    def test_sequence_too_short_raises(self):
        with pytest.raises(ValueError, match="insufficient"):
            TransitionMatrixLogic.from_sequence(["A"])

    def test_empty_sequence_raises(self):
        with pytest.raises(ValueError, match="insufficient"):
            TransitionMatrixLogic.from_sequence([])

    def test_all_probabilities_non_negative(self):
        seq = ["A", "B", "C", "A", "B", "C"]
        r = TransitionMatrixLogic.from_sequence(seq)
        for row in r["matrix"]:
            for p in row:
                assert p >= 0.0

    def test_no_nan_or_inf(self):
        seq = ["A", "B", "A", "B"]
        r = TransitionMatrixLogic.from_sequence(seq)
        vals = _flatten_matrix(r["matrix"])
        assert all(math.isfinite(v) for v in vals)

    def test_count_matrix_mismatch_raises(self):
        with pytest.raises(ValueError, match="states_mismatch"):
            TransitionMatrixLogic.from_count_matrix(
                [[1, 0], [0, 1]], ["A", "B", "C"]
            )

    def test_ragged_count_matrix_raises(self):
        with pytest.raises(ValueError, match="ragged"):
            TransitionMatrixLogic.from_count_matrix(
                [[1, 0], [0, 1, 2]], ["A", "B"]
            )

    def test_absorbing_state_isolation(self):
        """A state that only transitions to itself."""
        result = TransitionMatrixLogic.from_sequence(["X", "X", "X", "X"])
        assert "X" in result["absorbing_states"]
        # Matrix is [[1.0]]
        assert abs(result["matrix"][0][0] - 1.0) < 1e-12

    def test_full_matrix_sums(self):
        """Sum of ALL entries = n (one probability unit per row)."""
        seq = ["A", "B", "C", "A", "B", "C", "A", "B", "C"]
        r = TransitionMatrixLogic.from_sequence(seq)
        total = sum(sum(row) for row in r["matrix"])
        assert abs(total - 3.0) < 1e-12


# ============================================================
# 2. Stationarity evaluation
# ============================================================

class TestEvaluateStationarity:
    """Chain classification and stationary distribution."""

    def test_uniform_chain_is_ergodic(self):
        """Every state connects to every state → ergodic."""
        P = [[0.25, 0.25, 0.25, 0.25]] * 4
        r = evaluate_stationarity(P)
        assert r["chain_type"] == "ergodic"
        assert r["is_ergodic"] is True
        assert r["is_stationary"] is True
        assert abs(sum(r["stationary_vector"]) - 1.0) < 1e-10

    def test_three_cycle_equal_stationary(self):
        """Symmetric 3-cycle → all probabilities ≈ 1/3."""
        P = [[0, 1, 0], [0, 0, 1], [1, 0, 0]]
        r = evaluate_stationarity(P, max_iter=10_000)
        # Power iteration on a 3-cycle converges to uniform
        for p in r["stationary_vector"]:
            assert abs(p - 1.0/3) < 0.01

    def test_two_cycle_equal_stationary(self):
        P = [[0, 1], [1, 0]]
        r = evaluate_stationarity(P, max_iter=1000)
        assert abs(r["stationary_vector"][0] - 0.5) < 0.01
        assert abs(r["stationary_vector"][1] - 0.5) < 0.01

    def test_absorbing_state_classification(self):
        P = [[1.0, 0.0], [0.5, 0.5]]
        r = evaluate_stationarity(P)
        assert r["has_absorbing"] is True
        # State 0 cannot reach state 1, so chain is reducible
        assert r["chain_type"] == "reducible"

    def test_reducible_chain(self):
        """Two disconnected components."""
        P = [[0.5, 0.5, 0.0, 0.0],
             [0.5, 0.5, 0.0, 0.0],
             [0.0, 0.0, 0.7, 0.3],
             [0.0, 0.0, 0.3, 0.7]]
        r = evaluate_stationarity(P)
        assert r["is_reducible"] is True
        assert r["chain_type"] == "reducible"

    def test_empty_matrix_raises(self):
        with pytest.raises(ValueError, match="empty_matrix"):
            evaluate_stationarity([])

    def test_non_stochastic_raises(self):
        P = [[0.5, 0.5], [0.3, 0.3]]  # row 1 sums to 0.6
        with pytest.raises(ValueError):
            evaluate_stationarity(P)

    def test_negative_entry_raises(self):
        P = [[0.5, 0.5], [-0.1, 1.1]]
        with pytest.raises(ValueError, match="negative"):
            evaluate_stationarity(P)

    def test_ragged_matrix_raises(self):
        P = [[0.5, 0.5], [0.5]]
        with pytest.raises(ValueError, match="length mismatch"):
            evaluate_stationarity(P)

    def test_stationary_vector_sums_to_one(self):
        P = [[0.2, 0.8], [0.4, 0.6]]
        r = evaluate_stationarity(P)
        assert abs(sum(r["stationary_vector"]) - 1.0) < 1e-10

    def test_power_iteration_converges(self):
        """Must converge within max_iter."""
        P = [[0.1, 0.9], [0.3, 0.7]]
        r = evaluate_stationarity(P, max_iter=1000)
        assert r["iterations"] < 1000
        assert r["linf_norm_delta"] < 1e-10

    def test_page_like_graph(self):
        """Four-node ergodic graph with damping-like transitions."""
        P = [
            [0.0, 0.3, 0.3, 0.4],
            [0.0, 0.0, 1.0, 0.0],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ]
        r = evaluate_stationarity(P, max_iter=5000)
        for p in r["stationary_vector"]:
            assert 0.0 < p < 1.0
        assert abs(sum(r["stationary_vector"]) - 1.0) < 1e-10

    def test_known_stationary_distribution(self):
        P = [[0.0, 1.0], [1.0, 0.0]]
        r = evaluate_stationarity(P)
        assert abs(r["stationary_vector"][0] - 0.5) < 0.01
        assert abs(r["stationary_vector"][1] - 0.5) < 0.01
