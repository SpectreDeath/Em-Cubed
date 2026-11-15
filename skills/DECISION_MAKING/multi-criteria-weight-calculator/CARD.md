# Skill Summary Card: `multi-criteria-weight-calculator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        multi-criteria-weight-calculator          │
│ Category:    DECISION_MAKING / MCDA Weighting          │
│ Invocation:  /multi-criteria-weight-calculator         │
│ Trigger:     "multi criteria weight calculator",       │
│              "ahp weights", "topsis ranking", "mcda",  │
│              "consistency ratio", "entropy weights"    │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Derive criteria weights via AHP, TOPSIS,  │
│              Entropy & Fuzzy AHP with Prolog $CR \le   │
│              0.10$ consistency ratio verification.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest criteria names & pairwise/decision matrix | MCDA Problem AST | $n \ge 2$ criteria verified |
| **2. Eigenvector** | Compute principal eigenvector weights & $\lambda_{\text{max}}$| Unnormalized Weight Record| Weights $\mathbf{w}$ solved |
| **3. Visual Brief** | Render criteria weight bars & AHP comparison matrix| `%TEMP%\multi-criteria-brief-*.html`| Dark theme HTML brief |
| **4. Checkpoint** | Validate AHP consistency threshold ($CR \le 0.10$)| Consistency Gate Record | $CR \le 0.10$ certified in Prolog|
| **5. Model Emission** | Normalize weights $\sum w_i = 1$ & emit rankings | `MCDAWeightResult` Payload | Full weight payload emitted |

---

## Invariants & Guardrails

- [ ] **AHP Consistency Invariant**: $CR = CI / RI \le 0.10$.
- [ ] **Weight Conservation**: $\sum_{i=1}^n w_i = 1.0 \pm 10^{-6}$.
- [ ] **Positive Comparison Entries**: $A_{ij} \in [1/9, 9]$ with reciprocal symmetry $A_{ji} = 1/A_{ij}$.
