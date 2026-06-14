"""Integration tests for n_gram_token_predictor stochastic process skill."""

import math
from collections import defaultdict

import pytest

def _prefix_key(tokens):
    return "|".join(tokens)

class NGramModel:
    def __init__(self, n, vocabulary, prefix_counts, transition_counts,
                 laplace_alpha, min_frequency):
        self.n = n
        self.vocabulary = vocabulary
        self.prefix_counts = prefix_counts
        self.transition_counts = transition_counts
        self.laplace_alpha = laplace_alpha
        self.min_frequency = min_frequency

class PredictionResult:
    def __init__(self, context, predicted_tokens, top_token,
                 top_probability, entropy, model_n):
        self.context = context
        self.predicted_tokens = predicted_tokens
        self.top_token = top_token
        self.top_probability = top_probability
        self.entropy = entropy
        self.model_n = model_n

def build_ngram_model(corpus, n=3, laplace_alpha=1.0, min_frequency=1):
    if not corpus or n < 1:
        raise ValueError(f"corpus must be non-empty and n >= 1, got n={n}")

    vocab = set()
    prefix_counts = {}
    transition_counts = defaultdict(lambda: defaultdict(int))

    for seq in corpus:
        if len(seq) < n:
            continue
        for tok in seq:
            vocab.add(tok)
        for i in range(len(seq) - n + 1):
            window = tuple(seq[i: i + n - 1])
            suffix = seq[i + n - 1]
            key = _prefix_key(window)
            prefix_counts[key] = prefix_counts.get(key, 0) + 1
            transition_counts[key][suffix] += 1

    return NGramModel(
        n=n,
        vocabulary=tuple(sorted(vocab)),
        prefix_counts=dict(prefix_counts),
        transition_counts=dict(transition_counts),
        laplace_alpha=laplace_alpha,
        min_frequency=min_frequency,
    )

def predict_next(model, context, top_k=5):
    n = model.n
    window_size = n - 1

    if window_size > 0:
        if len(context) >= window_size:
            window = tuple(context[-window_size:])
        else:
            window = tuple(context)
    else:
        window = ()

    key = _prefix_key(window)
    v_size = len(model.vocabulary)
    alpha = model.laplace_alpha

    if key not in model.transition_counts:
        probs = {t: 1.0 / v_size for t in model.vocabulary}
    else:
        suffix_counts = model.transition_counts[key]
        total_observed = sum(suffix_counts.values())
        denom = total_observed + alpha * v_size
        probs = {
            t: (suffix_counts.get(t, 0) + alpha) / denom
            for t in model.vocabulary
        }

    ranked = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:top_k]
    entropy = -sum(p * math.log2(p) for p in probs.values() if p > 0)

    top_tok, top_p = ranked[0] if ranked else ("", 0.0)

    return PredictionResult(
        context=window,
        predicted_tokens=tuple(ranked),
        top_token=top_tok,
        top_probability=top_p,
        entropy=entropy,
        model_n=n,
    )

def valid_n(n):
    return 1 <= n <= 10

def min_frequency_met(count, min_freq):
    return count >= min_freq

def prefix_suffix_consistent(prefix, suffix, transition_counts):
    key = _prefix_key(prefix)
    return key in transition_counts and suffix in transition_counts[key]

def vocabulary_consistent(corpus_tokens, vocab):
    return set(corpus_tokens).issubset(set(vocab))

class TestPrefixKey:
    def test_empty(self):
        assert _prefix_key(()) == ""

    def test_single(self):
        assert _prefix_key(("a",)) == "a"

    def test_multiple(self):
        assert _prefix_key(("a", "b", "c")) == "a|b|c"

class TestBuildNGramModel:
    def test_unigram(self):
        corpus = [["a", "b", "a"]]
        model = build_ngram_model(corpus, n=1)
        assert model.n == 1
        assert model.vocabulary == ("a", "b")
        assert model.prefix_counts == {"": 3}
        assert model.transition_counts == {"": {"a": 2, "b": 1}}

    def test_bigram(self):
        corpus = [["a", "b", "c"]]
        model = build_ngram_model(corpus, n=2)
        assert model.n == 2
        assert model.vocabulary == ("a", "b", "c")
        assert "a" in model.transition_counts
        assert model.transition_counts["a"]["b"] == 1
        assert model.transition_counts["b"]["c"] == 1

    def test_trigram(self):
        corpus = [["a", "b", "c", "d"]]
        model = build_ngram_model(corpus, n=3)
        assert model.n == 3
        assert model.vocabulary == ("a", "b", "c", "d")
        assert model.transition_counts["a|b"]["c"] == 1
        assert model.transition_counts["b|c"]["d"] == 1

    def test_vocabulary_extraction(self):
        corpus = [["x", "y", "z"], ["y", "z", "x"]]
        model = build_ngram_model(corpus, n=2)
        assert set(model.vocabulary) == {"x", "y", "z"}

    def test_empty_corpus_error(self):
        with pytest.raises(ValueError, match="n >= 1"):
            build_ngram_model([], n=2)

    def test_n_less_than_one_error(self):
        with pytest.raises(ValueError, match="n >= 1"):
            build_ngram_model([["a", "b"]], n=0)

    def test_multiple_sequences_combined(self):
        corpus = [["a", "b", "c"], ["a", "b", "d"]]
        model = build_ngram_model(corpus, n=2)
        assert model.transition_counts["a"]["b"] == 2
        assert model.transition_counts["b"]["c"] == 1
        assert model.transition_counts["b"]["d"] == 1

