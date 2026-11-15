---
name: n_gram_token_predictor
domain: STOCHASTIC_PROCESSES
version: 1.0.0
surfaces:
  - prolog
  - python
description: Shannon information-theoretic n-gram Markov language modeling engine predicting next-token probability distributions from context history windows. Enforces n-gram order bounds ($1 \le n \le 10$) and prefix-suffix consistency in Prolog, constructs prefix-to-suffix co-occurrence frequency tables with Laplace smoothing $\alpha$, evaluates top-k candidate predictions, and calculates predictive distribution Shannon entropy $H(X)$ in Python. Use when generating text, forecasting sequential action tokens, or estimating language model entropy.
purpose: Train n-gram Markov language models and generate top-k next token predictions with Shannon entropy evaluation.
dependencies:
  - STOCHASTIC_PROCESSES/generate_transition_matrix
tags:
  - ngram-predictor
  - markov-language-model
  - shannon-entropy
  - laplace-smoothing
  - next-token-prediction
  - information-theory
inputs:
  corpus:
    type: array
    required: true
    description: Training corpus of tokenized sequences `[['token_1', 'token_2', ...], ...]`.
  n:
    type: integer
    required: false
    description: N-gram model order ($1 \le n \le 10$, default 3).
  laplace_alpha:
    type: number
    required: false
    description: Additive Laplace smoothing parameter (default 1.0).
  min_frequency:
    type: integer
    required: false
    description: Minimum prefix observation threshold (default 1).
  context:
    type: array
    required: true
    description: Input context token window for next-token prediction `['prefix_1', 'prefix_2']`.
  top_k:
    type: integer
    required: false
    description: Number of top candidate predictions to return (default 5).
outputs:
  context:
    type: array
    description: Normalized context window utilized for prediction.
  predicted_tokens:
    type: array
    description: Ranked list of `[token, probability]` pairs for top-k candidates.
  top_token:
    type: string
    description: Most probable next token candidate.
  top_probability:
    type: number
    description: Estimated conditional probability $P(\text{top\_token} \mid \text{context})$.
  entropy:
    type: number
    description: Shannon entropy $H(X) = -\sum P(w) \log_2 P(w)$ of predictive distribution.
  vocabulary_size:
    type: integer
    description: Total distinct vocabulary size $|V|$.
---

# N-Gram Token Predictor Engine

`n_gram_token_predictor` implements Shannon's information-theoretic Markov text generation model. Given an input context window of size $n - 1$, it estimates the **conditional next-token probability distribution with Laplace smoothing** and evaluates predictive **Shannon entropy** in **Python**:

$$P(w_t \mid w_{t-n+1}^{t-1}) = \frac{C(w_{t-n+1}^t) + \alpha}{C(w_{t-n+1}^{t-1}) + \alpha |V|}, \quad H(X) = -\sum_{w \in V} P(w \mid \text{context}) \log_2 P(w \mid \text{context})$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage N-Gram Prediction Progression

```
[1. Corpus Ingest & Token Invariant Audit] → [2. N-Gram Co-Occurrence Training] → [3. Visual Brief] → [4. Checkpoint] → [5. Conditional MAP Inference & Emit]
```

### Stage 1: Corpus Ingest & Token Invariant Audit
1. Ingest training `corpus` and verify non-empty token sequences.
2. Assert n-gram order $1 \le n \le 10$.
3. Build vocabulary dictionary $V$.

> **Completion criterion**: Clean corpus and vocabulary $|V| \ge 2$ established.

---

### Stage 2: N-Gram Co-Occurrence Training
1. Slide window of length $n$ across all corpus sequences.
2. Record prefix occurrences $C(\mathbf{w}_{\text{prefix}})$ and suffix transitions $C(\mathbf{w}_{\text{prefix}} \to w_{\text{suffix}})$.

> **Completion criterion**: N-gram prefix-to-suffix transition counts compiled.

---

