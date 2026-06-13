---
name: stochastic-transmission-network
Domain: EPIDEMIOLOGY
Version: 1.0.0
surfaces:
  - python
  - prolog
  - sqlite
description: Multi-surface stochastic transmission network with Python surface for graph-based infection simulation, Prolog surface for epidemiological rule inference, and SQLite surface for contact tracing and state persistence.
compatibility: PYTHON
allowed-tools: |
  - read
  - write
  - edit
  - bash
  - glob
  - grep
  - codebase_search
  - task
  - sequentialthinking_sequentialthinking
  - webfetch
  - websearch
  - question
  - suggest
---

## Purpose

Stochastic transmission network model for epidemic spread simulation using contact tracing and probability-based infection propagation.

## Description

Models disease transmission through a network of individuals with configurable infection probabilities, recovery rates, and contact patterns.

## Implementation

### Python Transmission Simulation

```python
import random
from typing import Dict, List

def simulate_transmission(population: int, initial_infected: int, 
                        contact_rate: float, infection_prob: float,
                        days: int) -> Dict[str, List[int]]:
    """Simulate epidemic transmission through population network."""
    infected = set(random.sample(range(population), min(initial_infected, population)))
    recovered = set()
    daily_stats = {"infected": [], "recovered": [], "susceptible": []}
    
    for day in range(days):
        new_infected = set()
        for inf in infected:
            contacts = int(random.gauss(contact_rate, 2))
            for _ in range(max(0, contacts)):
                contact = random.randint(0, population - 1)
                if contact not in infected and contact not in recovered:
                    if random.random() < infection_prob:
                        new_infected.add(contact)
        
        infected.update(new_infected)
        recovery = set()
        for inf in list(infected):
            if random.random() < 0.1:
                recovery.add(inf)
        recovered.update(recovery)
        infected -= recovery
        
        daily_stats["infected"].append(len(infected))
        daily_stats["recovered"].append(len(recovered))
        daily_stats["susceptible"].append(population - len(infected) - len(recovered))
    
    return daily_stats

def compute_r0(total_infected: int, total_population: int, 
               contact_rate: float, infection_prob: float) -> float:
    """Compute basic reproduction number R0."""
    return contact_rate * infection_prob
```

### Prolog Contact Tracing Logic

```prolog
% Contact tracing rules
exposed(Person, Day) :-
    infected(Contact, DayPrev),
    contact(Contact, Person),
    Day is DayPrev + 1.

% Transmission chain tracking
transmission_chain(Infected, Day, Chain) :-
    findall(Contact, (exposed(Infected, D, Contact), D =< Day), Chain).

% Quarantine constraint
valid_quarantine(QuarantineStart, SymptomOnset, InfectiousPeriod) :-
    QuarantineStart =< SymptomOnset,
    QuarantineStart + InfectiousPeriod >= SymptomOnset.
```

### SQLite Schema for Outbreak Tracking

```sql
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY,
    person_a INTEGER,
    person_b INTEGER,
    contact_date TEXT,
    location TEXT
);

CREATE TABLE IF NOT EXISTS infection_events (
    id INTEGER PRIMARY KEY,
    infector INTEGER,
    infected INTEGER,
    timestamp INTEGER,
    r0_estimate REAL
);

CREATE TABLE IF NOT EXISTS transmission_stats (
    day INTEGER PRIMARY KEY,
    infected_count INTEGER,
    recovered_count INTEGER,
    susceptible_count INTEGER
);
```

## Testing

```python
import pytest

def test_simulation():
    stats = simulate_transmission(100, 5, 3.0, 0.3, 30)
    assert len(stats["infected"]) == 30
    assert sum(stats["infected"]) > 0

def test_r0():
    r0 = compute_r0(100, 1000, 2.5, 0.2)
    assert 0.0 < r0 < 10.0
```

## Security Considerations

- Pure simulation logic, no external data sources.