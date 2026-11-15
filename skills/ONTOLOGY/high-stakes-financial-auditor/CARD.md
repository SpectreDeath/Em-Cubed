# Skill Summary Card: `high-stakes-financial-auditor`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        high-stakes-financial-auditor             │
│ Category:    ONTOLOGY / High-Stakes Financial Audit    │
│ Invocation:  /high-stakes-financial-auditor            │
│ Trigger:     "audit financial transaction",            │
│              "verify balance proof", "graphrag payout" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Zero-hallucination transaction auditing   │
│              via Graph-Path RAG, prompt steering, and  │
│              Z3 SMT symbolic balance verification.     │
└────────────────────────────────────────────────────────┘
```

---

## The 6-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Request Audit** | Validate transaction schema & amount bounds | Validated Payload | Structural validation passed with $Amount > 0$ |
| **2. Graph-Path RAG** | Traverse semantic triples to verify ownership | Traversal Subgraph | Valid path from Account to KYC user |
| **3. Prompt Steering** | Inject functional property uniqueness rules | Prompt Directives | Rules bound to agent context |
| **4. Visual Brief** | Render transaction flow and balance shifts | `%TEMP%\financial-audit-brief-*.html` | Dark theme HTML audit brief |
| **5. Checkpoint** | Gate approval on high-value thresholds | `implementation_plan.md` | Human confirmation on high-risk payouts |
| **6. SMT Proof & Trail** | Execute Z3 balance proof and export JSON-LD | JSON-LD Trail Object | Z3 proof `sat` and audit trail exported |

---

## Invariants & Guardrails

- [ ] **Exact Balance Non-Negativity**: Post-transaction balance must be algebraically $\ge 0$.
- [ ] **Zero Hallucination Tolerance**: No approval without symbolic Z3 satisfaction.
- [ ] **Provenance Trail**: Every verdict must export verifiable JSON-LD audit metadata.
