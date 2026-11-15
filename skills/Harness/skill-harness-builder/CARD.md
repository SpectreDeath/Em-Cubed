# Skill Summary Card: `skill-harness-builder`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-harness-builder                     │
│ Category:    Harness / Sandboxing                      │
│ Invocation:  /skill-harness-builder                    │
│ Trigger:     "build harness", "compile skill harness", │
│              "sandbox tool mapping", "workspace state" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compile declarative SKILL.md blueprints   │
│              into isolated, sandboxed execution        │
│              harnesses with SQLite session state.      │
└────────────────────────────────────────────────────────┘
```

---

## The 6-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Audit & Parse** | Validate frontmatter and required invariants | AST Definition Object | Zero syntax/schema validation errors |
| **2. Scope Formulation** | Construct least-privilege tool permission map | `tool_map` Object | All tools assigned explicit scopes |
| **3. Visual Brief** | Render dependency and permission graph | `%TEMP%\harness-build-brief-*.html` | Dark theme HTML generated with Mermaid |
| **4. Checkpoint** | Validate sandbox permissions and boundaries | `implementation_plan.md` | Gated verification on breaking mutations |
| **5. Compile & Lock** | Emit manifest and persist SQLite state | `harness_manifest` & SQLite row | Atomic transaction in `harness_workspaces` |
| **6. Smoke Test** | Verify sandbox isolation and confinement | `readiness_status: ready` | Confinement probe passes without leakage |

---

## Quick Reference

### Python Surface Invocation
```python
from em_cubed.skills.harness_builder import build_harness

harness = build_harness(
    skill_definition=parsed_skill,
    tool_schema=tools,
    workspace_mode="shared",
    sandbox_policy={"max_memory_mb": 512, "network": False},
)
```

### SQLite Schema Summary
- `harness_workspaces`: `workspace_id (PK)`, `skill_name`, `domain`, `tool_map`, `sandbox_policy`, `state_hash`, `created_at`
- `harness_events`: `event_id (PK)`, `workspace_id (FK)`, `event_type`, `payload`, `timestamp`

---

## Invariants & Anti-Patterns Checklist

- [ ] **Least-Privilege Tool Scopes**: No tool exposed without explicit capability masks (`read`, `write`, `exec`).
- [ ] **Deterministic State Hashes**: Every workspace mutation recorded in `harness_events` and committed to `harness_workspaces`.
- [ ] **Fail-Closed Sandbox**: Any boundary breach or scope violation triggers `sandbox_locked` or `build_failed`.
- [ ] **No Silent Fallbacks**: Build failures halt immediately and report actionable error diagnostics.
