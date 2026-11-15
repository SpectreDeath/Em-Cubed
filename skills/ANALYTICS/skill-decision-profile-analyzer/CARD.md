# Skill Summary Card: `skill-decision-profile-analyzer`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        skill-decision-profile-analyzer           │
│ Category:    ANALYTICS / Solver Behavioral Profiling   │
│ Invocation:  /skill-decision-profile-analyzer          │
│ Trigger:     "analyze decision profile", "prune ratio",│
│              "solver personality", "elimination trace" │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute hard-pruning vs probabilistic-    │
│              decay ratios from SQLite traces and assert│
│              queryable Prolog solver_profile facts.    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Trace Ingest** | Query SQLite elimination traces by session | Trace Step Records | Step count $N_{\text{total}} \ge 1$ |
| **2. Ratio Calculation**| Compute prune ratio and bias direction | Profile Calculation AST | $\text{prune\_ratio} \in [0.0, 1.0]$ |
| **3. Visual Brief** | Render solver personality radar and bias chart| `%TEMP%\decision-profile-brief-*.html`| Dark theme HTML profile brief |
| **4. Checkpoint** | Validate minimum step count for confidence | Statistical Gate Record | Sample size sufficient ($N \ge 3$) |
| **5. Prolog Assert** | Assert `solver_profile/3` fact and close session| Final Profile Payload | Fact asserted in Prolog and session closed |

---

## Invariants & Guardrails

- [ ] **Step Count Conservation**: $N_{\text{hard}} + N_{\text{decay}} = N_{\text{total}}$.
- [ ] **Dynamic Fact Cleanliness**: Retract stale profile facts before asserting new session facts.
- [ ] **Confidence Scaling**: Confidence strictly scaled by sample depth.
