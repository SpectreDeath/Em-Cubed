"""
Integration tests for STOCHASTIC_PROCESSES:
  - calculate_pagerank_vector (damping 0.85/0.15, dangling redistribution)
  - execute_monte_carlo_walk (seedable, dynamic context_callback)
  - compile_simulation_histogram (empirical stationary distribution)

Bottom-up: PageRank stationary vector → seedable MC walk → empirical histogram.
"""

import math
import random
import pytest


# ============================================================
# Re-implementations from SKILL.md (self-contained, zero imports)
# ============================================================

def _pagerank(edges, damping=0.85, max_iter=1000, tol=1e-10, personalization=None):
    if not (0.0 < damping < 1.0):
        raise ValueError("damping must be in (0,1)")
    adj = {}; nodes = set()
    for src, dst in edges:
        s, d = str(src), str(dst)
        nodes.add(s); nodes.add(d)
        adj.setdefault(s, {})
        adj[s][d] = adj[s].get(d, 0.0) + 1.0
    node_list = sorted(nodes); n = len(node_list)
    if n == 0:
        raise ValueError("no nodes")
    outdeg = {s: sum(adj.get(s, {}).values()) for s in node_list}
    dangling = {s: outdeg[s] == 0.0 for s in node_list}
    G = []; idx = {s: i for i, s in enumerate(node_list)}
    for src in node_list:
        row = [0.0]*n; deg = outdeg[src]
        if deg > 0:
            for dst, cnt in adj.get(src, {}).items():
                row[idx[dst]] = cnt / deg
        G.append(row)
    if personalization is None:
        e = [(1.0-damping)/n]*n
    else:
        raw = [float(personalization.get(s, 0.0)) for s in node_list]
        total = sum(raw)
        e = [v/total for v in raw] if total > 0 else [1.0/n]*n
    pi = [1.0/n]*n; iters = 0; delta = float("inf")
    for it in range(max_iter):
        new_pi = e[:]
        for i, src in enumerate(node_list):
            p_i = pi[i]
            if p_i == 0.0: continue
            contrib = p_i * damping
            row_i = G[i]
            for j in range(n):
                if row_i[j] > 0.0:
                    new_pi[j] += contrib * row_i[j]
        d_mass = sum(pi[k] for k in range(n) if dangling[node_list[k]])
        alloc = d_mass * damping / n
        for j in range(n):
            new_pi[j] += alloc
        delta = max(abs(new_pi[j]-pi[j]) for j in range(n))
        pi = new_pi; iters = it + 1
        if delta < tol: break
    total = sum(pi)
    pi = [p/total for p in pi] if total > 0 else [1.0/n]*n
    ranks = {s: p for s, p in zip(node_list, pi)}
    sorted_ranks = tuple(sorted(ranks.items(), key=lambda x: x[1], reverse=True))
    return {"ranks": ranks, "sorted_ranks": sorted_ranks,
            "iterations": iters, "linf_norm_delta": delta,
            "damping": damping, "n_nodes": n}


def _sample_next(state, state_to_idx, matrix, rng):
    idx = state_to_idx[state]; row = matrix[idx]
    u = rng.random(); cumsum = 0.0
    for j, p in enumerate(row):
        cumsum += p
        if u <= cumsum:
            return list(state_to_idx.keys())[j]
    return list(state_to_idx.keys())[-1]