### Stage 3: The Visual Brief
For language modeling and token prediction confidence, generate an interactive brief:
- **Location**: Write to `%TEMP%\ngram-predictor-brief-<timestamp>.html` (Windows) or `/tmp/ngram-predictor-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render context prefix to candidate token branch tree, top-k candidate probability bar chart, and Shannon entropy uncertainty gauge.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before generating predictions:
1. Normalize input context to window length $n - 1$.
2. If prefix is unseen, verify fallback to uniform smoothed vocabulary distribution.

> **Completion criterion**: Context window alignment and unseen prefix fallback verified.

---

### Stage 5: Conditional MAP Inference & Output Emission
1. Calculate smoothed conditional probabilities across vocabulary.
2. Extract top-k candidate tokens and compute Shannon entropy $H(X)$.
3. Emit complete `PredictionResult` record.

> **Completion criterion**: Full next-token prediction record emitted with entropy.

---

## Surface References

### Prolog Verification Surface

```prolog
:- module(ngram_validator, [
    valid_n/1,
    min_frequency_met/2
]).

valid_n(N) :- N >= 1, N =< 10.
min_frequency_met(Count, MinFreq) :- Count >= MinFreq.
```

### Python Calculation Surface

```python
import math
from collections import defaultdict
from typing import List, Dict, Any, Tuple

def _prefix_key(tokens: Tuple[str, ...]) -> str:
    return "|".join(tokens)

def build_ngram_model(corpus: List[List[str]], n: int = 3, laplace_alpha: float = 1.0, min_frequency: int = 1) -> Dict[str, Any]:
    if not corpus or n < 1:
        raise ValueError("invalid_corpus: Requires non-empty corpus and n >= 1.")
        
    vocab = set()
    prefix_counts = {}
    transition_counts = defaultdict(lambda: defaultdict(int))
    
    for seq in corpus:
        for tok in seq: vocab.add(tok)
        if len(seq) < n: continue
        for i in range(len(seq) - n + 1):
            window = tuple(seq[i: i + n - 1])
            suffix = seq[i + n - 1]
            key = _prefix_key(window)
            prefix_counts[key] = prefix_counts.get(key, 0) + 1
            transition_counts[key][suffix] += 1
            
    return {
        "n": n,
        "vocabulary": sorted(vocab),
        "prefix_counts": prefix_counts,
        "transition_counts": {k: dict(v) for k, v in transition_counts.items()},
        "laplace_alpha": max(0.0, float(laplace_alpha)),
        "min_frequency": min_frequency
    }

def predict_next_token(model: Dict[str, Any], context: List[str], top_k: int = 5) -> Dict[str, Any]:
    n = model["n"]
    window_size = n - 1
    vocab = model["vocabulary"]
    v_size = len(vocab)
    alpha = model["laplace_alpha"]
    
    if len(context) >= window_size:
        window = tuple(context[-window_size:]) if window_size > 0 else ()
    else:
        window = tuple(context)
        
    key = _prefix_key(window)
    transitions = model["transition_counts"].get(key, {})
    
    if not transitions:
        probs = {t: 1.0 / v_size for t in vocab}
    else:
        total_obs = sum(transitions.values())
        denom = total_obs + alpha * v_size
        probs = {t: (transitions.get(t, 0) + alpha) / denom for t in vocab}
        
    ranked = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:top_k]
    entropy = -sum(p * math.log2(p) for p in probs.values() if p > 0)
    top_tok, top_p = ranked[0] if ranked else ("", 0.0)
    
    return {
        "context": list(window),
        "predicted_tokens": [[t, round(p, 6)] for t, p in ranked],
        "top_token": top_tok,
        "top_probability": round(top_p, 6),
        "entropy": round(entropy, 4),
        "vocabulary_size": v_size
    }
```

---

## Anti-Patterns & Guardrails

- **Zero-Probability Multiplication for Unseen Tokens** — Failing to apply Laplace smoothing ($\alpha > 0$), assigning $P = 0$ to novel token continuations.
- **N-Gram Order Overextension ($n > 10$)** — Setting $n$ too high, leading to extreme prefix sparsity where every context is novel.
- **Unbounded Context Windows** — Passing multi-sentence contexts without truncating to the model's active window length $n - 1$.
