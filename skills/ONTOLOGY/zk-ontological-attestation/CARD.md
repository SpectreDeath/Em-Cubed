# Skill Summary Card: `zk-ontological-attestation`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        zk-ontological-attestation                │
│ Category:    ONTOLOGY / Cryptographic Zero-Knowledge   │
│ Invocation:  /zk-ontological-attestation               │
│ Trigger:     "generate zkp attestation", "zk proof",   │
│              "zero knowledge ontology", "merkle proof" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Cryptographic Zero-Knowledge Proof (ZKP)  │
│              commitments over sensitive subgraphs to   │
│              prove compliance without leaking data.    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Isolate sensitive triples and formalize statement| Segregated Data Spec | Private data separated from public goal |
| **2. Merkle Root** | Hash leaves and compute Merkle tree root | Merkle Root Hash | Root computed over sorted leaf hashes |
| **3. Visual Brief** | Render ZKP commitment tree and proof path | `%TEMP%\zk-attestation-brief-*.html`| Dark theme HTML proof tree brief |
| **4. Checkpoint** | Validate zero plaintext leakage | Safety Gate Record | Zero sensitive plaintext in public output |
| **5. ZKP Minting** | Sign proof payload and emit token | Verifiable Proof Token | Token emitted with valid cryptographic signature |

---

## Invariants & Guardrails

- [ ] **Zero Data Leakage**: No private entity literal may appear unhashed in the public proof token.
- [ ] **Cryptographic Entailment**: Committed Merkle root must mathematically ground the proposition.
- [ ] **Deterministic Ordering**: Leaves must be sorted before building Merkle root.
