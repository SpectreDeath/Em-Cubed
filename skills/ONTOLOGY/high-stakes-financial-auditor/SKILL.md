---
name: high-stakes-financial-auditor
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - z3
  - datalog
description: High-stakes financial transaction auditor combining Graph-Path RAG, constraint-aware prompt steering, and Z3 SMT symbolic balance proofs. Enforces zero-hallucination compliance across multi-hop semantic triples, verifies balance invariants ($Assets = Liabilities + Equity$), and exports JSON-LD compliance audit trails. Use when auditing high-value transactions, validating financial reconciliation ledgers, or verifying regulatory payout rules.
purpose: Enforce zero-hallucination compliance for high-stakes financial transactions via Graph-Path RAG and Z3 SMT proof verification.
dependencies: []
tags:
  - financial-auditor
  - graphrag
  - z3-smt
  - zero-hallucination
  - json-ld-audit
  - datalog
inputs:
  transaction_request:
    type: object
    required: true
    description: Financial payout or transaction payload to audit.
  knowledge_graph_triples:
    type: array
    required: true
    description: Ambient financial ledger triples and account ownership relations.
  regulatory_rules:
    type: array
    required: false
    description: Compliance constraints and functional uniqueness directives.
outputs:
  audit_verdict:
    type: string
    description: "approved | rejected | escalated_to_human"
  z3_proof_verified:
    type: boolean
    description: True if symbolic balance equations and invariants hold in Z3.
  json_ld_audit_trail:
    type: object
    description: Machine-verifiable JSON-LD proof trace.
---

# High-Stakes Financial Auditor Engine

`high-stakes-financial-auditor` demonstrates **Phase 2 Neurosymbolic AI** in `Em-Cubed`. It enforces **zero-hallucination compliance** for financial transactions by uniting multi-hop Graph-Path RAG, constraint-aware steering, and Z3 SMT symbolic proof verification.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 6-Stage Financial Audit Progression

```
[1. Request Invariant Audit] → [2. Graph-Path RAG] → [3. Constraint Steering] → [4. Visual Brief] → [5. Checkpoint] → [6. SMT Proof & Trail]
```

### Stage 1: Request Invariant Audit
1. Parse `transaction_request` parameters (account IDs, amounts, currency, signatures).
2. Validate non-negativity ($Amount > 0$) and currency ISO formatting.

> **Completion criterion**: Transaction payload structurally validated with positive amounts.

---

### Stage 2: Graph-Path RAG Traversal
1. Traverse semantic triples in Datalog to establish ownership and authorization paths:
   $$\text{Account} \xrightarrow{\text{belongsTo}} \text{User} \xrightarrow{\text{hasKYC}} \text{Verified}$$
2. Isolate relevant transaction context subgraph.

> **Completion criterion**: Complete authorization subgraph traversed and isolated.

---

### Stage 3: Constraint-Aware Prompt Steering
1. Inject OWL functional property rules into prompt directives (e.g. *Max 1 Refund per Order*).
2. Enforce disjoint class boundaries between customer accounts and settlement reserves.

> **Completion criterion**: Strict compliance steering directives compiled and bound to LLM context.

---

### Stage 4: The Visual Brief
For high-value or disputed transactions ($> \$50,000$), generate an interactive audit brief:
- **Location**: Write to `%TEMP%\financial-audit-brief-<timestamp>.html` (Windows) or `/tmp/financial-audit-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render transaction flow diagram, account balance shifts, and proof status.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 5: Mandatory Checkpoint
Before approving payout or modifying balance ledgers:
1. Halt for human confirmation on transactions flagged with compliance risk or exceeding threshold limits.
2. Provide explicit `implementation_plan.md` checkpoint with `RequestFeedback: true`.

> **Completion criterion**: Checkpoint reviewed and verified against anti-fraud policies.

---

### Stage 6: Z3 SMT Symbolic Proof & JSON-LD Emit
1. Formulate algebraic balance constraints in Z3:
   $$\text{Balance}_{\text{post}} = \text{Balance}_{\text{prev}} - \text{Amount} \ge 0$$
2. Execute solver check. If `sat`, emit JSON-LD verifiable audit trail with `approved`.

> **Completion criterion**: Z3 proof verified and machine-readable JSON-LD audit trail exported.

---

## Surface References

### Python & Z3 Audit Surface

```python
from typing import Dict, Any
from z3 import Solver, Real, sat

def verify_financial_payout(account_balance: float, payout_amount: float, max_limit: float = 10000.0) -> Dict[str, Any]:
    s = Solver()
    bal = Real("balance")
    amt = Real("amount")
    
    s.add(bal == account_balance)
    s.add(amt == payout_amount)
    s.add(amt > 0)
    s.add(amt <= max_limit)
    s.add(bal - amt >= 0.0)
    
    is_valid = s.check() == sat
    return {
        "audit_verdict": "approved" if is_valid else "rejected",
        "z3_proof_verified": is_valid,
        "json_ld_audit_trail": {
            "@context": "https://schema.org",
            "@type": "FinancialTransactionAudit",
            "payout_amount": payout_amount,
            "status": "Verified" if is_valid else "Violated"
        }
    }
```

---

## Anti-Patterns & Guardrails

- **Hallucinated Authorization** — Granting transaction approval based solely on ungrounded LLM completions without Z3 mathematical proof verification.
- **Floating Point Imprecision** — Calculating currency balances with naive floating point math. Always use exact integer cents or Z3 `Real` rationals.
- **Missing Audit Provenance** — Approving payouts without emitting a cryptographic JSON-LD proof trail.
