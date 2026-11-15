# Skill Summary Card: `ontological-os-cli-suite`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        ontological-os-cli-suite                  │
│ Category:    ONTOLOGY / Terminal CLI Management        │
│ Invocation:  /ontological-os-cli-suite                 │
│ Trigger:     "em3 cli", "run ontology command",        │
│              "terminal ontology suite", "em3 validate" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Unified terminal CLI suite (em3 ontology) │
│              for validation, elicitation, truthmakers, │
│              visualization, and schema migrations.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate CLI subcommand & flag arguments | Parsed CLI Args AST | Arguments conform to command spec |
| **2. Dispatch** | Map to underlying engine controller | Target Engine Route | Target engine initialized |
| **3. Visual Brief** | Render CLI pipeline & stdout stream | `%TEMP%\cli-suite-brief-*.html`| Dark theme HTML CLI brief |
| **4. Checkpoint** | Gate mutating commands or require `--confirm`| Safety Gate Record | Gated verification on live mutations |
| **5. Execution & Exit**| Run engine & emit ANSI stdout with exit code | Formatted CLI Output | Clean exit code (0 on success) emitted |

---

## Invariants & Guardrails

- [ ] **Standard Exit Codes**: `0` on success, `1` on validation violation, `2` on syntax error.
- [ ] **Dry-Run Safety**: Destructive mutations require explicit confirmation flags.
- [ ] **Structured Telemetry**: Output formatted cleanly for both human terminals and machine pipes.
