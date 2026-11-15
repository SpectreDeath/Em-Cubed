# Skill Summary Card: `truthmaker-hyperintensional-verifier`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        truthmaker-hyperintensional-verifier      │
│ Category:    ONTOLOGY / Hyperintensional Semantics     │
│ Invocation:  /truthmaker-hyperintensional-verifier     │
│ Trigger:     "truthmaker verify", "exact grounding",   │
│              "kit fine semantics", "wholly relevant"   │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Extract exact truthmaker states (s ⊩ A)   │
│              and evaluate hyperintensional grounding   │
│              while pruning irrelevant context noise.   │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Parse proposition and index candidate triples | Indexed Graph Store | Triples mapped into subject-predicate indices |
| **2. Datalog Slicing** | Extract candidate minimal support subgraph | Sliced Subgraph AST | All unreferenced ambient triples discarded |
| **3. Visual Brief** | Render full state vs exact truthmaker subgraph | `%TEMP%\truthmaker-verifier-brief-*.html` | Dark theme HTML comparison brief |
| **4. Checkpoint** | Validate bilateral consistency and falsemakers | Consistency Check | Confirmed $s \cap \text{Falsemakers}(A) = \emptyset$ |
| **5. Bilateral Eval** | Verify exactness ($s \Vdash A$) and emit | Grounding Payload | `is_satisfied: true` with minimal triple list |

---

## Invariants & Guardrails

- [ ] **Exact Relevance**: No triple permitted in the truthmaker set unless its removal invalidates satisfaction.
- [ ] **Hyperintensional Distinctions**: Propositions with identical truth-values across possible worlds are distinguished if their subject-matters diverge.
- [ ] **Zero Falsemaker Overlap**: The truthmaker state must not contain an exact falsemaker for the target assertion.
