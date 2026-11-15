# Skill Summary Card: `tri-engine-policy-steering`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        tri-engine-policy-steering                │
│ Category:    ONTOLOGY / Policy Steering & Prompts      │
│ Invocation:  /tri-engine-policy-steering               │
│ Trigger:     "steer agent prompt", "compile policy",   │
│              "inject topos guardrails", "dl constraint"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Dynamically compile and inject formal     │
│              Topos, DL, and Truthmaker policy rules    │
│              directly into LLM agent system prompts.   │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Parse prompt intent & extract target actions | Parsed Intent AST | Core intent and parameters isolated |
| **2. Compilation** | Synthesize Topos, DL & Truthmaker constraints| Steering Directives | Formal rules compiled in Prolog/Datalog |
| **3. Visual Brief** | Render prompt transformation and guard gates | `%TEMP%\policy-steering-brief-*.html`| Dark theme HTML steering brief |
| **4. Checkpoint** | Validate token budget and policy compliance | Safety Gate Record | Directives within token limits ($\le 500$) |
| **5. Assembly & Emit** | Assemble steered system prompt and return | Final Steered Prompt | Steered prompt emitted with `is_compliant` |

---

## Invariants & Guardrails

- [ ] **System Block Placement**: Directives must be injected into high-priority system prompt envelopes.
- [ ] **Token Budget Constraint**: Steering blocks must not exceed 500 tokens.
- [ ] **Modal Consistency**: Actions marked `NECESSARY` must carry confidence $\ge 0.90$.
