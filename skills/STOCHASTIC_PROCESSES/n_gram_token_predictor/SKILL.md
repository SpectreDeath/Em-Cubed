---
name: n_gram_token_predictor
domain: STOCHASTIC_PROCESSES
version: "1.0.0"
surfaces: [prolog, python]
description: |
  Shannon-style n-gram language model that predicts the next token
  from a context window of n-1 previous tokens.  Prolog verifies
  prefix-suffix consistency and enforces minimum frequency thresholds;
  Python computes conditional probabilities.
compatibility: PROLOG, PYTHON
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

# N-Gram Token Predictor

## Purpose
Implement Shannon's information-theoretic text approximation via n-gram Markov chains. Given a corpus of token sequences, the skill builds a conditional probability model P(token | context_window) and predicts the most likely next token(s) given a prefix (context window).

## Connection to Veritasium
- **Andrei Markov's vowel-consonant text**: Markov derived a transition matrix from Pushkin's Eugene Onegin, modeling letter sequences as a stochastic process.
- **Claude Shannon**: extended the idea to word-level and character-level trigram models for estimating English entropy and generating plausible text.
- **M³ agent context**: An agent's working memory history acts as the "prefix" fed into the n-gram model to predict the next action token.

## Description
Hybrid skill:
- **Prolog layer** — Verifies that every observed suffix is a valid continuation of its prefix; enforces minimum observation counts (e.g., a prefix must appear at least `min_frequency` times to be considered reliable).
- **Python layer** — Counts (prefix → suffix) co-occurrences at window size `n`, applies Laplace smoothing, and samples or argmax-predicts the next token.

### N-gram Conditional Probability
```
P(token_t | prefix) = (count(prefix + token) + α) / (count(prefix) + α * V)
```
where:
- `prefix` = (token_{t-n+1}, ..., token_{t-1})
- `V` = vocabulary size
- `α` = Laplace smoothing constant

## Prolog Surface (prelude.pl)

```prolog
:- module(ngram_validator, [
    prefix_suffix_consistent/2,
    min_frequency_met/2,
    valid_n/1,
    vocabulary_consistent/2
]).

% ============================================================
% 1. N-gram order validation
% ============================================================
valid_n(N) :- N >= 1, N =< 10.

% ============================================================
% 2. Minimum observation count threshold
% ============================================================
min_frequency_met(Count, MinFreq) :- Count >= MinFreq.

% ============================================================
% 3. Prefix-suffix consistency
%    (Prefix concatenated with Suffix) must have been observed.
% ============================================================
prefix_suffix_consistent(Prefix, Suffix) :-
    observed_ngram(Prefix, Suffix).

% ============================================================
% 4. Vocabulary consistency
%    Every token in the corpus must be in the vocabulary.
% ============================================================
vocabulary_consistent(CorpusTokens, Vocab) :-
    forall(
        member(Tok, CorpusTokens),
        memberchk(Tok, Vocab)
    ).
```

## Python Surface (executor.py)