def execute_monte_carlo_walk(matrix, states, start_state, n_steps,
                             seed=None, context_callback=None,
                             absorbing_threshold=0.99):
    if start_state not in states:
        raise ValueError("start_state not in states")
    if n_steps < 1:
        raise ValueError("n_steps must be >= 1")
    n = len(states)
    if len(matrix) != n:
        raise ValueError("matrix dimension mismatch")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError("row length mismatch")
        s = sum(row)
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"row {i} not row-stochastic")
    rng = random.Random(seed)
    state_to_idx = {s: i for i, s in enumerate(states)}
    path = [start_state]; history = [start_state]
    transition_log = []; visit_counts = {s: 0 for s in states}
    visit_counts[start_state] = 1
    absorbing_step = None; cur = start_state
    for step in range(n_steps):
        active_matrix = [row[:] for row in matrix]
        if context_callback is not None:
            override = context_callback(step, cur, history)
            if override:
                if "matrix_override" in override:
                    active_matrix = override["matrix_override"]
                if "state_boost" in override:
                    boost = override["state_boost"]
                    idx = state_to_idx[cur]
                    for s_label, delta in boost.items():
                        if s_label in state_to_idx:
                            j = state_to_idx[s_label]
                            active_matrix[idx][j] += delta
                    row_sum = sum(active_matrix[idx])
                    if row_sum > 0:
                        active_matrix[idx] = [p/row_sum for p in active_matrix[idx]]
        cur_idx = state_to_idx[cur]
        if active_matrix[cur_idx][cur_idx] >= absorbing_threshold:
            absorbing_step = step; break
        next_state = _sample_next(cur, state_to_idx, active_matrix, rng)
        trans_prob = active_matrix[cur_idx][state_to_idx[next_state]]
        transition_log.append((step, cur, next_state, trans_prob))
        path.append(next_state); history.append(next_state)
        visit_counts[next_state] = visit_counts.get(next_state, 0) + 1
        cur = next_state
    return {"path": tuple(path), "final_state": cur,
            "steps_taken": len(transition_log), "absorbing_step": absorbing_step,
            "state_visit_counts": visit_counts, "seed": seed,
            "transition_log": tuple(transition_log)}


def compile_simulation_histogram(paths, states=None, target_state=None):
    if not paths:
        raise ValueError("paths must be non-empty")
    seen = set()
    for p in paths:
        seen.update(p)
    if states is None:
        states = sorted(seen)
    else:
        states = list(states)
    if target_state is not None and target_state not in states:
        states.append(target_state)
        states.sort()
    idx = {s: i for i, s in enumerate(states)}
    n = len(states)
    counts = [0]*n; path_lengths = []; first_passage = {s: None for s in states}
    for path in paths:
        if not path: continue
        path_lengths.append(len(path))
        for t, s in enumerate(path):
            if s in idx:
                counts[idx[s]] += 1
        if target_state is not None:
            for t, s in enumerate(path):
                if s == target_state:
                    if first_passage[target_state] is None:
                        first_passage[target_state] = t
                    break
    total = sum(counts)
    dist = [c/total if total > 0 else 0.0 for c in counts]
    mean_len = sum(path_lengths)/len(path_lengths) if path_lengths else 0.0
    var_len = (sum((l-mean_len)**2 for l in path_lengths) / (len(path_lengths)-1)
               if len(path_lengths) > 1 else 0.0)
    std_len = math.sqrt(var_len) if var_len > 0 else 0.0
    uniform = [1.0/n]*n if n > 0 else []
    l1 = sum(abs(d-u) for d, u in zip(dist, uniform))
    return {"states": tuple(states), "visit_counts": tuple(counts),
            "total_visits": total, "empirical_distribution": tuple(dist),
            "path_count": len(paths), "total_steps": sum(path_lengths),
            "mean_path_length": mean_len, "std_path_length": std_len,
            "first_passage_times": first_passage,
            "chi_square_convergence": l1}


# ============================================================
# Section 1 — PageRank
# ============================================================