class TestPredictNext:
    def test_known_context_top_token(self):
        corpus = [["a", "b", "c", "d", "c"]]
        model = build_ngram_model(corpus, n=2)
        result = predict_next(model, ["b"])
        assert result.top_token == "c"

    def test_unseen_context_uniform(self):
        corpus = [["a", "b", "c"]]
        model = build_ngram_model(corpus, n=2)
        result = predict_next(model, ["z"])
        v_size = len(model.vocabulary)
        assert all(abs(p - 1.0 / v_size) < 1e-9 for _, p in result.predicted_tokens)

    def test_context_truncation_longer_than_window(self):
        corpus = [["a", "b", "c", "d", "e"]]
        model = build_ngram_model(corpus, n=2)
        result = predict_next(model, ["a", "b", "c", "d"])
        assert result.context == ("d",)

    def test_context_shorter_than_window_used_as_is(self):
        corpus = [["a", "b", "c"]]
        model = build_ngram_model(corpus, n=2)
        result = predict_next(model, ["a"])
        assert result.context == ("a",)

    def test_top_k_limited(self):
        corpus = [["a", "b", "c", "d"]]
        model = build_ngram_model(corpus, n=2)
        result = predict_next(model, ["a"], top_k=2)
        assert len(result.predicted_tokens) == 2

    def test_predicted_tokens_sorted_descending(self):
        corpus = [["a", "b", "b", "c", "b", "d"]]
        model = build_ngram_model(corpus, n=2)
        result = predict_next(model, ["a"])
        probs = [p for _, p in result.predicted_tokens]
        assert probs == sorted(probs, reverse=True)

class TestLaplaceSmoothing:
    def test_zero_frequency_suffix_nonzero_probability(self):
        corpus = [["a", "b", "c"]]
        model = build_ngram_model(corpus, n=2, laplace_alpha=1.0)
        result = predict_next(model, ["a"])
        vocab_set = set(model.vocabulary)
        unseen = vocab_set - set(model.transition_counts.get("a", {}))
        for token, prob in result.predicted_tokens:
            if token in unseen:
                assert prob > 0.0

    def test_probabilities_sum_to_one(self):
        corpus = [["a", "b", "c", "d"]]
        model = build_ngram_model(corpus, n=2, laplace_alpha=1.0)
        result = predict_next(model, ["a"])
        total = sum(p for _, p in result.predicted_tokens)
        assert abs(total - 1.0) < 1e-9

class TestEntropy:
    def test_uniform_distribution_log2_vocabulary(self):
        corpus = [["a", "b", "c"]]
        model = build_ngram_model(corpus, n=2)
        result = predict_next(model, ["z"])
        expected = math.log2(len(model.vocabulary))
        assert abs(result.entropy - expected) < 1e-9

    def test_deterministic_zero_entropy(self):
        corpus = [["x", "x", "x", "x"]]
        model = build_ngram_model(corpus, n=2, laplace_alpha=1.0)
        result = predict_next(model, ["x"])
        assert abs(result.entropy - 0.0) < 1e-9

class TestPrologValidation:
    def test_valid_n_in_range(self):
        assert valid_n(1) is True

    def test_valid_n_upper_bound(self):
        assert valid_n(10) is True

    def test_valid_n_below_range(self):
        assert valid_n(0) is False

    def test_valid_n_above_range(self):
        assert valid_n(11) is False

    def test_min_frequency_met(self):
        assert min_frequency_met(5, 3) is True
        assert min_frequency_met(3, 3) is True

    def test_min_frequency_not_met(self):
        assert min_frequency_met(2, 5) is False
        assert min_frequency_met(0, 1) is False

    def test_prefix_suffix_consistent_true(self):
        t = {"a|b": {"c": 2, "d": 1}}
        assert prefix_suffix_consistent(("a", "b"), "c", t) is True

    def test_prefix_suffix_consistent_false_missing_prefix(self):
        t = {"x|y": {}}
        assert prefix_suffix_consistent(("a", "b"), "c", t) is False

    def test_prefix_suffix_consistent_false_missing_suffix(self):
        t = {"a|b": {"c": 1}}
        assert prefix_suffix_consistent(("a", "b"), "z", t) is False

    def test_vocabulary_consistent_true(self):
        assert vocabulary_consistent(["a", "b", "c"], ("a", "b", "c", "d")) is True

    def test_vocabulary_consistent_false(self):
        assert vocabulary_consistent(["a", "b", "z"], ("a", "b", "c")) is False

    def test_vocabulary_consistent_empty_corpus(self):
        assert vocabulary_consistent([], ("a", "b")) is True
