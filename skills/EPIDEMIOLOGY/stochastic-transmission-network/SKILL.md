---
name: stochastic-transmission-network
domain: EPIDEMIOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - sqlite
description: Multi-surface stochastic transmission network model for epidemic spread simulation, contact tracing, and reproduction number estimation. Simulates agent network infections in Python, infers transmission chains and quarantine validity in Prolog, and records outbreak state in SQLite. Use when simulating disease propagation through contact graphs, evaluating non-pharmaceutical interventions, or tracing exposure chains.
purpose: Model disease transmission through stochastic contact networks, infer exposure chains via Prolog logic, and persist outbreak state in SQLite.
dependencies: []
tags:
  - epidemiology
  - stochastic-network
  - contact-tracing
  - r0-estimation
  - prolog-inference
  - sqlite-outbreak
inputs:
  population:
    type: integer
    required: true
    description: Total individual count in the simulation network.
  initial_infected:
    type: integer
    required: true
    description: Starting count of infected index cases.
  contact_rate:
    type: number
    required: true
    description: Mean daily contact interactions per individual.
  infection_prob:
    type: number
    required: true
    description: Probability of disease transmission per susceptible contact.
  days:
    type: integer
    required: true
    description: Total simulation duration in days.
outputs:
  daily_stats:
    type: object
    description: Daily counts of infected, recovered, and susceptible individuals.
  r0_estimate:
    type: number
    description: Estimated basic reproduction number R0.
  transmission_chains:
    type: array
    description: Inferred contact exposure chains from Prolog rules.
  outbreak_summary:
    type: object
    description: Cumulative infection and peak day summary.
---

# Stochastic Transmission Network Engine

`stochastic-transmission-network` coordinates epidemic spread modeling across three dedicated surfaces:
1. **Python Surface**: Simulates stochastic daily infection spread and SIR state transitions.
2. **Prolog Surface**: Evaluates relational exposure paths, transmission chains, and quarantine validity windows.
3. **SQLite Surface**: Persists contact events, exposure timelines, and outbreak telemetry.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 6-Stage Epidemic Simulation & Tracing Loop

Execute this sequence when configuring, simulating, and auditing network disease transmission:

```
[1. Topology & Invariants] → [2. Stochastic Propagation] → [3. Prolog Tracing] → [4. Visual Brief] → [5. Checkpoint] → [6. State Sync]
```

### Stage 1: Population & Parameter Invariant Audit
1. Validate population parameters: `population > 0`, `0 < initial_infected <= population`.
2. Validate transmission bounds: `0 <= infection_prob <= 1`, `contact_rate >= 0`, `days > 0`.
3. Compute expected baseline $R_0 = \text{contact\_rate} \times \text{infection\_prob}$.

> **Completion criterion**: Parameter bounds verified against epidemiological domain constraints.

---

### Stage 2: Stochastic Network Propagation (Python)
1. Initialize population state vectors ($S, I, R$) with uniform or graph-structured contact distributions.
2. Step through daily transmission rounds: sample contacts, compute transmission events, and apply recovery rates.
3. Track daily prevalence and cumulative attack rates.

> **Completion criterion**: Python simulation completes all `days` rounds returning continuous SIR trajectory arrays.

---

### Stage 3: Relational Contact Tracing & Quarantine Inference (Prolog)
1. Export observed contact pairs and infection events to Prolog knowledge base:
   - `contact(PersonA, PersonB).`
   - `infected(Person, Day).`
2. Query relational exposure chains: `transmission_chain(Infected, Day, Chain).`
3. Validate quarantine timing constraints: `valid_quarantine(Start, Onset, Period).`

> **Completion criterion**: Exposure chains evaluated and returned without unbound recursive loops.

---

### Stage 4: The Visual Brief
For all non-trivial outbreaks, generate an interactive epidemic curve and network topology brief:
- **Location**: Write to `%TEMP%\epidemic-transmission-brief-<timestamp>.html` (Windows) or `/tmp/epidemic-transmission-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the SIR epidemic curve, peak infection day, and transmission contact tree.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 5: Mandatory Checkpoint
Before committing large simulation runs to SQLite persistent storage:
1. Verify simulated $R_0$ stability against baseline predictions.
2. If total infected individuals exceed 80% of total population, pause and review intervention assumptions.

> **Completion criterion**: Outbreak metrics reviewed and verified consistent with model assumptions.

---

### Stage 6: SQLite Outbreak State Synchronization & Verification
1. Insert contact logs into `contacts` table.
2. Record infection events and $R_0$ estimates into `infection_events`.
3. Commit daily time-series counts to `transmission_stats`.

> **Completion criterion**: SQLite database tables updated atomically with consistent foreign key references.

---

## Surface References

### Python Surface

```python
import random
from typing import Dict, List

