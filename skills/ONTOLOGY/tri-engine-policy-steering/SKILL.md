---
name: tri-engine-policy-steering
description: Dynamically compiles and injects formal policy steering directives into LLM agents before action execution based on real-time Topos Ω modal truth, DL guards, and truthmakers.
---

# Tri-Engine Autonomous Agent Policy Steering Skill (`tri-engine-policy-steering`)

This skill compiles formal policy steering directives combining Topos $\Omega$ modal truth, Description Logic guards ($C \sqsubseteq D$), and Kit Fine truthmaker grounds ($s \Vdash A$) to steer LLM agent prompts before execution.

---

## 💻 Programmatic Usage Example

```python
from em_cubed.gateway.policy_steering import AutonomousPolicySteeringGateway

# Compile steering directive for candidate action
payload = AutonomousPolicySteeringGateway.compile_steering_directive(
    user_prompt="Mobilize peacekeeping forces along border",
    confidence_score=0.92,
)

print(f"Topos Ω Status: {payload.topos_modal_type}")
print(f"Compliant     : {payload.is_compliant}")
print("\nSteered System Prompt:\n", payload.steered_prompt)
```