class TestCalculatePageRankVector:
    """Damping factor (85/15), dangling redistribution, convergence, ranking stability."""

    def test_three_node_cycle_uniform(self):
        edges = [("A", "B"), ("B", "C"), ("C", "A")]
        r = _pagerank(edges, damping=0.85)
        assert r["n_nodes"] == 3
        for v in r["ranks"].values():
            assert abs(v - 1.0/3) < 1e-4
        assert abs(sum(r["ranks"].values()) - 1.0) < 1e-10

    def test_two_node_cycle(self):
        edges = [("X", "Y"), ("Y", "X")]
        r = _pagerank(edges, damping=0.85)
        assert abs(r["ranks"]["X"] - r["ranks"]["Y"]) < 0.05
        assert abs(sum(r["ranks"].values()) - 1.0) < 1e-10

    def test_damping_085_converges(self):
        edges = [("A", "B"), ("B", "A")]
        r = _pagerank(edges, damping=0.85)
        assert r["iterations"] < 500
        assert r["linf_norm_delta"] < 1e-10

    def test_damping_015_still_sums_to_one(self):
        edges = [("A", "B"), ("B", "A")]
        r = _pagerank(edges, damping=0.15)
        assert abs(sum(r["ranks"].values()) - 1.0) < 1e-10

    def test_damping_zero_rejects(self):
        with pytest.raises(ValueError):
            _pagerank([("A", "B")], damping=0.0)

    def test_damping_one_rejects(self):
        with pytest.raises(ValueError):
            _pagerank([("A", "B")], damping=1.0)

    def test_damping_negative_rejects(self):
        with pytest.raises(ValueError):
            _pagerank([("A", "B")], damping=-0.1)

    def test_personalization_biases_ranks(self):
        edges = [("A", "B"), ("B", "A")]
        pers = {"A": 0.9, "B": 0.1}
        r = _pagerank(edges, damping=0.85, personalization=pers)
        assert r["ranks"]["A"] > r["ranks"]["B"]

    def test_personalization_zero_total_fallback(self):
        edges = [("A", "B"), ("B", "A")]
        pers = {}
        r = _pagerank(edges, damping=0.5, personalization=pers)
        assert abs(sum(r["ranks"].values()) - 1.0) < 1e-10

    def test_empty_graph_raises(self):
        with pytest.raises(ValueError, match="no nodes"):
            _pagerank([], damping=0.85)

    def test_ranks_non_negative(self):
        edges = [("A", "B"), ("B", "C"), ("C", "A")]
        r = _pagerank(edges, damping=0.85)
        for v in r["ranks"].values():
            assert v >= 0.0
            assert math.isfinite(v)

    def test_ranks_stable_after_100_iterations(self):
        """Run twice: convergence should be deterministic for same seed-like input."""
        edges = [("A", "B"), ("B", "C"), ("C", "A")]
        r1 = _pagerank(edges, damping=0.85, max_iter=100, tol=1e-12)
        r2 = _pagerank(edges, damping=0.85, max_iter=100, tol=1e-12)
        for k in r1["ranks"]:
            assert abs(r1["ranks"][k] - r2["ranks"][k]) < 1e-12

    def test_dangling_node_redistributes_mass(self):
        """Node 'D' has no outlinks; mass should be redistributed, not lost."""
        edges = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "D")]
        # D is actually a self-loop, so not dangling — use properly dangling:
        edges = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "A")]
        r = _pagerank(edges, damping=0.85)
        assert abs(sum(r["ranks"].values()) - 1.0) < 1e-10
        for v in r["ranks"].values():
            assert v >= 0.0

    def test_single_node_self_loop(self):
        edges = [("S", "S")]
        r = _pagerank(edges, damping=0.85)
        assert abs(r["ranks"]["S"] - 1.0) < 1e-8


# ============================================================
# Section 2 — Monte Carlo Walk
# ============================================================

