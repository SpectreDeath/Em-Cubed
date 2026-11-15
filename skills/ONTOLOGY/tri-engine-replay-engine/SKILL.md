---
name: tri-engine-replay-engine
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Cryptographic Merkle-hashed execution frame recorder and deterministic retrospective replay engine. Captures multi-agent state frames (SME trust, Em-Cubed Topos Omega, Strategify actor actions) into a tamper-evident SHA-256 hash chain, verifies audit integrity, and replays state frames step-by-step. Use when recording verifiable multi-agent audit trails, verifying cryptographic ledger integrity, or debugging past execution states retrospectively.
purpose: Record execution state frames into a tamper-evident SHA-256 Merkle hash chain and execute deterministic step-by-step replays.
dependencies: []
tags:
  - replay-engine
  - merkle-chain
  - sha256-integrity
  - retrospective-audit
  - tri-engine
inputs:
  action_type:
    type: string
    required: true
    description: "record_frame | verify_integrity | replay_step | export_audit_log"
  frame_data:
    type: object
    required: false
    description: State snapshot data (step, trust_score, topos_truth, actor_state).
  target_step:
    type: integer
    required: false
    description: Specific step index to replay or inspect.
outputs:
  frame_record:
    type: object
    description: Captured frame with step, state payload, and SHA-256 block hash.
  chain_valid:
    type: boolean
    description: True if Merkle hash chain passes end-to-end cryptographic verification.
  replayed_state:
    type: object
    description: Fully reconstructed state snapshot for target step.
---

# Tri-Engine Verifiable Replay Engine

`tri-engine-replay-engine` captures execution state frames (SME trust, Em-Cubed Topos $\Omega$, Strategify actor moves) into a cryptographic SHA-256 Merkle hash chain, providing mathematical proof of audit integrity and deterministic retrospective execution replay.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Replay & Audit Progression

```
[1. Frame Invariant Audit] → [2. Merkle Hash Linking] → [3. Visual Brief] → [4. Checkpoint] → [5. Verification & Replay]
```

### Stage 1: Frame Invariant Audit
1. Ingest `frame_data` containing step index, Topos truth value ($\Omega$), and multi-engine actor state.
2. Validate strict monotonic step incrementation ($Step_{n} = Step_{n-1} + 1$).

> **Completion criterion**: Frame data validated with sequential step indexing.

---

### Stage 2: Merkle Hash Linking (SHA-256)
1. Serialize state payload deterministically to canonical JSON.
2. Compute cryptographic block hash linked to prior block hash:
   $$\text{Hash}_n = \text{SHA256}(\text{Step}_n \parallel \text{Payload}_n \parallel \text{Hash}_{n-1})$$

> **Completion criterion**: Frame hash computed and linked into persistent Merkle chain.

---

### Stage 3: The Visual Brief
For complete audit logs or detected chain corruptions, generate an interactive brief:
- **Location**: Write to `%TEMP%\replay-engine-brief-<timestamp>.html` (Windows) or `/tmp/replay-engine-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the cryptographic block chain, step states, and verification hash graph.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before overwriting active agent state with replayed retrospective state:
1. Verify cryptographic integrity of the entire chain from genesis block to target step.
2. If hash mismatch is detected, pause immediately and flag tamper alert.

> **Completion criterion**: Hash integrity verified with zero broken links.

---

### Stage 5: Retrospective Replay & Ledger Emit
1. Reconstruct exact system state at requested `target_step`.
2. Emit state payload, hash chain validation status, and audit trail record.

> **Completion criterion**: Replay completed with `chain_valid: true` and bit-accurate state restoration.

---

## Surface References

### Python Epistemic Replay Surface

```python
import hashlib
import json
from typing import Dict, Any, List

class EpistemicReplayEngine:
    def __init__(self):
        self.chain = []
        self.prev_hash = "0" * 64

    def record_frame(self, step: int, trust: float, topos: str, actor_state: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"step": step, "trust": trust, "topos": topos, "actor_state": actor_state}
        serialized = json.dumps(payload, sort_keys=True)
        block_hash = hashlib.sha256(f"{serialized}{self.prev_hash}".encode()).hexdigest()
        
        frame = {"step": step, "payload": payload, "prev_hash": self.prev_hash, "hash": block_hash}
        self.chain.append(frame)
        self.prev_hash = block_hash
        return frame

    def verify_integrity(self) -> bool:
        prev = "0" * 64
        for frame in self.chain:
            if frame["prev_hash"] != prev:
                return False
            serialized = json.dumps(frame["payload"], sort_keys=True)
            expected = hashlib.sha256(f"{serialized}{prev}".encode()).hexdigest()
            if frame["hash"] != expected:
                return False
            prev = frame["hash"]
        return True

    def replay_step(self, step: int) -> Dict[str, Any]:
        for frame in self.chain:
            if frame["step"] == step:
                return frame["payload"]
        return {}
```

---

## Anti-Patterns & Guardrails

- **Non-Deterministic Serialization** — Generating JSON hashes without key sorting, producing false-positive hash corruption alerts.
- **Unverified State Overwrites** — Restoring a past execution frame without validating the hash chain from genesis.
- **Mutable Historical Frames** — Allowing modifications to existing frames in the chain after append.
