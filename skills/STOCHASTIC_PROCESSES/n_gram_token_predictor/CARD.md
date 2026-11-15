# Skill Summary Card: `n_gram_token_predictor`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        n_gram_token_predictor                    │
│ Category:    STOCHASTIC_PROCESSES / Language Models    │
│ Invocation:  /n_gram_token_predictor                   │
│ Trigger:     "n gram token predictor", "ngram model",  │
│              "next token prediction", "shannon entropy"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Shannon n-gram language model for next-   │
│              token probability estimation, Laplace     │
│              smoothing & predictive entropy evaluation.│
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest training corpus & validate $1 \le n \le 10$| Training Corpus AST | Non-empty corpus verified |
| **2. Training** | Count prefix $\to$ suffix transitions with Laplace $\alpha$| N-Gram Transition Table | Co-occurrences compiled |
| **3. Visual Brief** | Render prefix-token tree & candidate probabilities| `%TEMP%\ngram-predictor-brief-*.html`| Dark theme HTML n-gram brief |
| **4. Checkpoint** | Validate context alignment ($n-1$ window size) | Window Decision Record | Window length verified |
| **5. Model Emission** | Calculate top-k predictions & Shannon entropy $H(X)$| `PredictionResult` Payload | Full prediction payload emitted |

---

## Invariants & Guardrails

- [ ] **N-Gram Order Bound**: $1 \le n \le 10$ enforced via Prolog.
- [ ] **Laplace Smoothing**: $\alpha \ge 0.0$ applied to eliminate zero-probability paths.
- [ ] **Predictive Entropy**: $H(X) = -\sum P \log_2 P \ge 0.0$.
