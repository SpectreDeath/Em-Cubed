---
name: tri-engine-replay-engine
description: Records timestamped execution frames into a cryptographic Merkle hash chain for deterministic replay and retrospective verification.
---

# Tri-Engine Verifiable Replay Engine Skill (`tri-engine-replay-engine`)

This skill captures execution state frames (SME trust, Em-Cubed Topos $\Omega$, Strategify actor moves) into a cryptographic SHA-256 Merkle hash chain, enabling step-by-step replay and tamper verification.

---

## 💻 Programmatic Usage Example

```python
from em_cubed.ontology.replay_engine import EpistemicReplayEngine

# 1. Record frames
engine = EpistemicReplayEngine()
f1 = engine.record_frame(0, 0.89, "Necessary", {"actors": 10})
f2 = engine.record_frame(1, 0.95, "Necessary", {"actors": 15})

# 2. Verify hash chain integrity
print("Hash Chain Valid:", engine.verify_integrity())

# 3. Replay step
step = engine.replay_step(1)
print(f"Replayed Step 1 Actors: {step.strategify_actor_state}")
```
