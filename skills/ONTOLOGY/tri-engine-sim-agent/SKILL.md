---
name: tri-engine-sim-agent
description: Orchestrates tri-engine geopolitical wargaming, SEIRH epidemiological biodefense, and Topos Ω modal truth governance across Strategify, Em-Cubed, and SME.
---

# Tri-Engine Simulation & Governance Agent Skill (`tri-engine-sim-agent`)

This skill orchestrates end-to-end tri-engine simulations uniting Perception (`SME`), Axiomatic Governance (`Em-Cubed`), and Agent-Based Simulation (`Strategify`).

---

## 🏛️ Tri-Engine Workflow Overview

1. **Perception Stage (`SME`)**:
   - `SMEOSINTBridge.fetch_epistemic_tension("Ukraine")` fetches real-world GDELT/OSINT sentiment and epistemic trust scores.
2. **Axiomatic Governance Stage (`Em-Cubed`)**:
   - `ToposDecisionBridge.evaluate_action_confidence("mobilize", 0.92)` classifies decision confidence in Topos $\Omega$ (`NECESSARY`).
   - `DLConflictGuard.guard_escalation("cyber_attack")` enforces Description Logic class expression bounds ($C \sqsubseteq D$).
3. **Macro-Simulation Stage (`Strategify`)**:
   - Runs Mesa Geo agent-based simulation and SEIRH biodefense model.
4. **Attestation & Verification Stage (`Em-Cubed`)**:
   - `ZKPBiodefenseAttestor.generate_biodefense_proof("MiddleEast", 0.85, 1.2)` seals trajectories with post-quantum Zero-Knowledge proofs ($s \Vdash A$).

---

## 💻 Programmatic Usage Example

```python
from strategify.osint.sme_adapter import SMEOSINTBridge
from strategify.logic.topos_bridge import ToposDecisionBridge
from strategify.sim.dl_guard import DLConflictGuard
from strategify.epidemiology.zkp_bridge import ZKPBiodefenseAttestor

# 1. Perception
perception = SMEOSINTBridge().fetch_epistemic_tension("Ukraine")

# 2. Governance
decision = ToposDecisionBridge.evaluate_action_confidence("mobilize", perception["epistemic_trust_score"])
guard = DLConflictGuard.guard_escalation("cyber_attack")

# 3. Attestation
proof = ZKPBiodefenseAttestor.generate_biodefense_proof("Ukraine", 0.85, 1.2)
print("Proof ID:", proof["proof_id"])
```