def simulate_transmission(
    population: int, 
    initial_infected: int, 
    contact_rate: float, 
    infection_prob: float, 
    days: int
) -> Dict[str, List[int]]:
    """Simulate epidemic transmission through population network."""
    infected = set(random.sample(range(population), min(initial_infected, population)))
    recovered = set()
    daily_stats = {"infected": [], "recovered": [], "susceptible": []}
    
    for _ in range(days):
        new_infected = set()
        for _ in infected:
            contacts = int(random.gauss(contact_rate, 2))
            for _ in range(max(0, contacts)):
                contact = random.randint(0, population - 1)
                if contact not in infected and contact not in recovered:
                    if random.random() < infection_prob:
                        new_infected.add(contact)
        
        infected.update(new_infected)
        recovery = {inf for inf in list(infected) if random.random() < 0.1}
        recovered.update(recovery)
        infected -= recovery
        
        daily_stats["infected"].append(len(infected))
        daily_stats["recovered"].append(len(recovered))
        daily_stats["susceptible"].append(population - len(infected) - len(recovered))
    
    return daily_stats

def compute_r0(contact_rate: float, infection_prob: float) -> float:
    """Compute basic reproduction number R0."""
    return contact_rate * infection_prob
```

### Prolog Contact Tracing Surface

```prolog
% Relational Contact Tracing Rules
exposed(Person, Day) :-
    infected(Contact, DayPrev),
    contact(Contact, Person),
    Day is DayPrev + 1.

transmission_chain(Infected, Day, Chain) :-
    findall(Contact, (exposed(Infected, D, Contact), D =< Day), Chain).

valid_quarantine(QuarantineStart, SymptomOnset, InfectiousPeriod) :-
    QuarantineStart =< SymptomOnset,
    QuarantineStart + InfectiousPeriod >= SymptomOnset.
```

### SQLite Persistence Schema

```sql
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_a INTEGER NOT NULL,
    person_b INTEGER NOT NULL,
    contact_date TEXT NOT NULL,
    location TEXT
);

CREATE TABLE IF NOT EXISTS infection_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    infector INTEGER,
    infected INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    r0_estimate REAL
);

CREATE TABLE IF NOT EXISTS transmission_stats (
    day INTEGER PRIMARY KEY,
    infected_count INTEGER NOT NULL,
    recovered_count INTEGER NOT NULL,
    susceptible_count INTEGER NOT NULL
);
```

---

## Capability Contract

### Inputs
- `population` *(integer, required)* — Network size.
- `initial_infected` *(integer, required)* — Initial case count.
- `contact_rate` *(number, required)* — Mean daily contacts per node.
- `infection_prob` *(number, required)* — Transmission likelihood per contact.
- `days` *(integer, required)* — Simulation time horizon.

### Outputs
- `daily_stats` *(object)* — SIR time-series arrays.
- `r0_estimate` *(number)* — Basic reproduction number $R_0$.
- `transmission_chains` *(array)* — Prolog-inferred contact paths.
- `outbreak_summary` *(object)* — Peak active infections and total attack rate.

---

## Anti-Patterns & Guardrails

- **Disconnected Contact Graphs** — Generating transmission networks with isolated subgraphs that prevent epidemic spread regardless of $R_0$.
- **Infinite Prolog Tracing Cycles** — Formulating cyclic contact rules (`contact(A, B) :- contact(B, A)`) without cycle detection or day bounding, leading to Prolog recursion depth errors.
- **Desynchronized Outbreak Logs** — Storing simulation metrics in memory without committing daily state records to SQLite `transmission_stats`.
- **Negative Population Counts** — Miscalculating recoveries such that $S + I + R \neq \text{population}$. Invariant $S + I + R = N$ must hold at all time ticks.
