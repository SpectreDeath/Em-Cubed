# Skill Summary Card: `calculate_central_tendency`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        calculate_central_tendency                │
│ Category:    STATISTICS / Descriptive Location         │
│ Invocation:  /calculate_central_tendency               │
│ Trigger:     "calculate mean median mode",             │
│              "central tendency", "sample average"      │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute mean, parity-corrected median,    │
│              multimodal mode, and sample counts from   │
│              sanitized numeric vectors.                │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Sanitization** | Filter NaN/Null & validate non-empty vector | Clean Numeric Vector | $N \ge 1$ after cleaning |
| **2. Sorted Setup** | Sort array & build element frequency counter | Sorted Array & Counts | Ascending sorted vector indexed |
| **3. Visual Brief** | Render distribution histogram with mean/median | `%TEMP%\central-tendency-brief-*.html`| Dark theme HTML distribution brief |
| **4. Checkpoint** | Validate skewness and potential bimodality | Skewness Diagnostic Record| Skewness evaluated against threshold |
| **5. Metric Emit** | Calculate mean, median, mode & emit results | `CentralTendencyResult` | Clean metrics record emitted |

---

## Invariants & Guardrails

- [ ] **Empty Vector Guard**: Explicitly error if $N = 0$ after dropping non-numeric values.
- [ ] **Parity Correction**: Even-length median computed as $(x_{n/2} + x_{n/2 + 1}) / 2$.
- [ ] **Multimodal Awareness**: List all tied modes if `multimodal == true`.
