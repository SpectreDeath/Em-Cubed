# Skill Summary Card: `tri-engine-replay-engine`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        tri-engine-replay-engine                  │
│ Category:    ONTOLOGY / Cryptographic Audit & Replay  │
│ Invocation:  /tri-engine-replay-engine                 │
│ Trigger:     "record replay frame", "verify hash chain",│
│              "replay execution step", "merkle audit"   │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Capture execution frames into a SHA-256   │
│              Merkle hash chain, verify integrity, and  │
│              execute deterministic step replays.       │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Frame Invariants** | Validate step monotonic sequence & payload AST | Validated Frame Data | Monotonic step index verified |
| **2. Merkle Hash** | Compute canonical SHA-256 block hash | Linked Block Record | Block cryptographically bound to parent |
| **3. Visual Brief** | Render Merkle block graph and state shifts | `%TEMP%\replay-engine-brief-*.html` | Dark theme HTML blockchain brief |
| **4. Checkpoint** | Validate end-to-end hash chain integrity | Cryptographic Proof | Zero hash mismatches across all blocks |
| **5. Replay & Emit** | Reconstruct state snapshot for target step | Replayed State Snapshot | Bit-accurate state returned with status |

---

## Invariants & Guardrails

- [ ] **Strict Monotonicity**: $Step_{n} = Step_{n-1} + 1$.
- [ ] **Deterministic Hashing**: Canonical JSON serialization with sorted keys.
- [ ] **Immutable History**: Once appended, prior frame hashes must never be modified.
