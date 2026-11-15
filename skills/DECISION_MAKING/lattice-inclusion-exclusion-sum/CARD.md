# Skill Summary Card: `lattice-inclusion-exclusion-sum`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        lattice-inclusion-exclusion-sum           │
│ Category:    DECISION_MAKING / Lattice Inclusion       │
│ Invocation:  /lattice-inclusion-exclusion-sum          │
│ Trigger:     "lattice inclusion exclusion sum",        │
│              "general sum rule", "disjunctive lattice",│
│              "meet join probability", "union prob"     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Compute lattice-native inclusion-exclusion│
│              disjunctive sums with structural meet/join│
│              resolution in Prolog & Fréchet bounds.    │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Ingestion** | Ingest distribution map & target proposition pair | Proposition Universe AST | $k \ge 2$ targets verified |
| **2. Prolog Meet** | Resolve algebraic meet element in Prolog | Structural Meet Atom | Meet element resolved |
| **3. Visual Brief** | Render Hasse lattice diagram & term breakdown | `%TEMP%\lattice-sum-brief-*.html`| Dark theme HTML sum brief |
| **4. Checkpoint** | Validate Fréchet bounds ($P(A \land B) \le \min(P(A), P(B))$)| Fréchet Invariant Record| Bound constraints passed |
| **5. Model Emission** | Compute $P(A \lor B \mid C)$ & emit decomposition | `LatticeSumResult` Payload | Full sum payload emitted |

---

## Invariants & Guardrails

- [ ] **Fréchet Bounds Invariant**: $P(A \land B) \le \min(P(A), P(B))$.
- [ ] **Probability Range**: $0.0 \le P(A \lor B \mid C) \le 1.0$.
- [ ] **Structural Meet Alignment**: Meet operation matches greatest lower bound in poset.
