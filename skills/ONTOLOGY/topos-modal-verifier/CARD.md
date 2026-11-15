# Skill Summary Card: `topos-modal-verifier`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        topos-modal-verifier                      │
│ Category:    ONTOLOGY / Categorical Logic & Modal SMT  │
│ Invocation:  /topos-modal-verifier                     │
│ Trigger:     "topos verify", "subobject classifier",   │
│              "modal necessity", "heyting truth omega"  │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Evaluate categorical truth object Omega,  │
│              structure-preserving surface morphisms,   │
│              and modal necessity across Kripke frames. │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate assertion AST & accessible world frames | Kripke Frame Spec | Relational frame satisfies accessibility rules |
| **2. Morphism Mapping** | Map structure across Python, Prolog, and Z3 | Functor Mapping Object | Commutative diagrams verified across surfaces |
| **3. Visual Brief** | Render Kripke graph & Heyting truth lattice | `%TEMP%\topos-verifier-brief-*.html` | Dark theme HTML lattice report |
| **4. Checkpoint** | Check counter-models and world coverage | Branch Exhaustion Map | All counter-model branches searched in Z3 |
| **5. SMT & Proof** | Compute Omega truth $\chi_P$ & modal category | Omega Truth Object | Valuation returned with confidence and status |

---

## Invariants & Guardrails

- [ ] **Heyting Algebra Bounds**: All truth values in $\Omega$ bounded in $[0.0, 1.0]$.
- [ ] **Morphism Preservation**: Mappings between surfaces must preserve identity and composition.
- [ ] **Kripke Frame Consistency**: Accessibility relations must adhere to defined modal axioms (e.g. S4 / S5).
