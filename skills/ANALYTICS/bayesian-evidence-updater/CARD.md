# Skill Summary Card: `bayesian-evidence-updater`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        bayesian-evidence-updater                 │
│ Category:    ANALYTICS / Bayesian Forensic Inference   │
│ Invocation:  /bayesian-evidence-updater                │
│ Trigger:     "update bayesian evidence",               │
│              "compute posterior distribution",         │
│              "mece hypothesis audit", "bayesian update"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Sequential conditional probability updates│
│              with Prolog MECE hypothesis audits and    │
│              atomic SQLite state persistence.          │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate prior distribution bounds & likelihoods | Normalized Prior Map | $\sum P(H_i) = 1.0 \pm 10^{-4}$ & $P \ge 0$ |
| **2. MECE Check** | Verify exclusivity and exhaustiveness in Prolog | Prolog Audit Status | `audit_hypothesis_space/1` passes |
| **3. Visual Brief** | Render prior vs posterior shifts & $P(E)$ gauge | `%TEMP%\bayesian-updater-brief-*.html`| Dark theme HTML probability brief |
| **4. Checkpoint** | Validate non-zero marginal likelihood $P(E)$ | Marginal Gating Record | $P(E) > 10^{-8}$ confirmed |
| **5. Update & Commit**| Compute normalized posteriors & commit SQLite | Updated Distribution Array| Posteriors committed and sum to 1.0 |

---

## Invariants & Guardrails

- [ ] **Sum-to-One Normalization**: $\sum P_{\text{post}}(H_i) = 1.0 \pm 10^{-6}$.
- [ ] **Zero-Marginal Gate**: Abort immediately if marginal probability $P(E) \le 10^{-8}$.
- [ ] **Atomic SQLite Updates**: All hypothesis updates committed within a single transaction.