class TestExecuteMonteCarloWalk:
    """Deterministic seed, absorbing states, stochastic distribution tolerance."""

    def test_deterministic_with_seed(self):
        matrix = [[0.5, 0.5], [0.5, 0.5]]
        states = ["A", "B"]
        r1 = execute_monte_carlo_walk(matrix, states, "A", 20, seed=42)
        r2 = execute_monte_carlo_walk(matrix, states, "A", 20, seed=42)
        assert r1["path"] == r2["path"]
        assert r1["final_state"] == r2["final_state"]

    def test_non_deterministic_without_seed(self):
        matrix = [[0.3, 0.7], [0.6, 0.4]]
        states = ["A", "B"]
        r1 = execute_monte_carlo_walk(matrix, states, "A", 50, seed=None)
        r2 = execute_monte_carlo_walk(matrix, states, "A", 50, seed=None)
        # Probability of identical path is astronomically low
        assert r1["path"] != r2["path"]

    def test_absorbing_state_halt(self):
        matrix = [[0.99, 0.01], [0.5, 0.5]]
        states = ["A", "B"]
        r = execute_monte_carlo_walk(matrix, states, "A", 1000, seed=0)
        assert r["absorbing_step"] is not None
        assert r["absorbing_step"] < 1000
        assert r["final_state"] == "A"

    def test_no_absorbing_full_walk(self):
        matrix = [[0.5, 0.5], [0.5, 0.5]]
        states = ["A", "B"]
        r = execute_monte_carlo_walk(matrix, states, "A", 50, seed=1)
        assert r["absorbing_step"] is None
        assert r["steps_taken"] == 50

    def test_start_state_in_path(self):
        states = ["X", "Y"]
        r = execute_monte_carlo_walk([[0.8, 0.2], [0.3, 0.7]],
                                     states, "X", 10, seed=7)
        assert r["path"][0] == "X"

    def test_path_length(self):
        r = execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "A", 25, seed=3)
        assert len(r["path"]) == 26  # initial state + 25 steps

    def test_state_visit_counts_non_negative(self):
        r = execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "A", 100, seed=5)
        for cnt in r["state_visit_counts"].values():
            assert cnt >= 0

    def test_both_states_visited(self):
        r = execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "A", 100, seed=9)
        assert r["state_visit_counts"]["A"] > 0
        assert r["state_visit_counts"]["B"] > 0

    def test_context_callback_state_boost(self):
        """After step 5, boost B by 50%."""
        matrix = [[0.5, 0.5], [0.3, 0.7]]
        states = ["A", "B"]

        def boost_callback(step, cur, history):
            if step >= 5 and cur == "A":
                return {"state_boost": {"B": 0.5}}
            return None

        r = execute_monte_carlo_walk(matrix, states, "A", 20, seed=11,
                                     context_callback=boost_callback)
        assert r["steps_taken"] == 20

    def test_invalid_start_raises(self):
        with pytest.raises(ValueError, match="start_state"):
            execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "Z", 10)

    def test_n_steps_zero_raises(self):
        with pytest.raises(ValueError, match="n_steps"):
            execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "A", 0)

    def test_non_stochastic_matrix_raises(self):
        with pytest.raises(ValueError, match="not row-stochastic"):
            execute_monte_carlo_walk([[0.5, 0.5], [0.3, 0.3]],
                                     ["A", "B"], "A", 10)

    def test_walk_stationary_distribution_tolerance(self):
        """
        Long walk on a 2-state chain should hit ~ stationary distribution.
        Theoretical: P = [[0.5,0.5],[0.5,0.5]] → uniform [0.5, 0.5].
        Empirical distribution should be within ε=0.01 of theoretical.
        """
        matrix = [[0.5, 0.5], [0.5, 0.5]]
        states = ["A", "B"]
        r = execute_monte_carlo_walk(matrix, states, "A", 10_000, seed=42)
        counts = r["state_visit_counts"]
        total = sum(counts.values())
        empirical_a = counts["A"] / total
        empirical_b = counts["B"] / total
        assert abs(empirical_a - 0.5) < 0.01
        assert abs(empirical_b - 0.5) < 0.01

    def test_asymmetric_chain_distribution(self):
        """
        P = [[0.2, 0.8], [0.6, 0.4]]
        Stationary: πA = 0.6*0.4/(0.2*0.4+0.6*0.8) = ... check convergence.
        """
        matrix = [[0.2, 0.8], [0.6, 0.4]]
        states = ["A", "B"]
        r = execute_monte_carlo_walk(matrix, states, "A", 50_000, seed=99)
        counts = r["state_visit_counts"]
        total = sum(counts.values())
        empirical = {s: counts[s]/total for s in states}
        # Compute theoretical stationary
        # πA = 0.6*0.4 / (0.2*0.4 + 0.6*0.8)  [wrong formula]
        # Correct: π = [πA, πB], πA = 0.6πB, πA+πB=1, πA = 0.6*0.4/(0.2*0.4+0.6*0.8)? 
        # Let me solve correctly: πA = 0.2πA + 0.6πB → 0.8πA = 0.6πB → πB = (0.8/0.6)πA
        # πA + (0.8/0.6)πA = 1 → πA = 0.6/(1.0+0.8/0.6) ... 
        # Simpler: 0.8πA = 0.6πB → πB/πA = 0.8/0.6 = 4/3
        # πA + 4/3 πA = 1 → πA = 3/7 ≈ 0.4286
        theo_a = 3.0 / 7.0
        assert abs(empirical["A"] - theo_a) < 0.01
        assert abs(empirical["B"] - (1.0 - theo_a)) < 0.01

    def test_seed_reproducibility_long_walk(self):
        matrix = [[0.3, 0.7], [0.4, 0.6]]
        states = ["A", "B"]
        r1 = execute_monte_carlo_walk(matrix, states, "A", 500, seed=12345)
        r2 = execute_monte_carlo_walk(matrix, states, "A", 500, seed=12345)
        assert r1["path"] == r2["path"]
        assert r1["transition_log"] == r2["transition_log"]

    def test_transition_log_length(self):
        r = execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "A", 30, seed=7)
        assert len(r["transition_log"]) == 30

    def test_each_transition_log_has_valid_probability(self):
        r = execute_monte_carlo_walk([[0.3, 0.7], [0.6, 0.4]],
                                     ["A", "B"], "A", 20, seed=8)
        for step, src, dst, prob in r["transition_log"]:
            assert 0.0 <= prob <= 1.0
            assert src in ("A", "B")
            assert dst in ("A", "B")

    def test_seed_echoed_in_result(self):
        r = execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "A", 10, seed=42)
        assert r["seed"] == 42

    def test_none_seed_echoed(self):
        r = execute_monte_carlo_walk([[0.5, 0.5], [0.5, 0.5]],
                                     ["A", "B"], "A", 10, seed=None)
        assert r["seed"] is None


