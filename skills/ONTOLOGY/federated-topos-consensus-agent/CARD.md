# Skill Summary Card: `federated-topos-consensus-agent`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        federated-topos-consensus-agent           │
│ Category:    ONTOLOGY / Multi-Agent Consensus          │
│ Invocation:  /federated-topos-consensus-agent          │
│ Trigger:     "federated consensus", "topos meet",      │
│              "multi-agent agreement", "sync registry"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Evaluate Heyting algebra meet consensus   │
│              and synchronize federated ontology state  │
│              hashes across distributed agents.         │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Ingest and normalize agent truth payloads | Normalized Payload List | All confidence scores bounded in $[0, 1]$ |
| **2. Heyting Meet** | Compute categorical $\Omega$ meet ($\bigwedge_i \Omega_i$) | Meet Truth Object | Composite confidence & modal type computed |
| **3. Visual Brief** | Render multi-agent consensus graph | `%TEMP%\federated-consensus-brief-*.html` | Dark theme HTML consensus brief |
| **4. Checkpoint** | Validate consensus thresholds & dissenters | Consensus Status | Threshold checked without unhandled vetoes |
| **5. State Sync** | Calculate SHA-256 state hash & sync nodes | Checksum Record | Identical SHA-256 committed across swarm |

---

## Invariants & Guardrails

- [ ] **Heyting Meet Invariant**: $\Omega_{\text{consensus}} = \min_i(\Omega_i)$.
- [ ] **Modal Unanimity**: Invariant requires all voting agents to report `Necessary` for global necessity.
- [ ] **Cryptographic Sync**: Swarm alignment verified via SHA-256 state checksum.
