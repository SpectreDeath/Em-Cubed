# Skill Summary Card: `ontological-os-tui-dashboard`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        ontological-os-tui-dashboard              │
│ Category:    ONTOLOGY / Terminal User Interface (TUI)  │
│ Invocation:  /ontological-os-tui-dashboard             │
│ Trigger:     "open tui dashboard", "terminal workspace",│
│              "view ontology status", "topos gauge"     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Live interactive terminal dashboard       │
│              rendering triple ledgers, Topos gauges,   │
│              health metrics, and ZKP proof status.     │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Ingest and validate multi-engine telemetry | Normalized Telemetry AST | All metrics bounded in range |
| **2. Layout Compilation**| Compile 5-panel layout into display buffer | Display Buffer AST | Panels sized and formatted cleanly |
| **3. Visual Brief** | Render terminal UI preview & component DAG | `%TEMP%\tui-dashboard-brief-*.html`| Dark theme HTML dashboard brief |
| **4. Checkpoint** | Validate ANSI TTY capabilities & screen size | Terminal Capability Record | TTY verified or static fallback ready |
| **5. Render & Emit** | Draw ANSI dashboard frame & emit snapshot | Rendered Frame String | Dashboard displayed with zero tearing |

---

## Invariants & Guardrails

- [ ] **TTY Detection**: Automatically fallback to static snapshot when `isatty() == false`.
- [ ] **Panel Bounds**: Graceful truncation when terminal dimensions are below $80 \times 24$.
- [ ] **Zero-Tearing Buffer**: Double-buffered string rendering to prevent flicker.