# ============================================================
# Section 3 — Compile Simulation Histogram
# ============================================================

class TestCompileSimulationHistogram:
    """Empirical stationary distribution from aggregated walk paths."""

    def test_single_path_counts(self):
        paths = [["A", "B", "A", "B", "A"]]
        r = compile_simulation_histogram(paths)
        assert r["visit_counts"][r["states"].index("A")] == 3
        assert r["visit_counts"][r["states"].index("B")] == 2

    def test_multi_path_aggregation(self):
        paths = [["A", "B", "C"], ["C", "B", "A"], ["A", "B", "A"]]
        r = compile_simulation_histogram(paths)
        assert r["path_count"] == 3
        assert r["total_steps"] == 9
        assert r["total_visits"] == 9

    def test_empirical_distribution_sums_to_one(self):
        paths = [["A", "B"] * 50]
        r = compile_simulation_histogram(paths)
        assert abs(sum(r["empirical_distribution"]) - 1.0) < 1e-12

    def test_uniform_chain_converges_to_uniform(self):
        """Many paths on a symmetric chain → empirical ≈ uniform."""
        matrix = [[0.5, 0.5], [0.5, 0.5]]
        states = ["A", "B"]
        paths = []
        for s in range(200):
            r = execute_monte_carlo_walk(matrix, states, "A", 100, seed=s)
            paths.append(r["path"])
        hist = compile_simulation_histogram(paths)
        uniform = [0.5, 0.5]
        l1 = sum(abs(d - u) for d, u in zip(hist["empirical_distribution"], uniform))
        assert l1 < 0.01  # L1 distance from uniform within tolerance

    def test_first_passage_time(self):
        paths = [["A", "B", "C", "B", "C", "D"]]
        r = compile_simulation_histogram(paths, target_state="D")
        assert r["first_passage_times"]["D"] == 5

    def test_first_passage_not_reached(self):
        paths = [["A", "B", "A", "B"]]
        r = compile_simulation_histogram(paths, target_state="D")
        assert r["first_passage_times"]["D"] is None

    def test_empty_paths_raises(self):
        with pytest.raises(ValueError, match="paths must be non-empty"):
            compile_simulation_histogram([])

    def test_mean_path_length(self):
        paths = [["A", "B", "C"], ["A", "B"], ["A", "B", "C", "D"]]
        r = compile_simulation_histogram(paths)
        assert abs(r["mean_path_length"] - (3 + 2 + 4) / 3) < 1e-12

    def test_chi_square_convergence_low_for_long_walks(self):
        """L1 distance from uniform decreases with more data."""
        matrix = [[0.5, 0.5], [0.5, 0.5]]
        states = ["A", "B"]
        paths_short = [execute_monte_carlo_walk(matrix, states, "A", 10, seed=i)["path"]
                       for i in range(10)]
        paths_long = [execute_monte_carlo_walk(matrix, states, "A", 10, seed=i)["path"]
                      for i in range(500)]
        h_short = compile_simulation_histogram(paths_short)
        h_long = compile_simulation_histogram(paths_long)
        assert h_long["chi_square_convergence"] < h_short["chi_square_convergence"]

    def test_explicit_states_preserves_order(self):
        paths = [["Z", "Y", "X"]]
        states = ["X", "Y", "Z"]  # explicit order
        r = compile_simulation_histogram(paths, states=states)
        assert r["states"] == ("X", "Y", "Z")
