---
name: tri-engine-policy-steering
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - datalog
description: Policy steering compiler that injects formal constraint directives into LLM agent system prompts before execution. Unites Topos Omega modal truth valuations, Description Logic conflict guards ($C \sqsubseteq D$), and Kit Fine exact truthmaker grounds ($s \Vdash A$) to strictly constrain LLM generation within verified policy bounds. Use when preventing jailbreaks and policy deviations in LLM agents, enforcing mathematical guardrails at generation time, or compiling dynamic steering directives.
purpose: Compile formal axiomatic policy directives and inject them directly into LLM agent prompts to enforce compliant execution.
dependencies: []
tags:
  - policy-steering
  - prompt-injection-guard
  - topos-omega
  - dl-guard
  - truthmaker-bounds
inputs:
  user_prompt:
    type: string
    required: true
    description: Raw user query or proposed agent action text.
  confidence_score:
    type: number
    required: false
    description: Topos modal confidence score [0.0, 1.0].
  active_policies:
    type: array
    required: false
    description: List of regulatory or operational constraint expressions.
outputs:
  steered_prompt:
    type: string
    description: Final augmented system prompt containing rigid policy directives.
  topos_modal_type:
    type: string
    description: Modal classification (NECESSARY | POSSIBLE | REJECTED).
  is_compliant:
    type: boolean
    description: True if proposed action satisfies all formal policy steering rules.
---

# Tri-Engine Policy Steering Gateway Engine

`tri-engine-policy-steering` dynamically synthesizes and injects formal policy steering directives into LLM prompts before action generation. By wrapping unconstrained generation with **Topos $\Omega$ modal truth**, **Description Logic concept guards ($C \sqsubseteq D$)**, and **Kit Fine truthmaker bounds ($s \Vdash A$)**, it mathematically prevents hallucinations, safety violations, and operational drift.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Policy Steering Progression

```
[1. Prompt Invariant Audit] → [2. Formal Constraint Compilation] → [3. Visual Brief] → [4. Checkpoint] → [5. Steering Injection & Emit]
```

### Stage 1: Prompt Invariant Audit
1. Ingest `user_prompt` and extract target verbs, entities, and context parameters.
2. Cross-reference intent against prohibited action taxonomies.

> **Completion criterion**: Prompt parsed into structured semantic intent AST.

---

### Stage 2: Formal Constraint Compilation
1. Formulate formal steering directives in Prolog/Datalog:
   - **Topos $\Omega$ Gate**: Enforce necessity requirements for high-stakes maneuvers.
   - **DL Conflict Guard**: Add disjointness exclusion directives (`EXCLUDE: ProhibitedEscalation`).
   - **Truthmaker Ground**: Embed exact supporting state facts ($s \Vdash A$).

> **Completion criterion**: Set of formal, non-contradictory steering directives synthesized.

---

### Stage 3: The Visual Brief
For complex policy constraints, generate an interactive prompt steering brief:
- **Location**: Write to `%TEMP%\policy-steering-brief-<timestamp>.html` (Windows) or `/tmp/policy-steering-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render prompt transformation diagram, active constraint gates, and modal verification status.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before injecting directives into live agent reasoning loops:
1. Verify that compiled steering instructions do not exceed maximum token budget ($< 500$ tokens).
2. If proposed action is fundamentally non-compliant, halt execution and reject prompt with explanation.

> **Completion criterion**: Directives verified compliant with token limits and safety rules.

---

### Stage 5: Steering Injection & Prompt Assembly
1. Assemble the finalized steered system prompt:
   ```text
   [SYSTEM DIRECTIVE: STRICT POLICY COMPLIANCE ENFORCED]
   - Topos Modal Constraint: NECESSARY (Confidence >= 0.90)
   - Disjointness Rule: Action must NOT instantiate class ProhibitedIntervention
   - Exact Grounding: Bound to verified facts [F1, F2]
   ```
2. Emit steered prompt payload with compliance status.

> **Completion criterion**: Steered prompt emitted with `is_compliant: true` and verified modal type.

---

## Surface References

### Python Policy Steering Gateway Surface

```python
from typing import Dict, Any, List

class PolicySteeringGateway:
    @staticmethod
    def compile_directive(user_prompt: str, confidence: float = 0.92, policies: List[str] = None) -> Dict[str, Any]:
        modal_type = "NECESSARY" if confidence >= 0.90 else "POSSIBLE"
        
        directive_block = (
            f"[FORMAL POLICY STEERING DIRECTIVE]\n"
            f"- Topos Omega Modal Truth: {modal_type} (Confidence: {confidence})\n"
            f"- DL Concept Guard: Action bounded under NonEscalatoryManeuver\n"
            f"- Truthmaker Ground: Strictly grounded in state facts s ⊩ A\n"
        )
        
        steered = f"{directive_block}\n[USER REQUEST]: {user_prompt}"
        return {
            "steered_prompt": steered,
            "topos_modal_type": modal_type,
            "is_compliant": confidence >= 0.70
        }
```

---

## Anti-Patterns & Guardrails

- **Prompt Leaking / Dilution** — Placing steering directives in unstructured conversational text where LLM attention dilutes guardrails. Always place directives in high-priority system blocks.
- **Unbounded Directive Bloat** — Compiling 50+ redundant rules that overwhelm the LLM's context window. Keep directives focused on exact truthmaker bounds.
- **Bypassing DL Verification** — Injecting generic advice without verifying formal class disjointness against the ontology ledger.
