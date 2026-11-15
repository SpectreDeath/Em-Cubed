# Skill Summary Card: `distributive-lattice-validator`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        distributive-lattice-validator            │
│ Category:    LOGIC / Distributive Lattice Theory       │
│ Invocation:  /distributive-lattice-validator           │
│ Trigger:     "validate distributive lattice",          │
│              "compute lub glb", "check n5 m3",         │
│              "lattice distributivity proof"            │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Verify unique pairwise joins/meets in     │
│              Prolog and mathematically prove algebraic │
│              distributivity axioms using Z3 SMT.       │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate poset facts & extract element set $\mathcal{E}$ | Certified Poset Spec | Input relation confirmed as valid poset |
| **2. Join & Meet Map**| Compute unique LUB and GLB for all pairs | Join & Meet Tables | Single-valued LUB/GLB for all $N^2$ pairs |
| **3. Visual Brief** | Render lattice Hasse graph & sublattice check | `%TEMP%\lattice-validator-brief-*.html`| Dark theme HTML lattice brief |
| **4. Checkpoint** | Detect forbidden $N_5$ (pentagon) / $M_3$ (diamond) | Sublattice Obstruction Map| Zero $N_5$ or $M_3$ sublattices present |
| **5. Z3 Distributivity**| Assert $x \land (y \lor z) = (x \land y) \lor (x \land z)$ | Distributivity Verdict | Axioms satisfied for all $N^3$ triplets |

---

## Invariants & Guardrails

- [ ] **Lattice Completeness**: Every pair $(x, y)$ must have a unique LUB ($\lor$) and GLB ($\land$).
- [ ] **Dual Distributivity**: Both $x \land (y \lor z) = (x \land y) \lor (x \land z)$ and $x \lor (y \land z) = (x \lor y) \land (x \lor z)$ must hold.
- [ ] **Sublattice Invariant**: Lattice must contain no isomorphic sublattices to $N_5$ or $M_3$.
