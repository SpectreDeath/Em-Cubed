# Skill Summary Card: `poset-implication-builder`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        poset-implication-builder                 │
│ Category:    LOGIC / Partially Ordered Sets (Poset)    │
│ Invocation:  /poset-implication-builder                │
│ Trigger:     "build poset", "implication order",       │
│              "transitive closure", "verify poset z3"   │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Construct partially ordered sets from     │
│              propositions under logical implication    │
│              and prove poset axioms via Z3 SMT.        │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate proposition set and edge references | Proposition Dictionary | Zero dangling references |
| **2. Transitive Closure**| Compute transitive reachability & extrema in Prolog | Transitive Implication Map| Transitive closure generated |
| **3. Visual Brief** | Render Hasse diagram & transitive reduction | `%TEMP%\poset-builder-brief-*.html`| Dark theme HTML Hasse diagram brief |
| **4. Checkpoint** | Validate acyclicity & collapse cyclic equivalences | DAG Verification Record | Implication graph verified acyclic |
| **5. Z3 Poset Proof** | Verify reflexivity, antisymmetry, and transitivity | Verified Poset Facts | Z3 solver returns `sat` |

---

## Invariants & Guardrails

- [ ] **Reflexivity**: $P \implies P$ for every proposition $P$.
- [ ] **Antisymmetry**: $P \implies Q \land Q \implies P \implies P = Q$.
- [ ] **Transitivity**: $P \implies Q \land Q \implies R \implies P \implies R$.
- [ ] **Unique Extrema**: Identify well-defined $\top$ and $\bot$ elements when bounded.
