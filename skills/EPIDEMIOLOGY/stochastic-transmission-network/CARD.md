# Skill Summary Card: `stochastic-transmission-network`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        stochastic-transmission-network           │
│ Category:    EPIDEMIOLOGY / Network Modeling           │
│ Invocation:  /stochastic-transmission-network          │
│ Trigger:     "simulate epidemic", "contact tracing",   │
│              "estimate r0", "transmission network"     │
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Simulate epidemic spread in Python, infer │
│              chains in Prolog, and persist in SQLite.  │
└────────────────────────────────────────────────────────┘
```

---

## The 6-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Invariant Audit** | Validate population and transmission parameters | Configuration Record | Parameter bounds satisfy biological domain |
| **2. Python Propagation** | Execute stochastic network transmission | `daily_stats` Object | Continuous daily SIR arrays generated |
| **3. Prolog Tracing** | Infer exposure chains and quarantine bounds | `transmission_chains` Array | Relational exposure chains returned |
| **4. Visual Brief** | Render epidemic curves and transmission tree | `%TEMP%\epidemic-transmission-brief-*.html` | Dark theme HTML curve report generated |
| **5. Outbreak Checkpoint** | Validate $R_0$ stability and attack rates | Checkpoint Summary | Trajectory verified against expected $R_0$ |
| **6. SQLite Persistence** | Atomically commit contacts and events | SQLite Database Rows | Transaction committed across all tables |

---

## Multi-Surface Cheat Sheet

### Python Simulation
```python
stats = simulate_transmission(
    population=1000, 
    initial_infected=5, 
    contact_rate=3.5, 
    infection_prob=0.2, 
    days=60
)
```

### Prolog Contact Inference
```prolog
% Query transmission chain for patient 42 on day 10
?- transmission_chain(42, 10, Chain).
```

### SQLite Schema
- `contacts`: `id (PK)`, `person_a`, `person_b`, `contact_date`, `location`
- `infection_events`: `id (PK)`, `infector`, `infected`, `timestamp`, `r0_estimate`
- `transmission_stats`: `day (PK)`, `infected_count`, `recovered_count`, `susceptible_count`

---

## Invariants & Guardrails

- [ ] **Population Conservation**: $S(t) + I(t) + R(t) = N$ for every simulated day $t$.
- [ ] **Acyclic Tracing Constraints**: Prolog tracing queries enforce depth limits ($D \le \text{Day}$).
- [ ] **Finite $R_0$ Range**: $R_0 = \text{contact\_rate} \times \text{infection\_prob} \ge 0$.
- [ ] **Relational Foreign Key Integrity**: Every infection record in SQLite maps to a valid person.
