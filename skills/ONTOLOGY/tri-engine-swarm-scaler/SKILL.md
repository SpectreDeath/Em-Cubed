---
name: tri-engine-swarm-scaler
description: Dynamically balances agent worker allocations across SME perception ingestion, Em-Cubed Topos Ω modal verification, and Strategify Mesa Geo ABM simulation.
---

# Tri-Engine Swarm Capacity Scaler Skill (`tri-engine-swarm-scaler`)

This skill dynamically balances agent worker allocations across SME, Em-Cubed, and Strategify based on real-time Coherence Index (%) and Epistemic Trust score.

---

## 💻 Programmatic Usage Example

```python
from em_cubed.orchestration.swarm_scaler import SwarmCapacityScaler

# Calculate allocation for a 12-worker pool
report = SwarmCapacityScaler.calculate_allocation(
    total_workers=12,
    coherence_index=0.95,
    epistemic_trust=0.89,
)

print(f"Scaling Mode      : {report.scaling_mode}")
print(f"SME Workers       : {report.sme_workers}")
print(f"Em-Cubed Workers  : {report.em_cubed_workers}")
print(f"Strategify Workers: {report.strategify_workers}")
```
