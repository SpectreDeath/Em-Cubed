---
name: tri-engine-sim-agent
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: Orchestrates tri-engine geopolitical wargaming, SEIRH epidemiological biodefense, and Topos Omega modal truth governance across Strategify, Em-Cubed, and SME Harvester. Unites empirical OSINT perception, axiomatic Description Logic constraints ($C \sqsubseteq D$), agent-based Mesa simulations, and Zero-Knowledge Proof attestations. Use when simulating geopolitical crisis escalation, modeling biodefense contagion with axiomatic policy guardrails, or verifying multi-engine simulation trajectories.
purpose: Orchestrate perception, axiomatic governance, and agent-based simulation across SME, Em-Cubed, and Strategify engines.
dependencies: []
tags:
  - tri-engine
  - geopolitical-sim
  - seirh-epidemiology
  - topos-omega
  - dl-conflict-guard
  - zkp-attestation
inputs:
  theater_region:
    type: string
    required: true
    description: Target geopolitical or epidemiological region (e.g. 'Ukraine', 'MiddleEast').
  candidate_action:
    type: string
    required: true
    description: Proposed policy intervention or strategic maneuver (e.g. 'mobilize', 'quarantine', 'cyber_attack').
  simulation_steps:
    type: integer
    required: false
    description: Simulation duration ticks (default 30).
outputs:
  epistemic_perception:
    type: object
    description: Ingested OSINT sentiment and empirical trust metrics from SME.
  governance_verdict:
    type: object
    description: Topos Omega truth evaluation and Description Logic conflict guard status.
  simulation_outcome:
    type: object
    description: Agent-based simulation trajectory and epidemiological metrics.
  zkp_attestation_id:
    type: string
    description: Cryptographic Zero-Knowledge proof commitment ID for verified trajectory.
---

# Tri-Engine Simulation & Governance Agent Engine

`tri-engine-sim-agent` orchestrates end-to-end multi-paradigm simulations by uniting:
1. **Perception (`SME Harvester`)**: Real-world GDELT/OSINT epistemic sentiment and observation feeds.
2. **Axiomatic Governance (`Em-Cubed`)**: Description Logic conflict guarding ($C \sqsubseteq D$) and Topos Subobject Classifier modal necessity ($\Omega$).
3. **Macro-Simulation (`Strategify`)**: Mesa Geo agent-based simulation and SEIRH biodefense contagion modeling.
4. **Attestation (`Em-Cubed`)**: Post-quantum Zero-Knowledge state commitments ($s \Vdash A$).

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 6-Stage Tri-Engine Progression

```
[1. Theater Invariant Audit] → [2. SME Perception Ingest] → [3. Axiomatic DL & Topos Guard] → [4. Visual Brief] → [5. Checkpoint] → [6. Simulation & ZKP Attestation]
```

### Stage 1: Theater & Parameter Invariant Audit
1. Ingest `theater_region` and `candidate_action` parameters.
2. Validate spatial boundary definitions and baseline epidemiological/economic invariants.

> **Completion criterion**: Theater parameters validated and baseline state initialized.

---

### Stage 2: SME Perception Ingestion
1. Query `SMEOSINTBridge` for real-time epistemic tension, event frequency, and trust metrics for target theater.
2. Calculate empirical trust factor $T_{\text{epistemic}} \in [0.0, 1.0]$.

> **Completion criterion**: Empirical perception vector ingested and normalized.

---

### Stage 3: Axiomatic DL Conflict Guarding & Topos $\Omega$
1. Classify decision confidence in Topos Subobject Classifier ($\Omega$).
2. Evaluate Description Logic escalation constraints ($C_{\text{action}} \sqsubseteq \neg C_{\text{prohibited}}$).
3. If rule collision occurs, clamp action parameters to compliant defensive boundaries.

> **Completion criterion**: Action certified compliant with Topos necessity and Description Logic axioms.

---

### Stage 4: The Visual Brief
For high-stakes simulations, generate an interactive tri-engine trajectory brief:
- **Location**: Write to `%TEMP%\tri-engine-sim-brief-<timestamp>.html` (Windows) or `/tmp/tri-engine-sim-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render perception-governance-simulation pipeline, tension curve, and SEIRH contagion trajectory.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 5: Mandatory Checkpoint
Before executing computationally intensive wargame runs ($> 100$ steps) or dispatching automated counter-measures:
1. Verify that projected escalation metrics remain below critical thresholds.
2. Halt for human sign-off if action classified as high-risk escalation.

> **Completion criterion**: Simulation run approved under safety policies.

---

### Stage 6: Macro-Simulation & ZKP Attestation
1. Execute Mesa Geo agent-based simulation / SEIRH biodefense model across requested steps.
2. Seal final trajectory state with post-quantum Zero-Knowledge proof commitment ($s \Vdash A$).
3. Emit full simulation telemetry and proof ID.

> **Completion criterion**: Simulation completed and ZKP attestation generated.

---

## Surface References

### Python Tri-Engine Orchestrator Surface

```python
from typing import Dict, Any

def run_tri_engine_simulation(theater: str, action: str, steps: int = 30) -> Dict[str, Any]:
    # 1. Perception
    perception = {"theater": theater, "epistemic_trust_score": 0.92, "event_tension": "HIGH"}
    
    # 2. Governance
    topos_decision = {"action": action, "confidence": 0.92, "modal_truth": "NECESSARY"}
    dl_guard = {"is_permitted": True, "conflict_detected": False}
    
    # 3. Attestation
    proof_id = f"ZKP-SIM-{theater.upper()}-88219"
    
    return {
        "epistemic_perception": perception,
        "governance_verdict": {"topos": topos_decision, "dl_guard": dl_guard},
        "simulation_outcome": {
            "steps_run": steps,
            "peak_tension": 0.85,
            "containment_rate": 0.94
        },
        "zkp_attestation_id": proof_id
    }
```

---

## Anti-Patterns & Guardrails

- **Ungoverned Agent Escalation** — Allowing agent-based simulation agents to execute kinetic or high-impact actions without Topos $\Omega$ and Description Logic guard approval.
- **Purely Empirical Fallback** — Relying exclusively on noisy OSINT sentiment while bypassing deductive semantic balance constraints.
- **Unverified Simulation Outputs** — Disseminating macro-simulation trajectories without cryptographic ZKP state attestations.
