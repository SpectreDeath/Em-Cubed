# Skill Summary Card: `markov-chain-sequence`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        markov-chain-sequence                     │
│ Category:    ANALYTICS / Markovian State Dynamics      │
│ Invocation:  /markov-chain-sequence                    │
│ Trigger:     "step markov chain", "markov sequence",   │
│              "stochastic transition", "state walk"     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Simulate discrete Markov chain transitions│
│              with Prolog stochastic row validation     │
│              and cumulative density sampling.          │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate state vocabulary and positive weights | State Transition AST | $P_{ij} \ge 0.0$ and current state valid |
| **2. Prolog Row Check**| Assert row probabilities sum to unity | Prolog Proof Status | $\sum P_{ij} = 1.0 \pm 10^{-4}$ verified |
| **3. Visual Brief** | Render state transition graph & probability weights| `%TEMP%\markov-chain-brief-*.html`| Dark theme HTML transition graph |
| **4. Checkpoint** | Validate absorbing states & random bounds | Safety Gate Record | $r \in [0.0, 1.0]$ validated |
| **5. Cumulative Step** | Sample next state via CDF & emit | Sampled Transition Step | Valid destination state returned |

---

## Invariants & Guardrails

- [ ] **Row Normalization**: Every state row must sum to $1.0 \pm 0.0001$.
- [ ] **State Closure**: All destination states must be valid keys in the transition matrix.
- [ ] **Memoryless Invariant**: $P(S_{t+1} \mid S_t, \dots, S_0) = P(S_{t+1} \mid S_t)$.