```python
"""
n_gram_token_predictor
========================
Shannon-style n-gram Markov model for next-token prediction.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class NGramModel:
    n: int
    vocabulary: Tuple[str, ...]
    prefix_counts: Dict[str, int]           # prefix_str → total occurrences
    transition_counts: Dict[str, Dict[str, int]]  # prefix_str → {suffix: count}
    laplace_alpha: float
    min_frequency: int

    def to_dict(self) -> dict:
        return {
            "n":                 self.n,
            "vocabulary":        list(self.vocabulary),
            "prefix_counts":     dict(self.prefix_counts),
            "transition_counts": {k: dict(v) for k, v in self.transition_counts.items()},
            "laplace_alpha":     self.laplace_alpha,
            "min_frequency":     self.min_frequency,
        }


@dataclass(frozen=True)
class PredictionResult:
    context: Tuple[str, ...]
    predicted_tokens: Tuple[Tuple[str, float], ...]
    top_token: str
    top_probability: float
    entropy: float
    model_n: int

    def to_dict(self) -> dict:
        return {
            "context":           list(self.context),
            "predicted_tokens":  [list(t) for t in self.predicted_tokens],
            "top_token":         self.top_token,
            "top_probability":   self.top_probability,
            "entropy":           self.entropy,
            "model_n":           self.model_n,
        }


def _prefix_key(tokens: Tuple[str, ...]) -> str:
    """Serialize prefix to a stable hashable key."""
    return "|".join(tokens)


def build_ngram_model(
    corpus: List[List[str]],
    n: int = 3,
    laplace_alpha: float = 1.0,
    min_frequency: int = 1,
) -> NGramModel:
    """Train an n-gram Markov model from a corpus of token sequences.

    Parameters
    ----------
    corpus : list[list[str]]
        Each element is a tokenized sequence (sentence, action history, etc.).
    n : int
        N-gram order (1 = unigram, 2 = bigram, 3 = trigram, ...).
    laplace_alpha : float
        Additive smoothing constant.
    min_frequency : int
        Prefixes seen fewer than this times are kept but may produce
        degraded predictions.

    Returns
    -------
    NGramModel
    """
    if not corpus or n < 1:
        raise ValueError(f"corpus must be non-empty and n >= 1, got n={n}")

    vocab: set = set()
    prefix_counts: Dict[str, int] = {}
    transition_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

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
        n                 = n,
        vocabulary        = tuple(sorted(vocab)),
        prefix_counts     = dict(prefix_counts),
        transition_counts = dict(transition_counts),
        laplace_alpha     = laplace_alpha,
        min_frequency     = min_frequency,
    )


def predict_next(
    model: NGramModel,
    context: List[str],
    top_k: int = 5,
) -> PredictionResult:
    """Predict next token(s) given a context window.

    Parameters
    ----------
    model : NGramModel
        Trained model from build_ngram_model.
    context : list[str]
        Context window (any length; truncated/padded to model.n-1 automatically).
    top_k : int
        Return top-k predictions sorted by probability.

    Returns
    -------
    PredictionResult
    """
    n = model.n
    window_size = n - 1

    # Normalize context to window size
    if len(context) >= window_size:
        window = tuple(context[-window_size:]) if window_size > 0 else ()
    else:
        window = tuple(context)

    key = _prefix_key(window)
    v_size = len(model.vocabulary)
    alpha = model.laplace_alpha

    if key not in model.transition_counts:
        # Unseen prefix: uniform distribution over vocabulary
        probs = {t: 1.0 / v_size for t in model.vocabulary}
    else:
        suffix_counts = model.transition_counts[key]
        total_observed = sum(suffix_counts.values())
        denom = total_observed + alpha * v_size
        probs = {
            t: (suffix_counts.get(t, 0) + alpha) / denom
            for t in model.vocabulary
        }

    # Sort by probability descending
    ranked = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:top_k]

    # Shannon entropy of the predicted distribution
    entropy = -sum(p * math.log2(p) for p in probs.values() if p > 0)

    top_tok, top_p = ranked[0] if ranked else ("", 0.0)

    return PredictionResult(
        context           = window,
        predicted_tokens  = tuple(ranked),
        top_token         = top_tok,
        top_probability   = top_p,
        entropy           = entropy,
        model_n           = n,
    )
```

## Inputs

| name | type | description |
|---|---|---|
| corpus | list[list[str]] | Training data: list of tokenized sequences |
| n | int | N-gram order (1–10) |
| laplace_alpha | float | Laplace smoothing constant (default 1.0) |
| min_frequency | int | Min prefix occurrence threshold (default 1) |
| context | list[str] | Context window for prediction |
| top_k | int | Number of predictions to return (default 5) |

## Outputs

| name | type | description |
|---|---|---|
| vocabulary | tuple[str] | Token universe |
| prefix_counts | dict[str → int] | Prefix occurrence counts |
| transition_counts | dict[str → dict[str → int]] | (prefix → suffix) co-occurrence |
| predicted_tokens | list[tuple[str, float]] | Top-k (token, probability) pairs |
| top_token | str | Highest-probability next token |
| top_probability | float | Probability of top token |
| entropy | float | Shannon entropy of the predictive distribution |

## State Updates
```
state_add_observation("nlp/ngram/vocabulary_size", len(model.vocabulary))
state_add_observation("nlp/ngram/top_prediction", result.top_token)
belief_add(ngram_model_trained(N, VocabSize, Alpha))
```

## Error Handling
| Error | Condition |
|---|---|
| empty_corpus | corpus is empty |
| invalid_n | n < 1 or n > 10 |
| vocabulary_overflow | V > 10^6 (Prolog can flag) |

## Security
- No I/O. In-memory corpus indexing.
- Corpus strings not logged or transmitted.
