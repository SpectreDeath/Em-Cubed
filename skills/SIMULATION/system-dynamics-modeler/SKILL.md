---
name: system-dynamics-modeler
domain: SIMULATION
version: 1.0.0
description: System dynamics modeler for stock-flow simulation, feedback loop analysis, and policy scenario testing.
compatibility: UNIVERSAL
complexity: High
type: Modeling
category: Systems Skills
estimated execution time: 10-20 minutes
source: community
allowed-tools: '- read

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

  '
---
origin: manual
triggers:
  - simulation
  - system_dynamics
  - causal_modeling
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:30:00Z"
updated_at: "2026-05-02T12:30:00Z"

## Purpose

Multi-surface system dynamics modeler that combines Python for numerical simulation, Prolog for causal relationship logic, and Datalog for recursive feedback loop analysis.

## Description

This skill builds and simulates system dynamics models by:
- Python for differential equation solving and simulation
- Prolog for causal loop detection and feedback analysis
- Datalog for recursive system relationship modeling

## Examples

### Population Dynamics Model

```
Input: Birth rates, death rates, migration, carrying capacity
Output: Population trajectory with confidence intervals
```

## Implementation

### Python System Simulation

```python
import numpy as np
from typing import Dict, List, Callable, Tuple, Optional
from scipy.integrate import odeint
from dataclasses import dataclass, field
import networkx as nx

@dataclass
class Stock:
    name: str
    value: float
    min_val: float = 0
    max_val: float = float('inf')

@dataclass
class Flow:
    name: str
    source: str
    target: str
    rate_func: Callable
    equation: str

class SystemDynamicsModel:
    """System dynamics modeling and simulation."""
    
    def __init__(self):
        self.stocks: Dict[str, Stock] = {}
        self.flows: List[Flow] = []
        self.variables: Dict[str, float] = {}
        self.equations: Dict[str, str] = {}
    
    def add_stock(self, stock: Stock) -> None:
        """Add a stock (state variable)."""
        self.stocks[stock.name] = stock
    
    def add_flow(self, flow: Flow) -> None:
        """Add a flow (rate of change)."""
        self.flows.append(flow)
    
    def set_variable(self, name: str, value: float) -> None:
        """Set a model variable."""
        self.variables[name] = value
    
    def _derivatives(self, state: np.ndarray, t: float) -> np.ndarray:
        """Compute derivatives for ODE solver."""
        derivatives = np.zeros(len(state))
        
        # Create state dictionary
        state_dict = {name: val for name, val in zip(self.stocks.keys(), state)}
        state_dict.update({k: v for k, v in self.variables.items()})
        
        # Compute flows
        for flow in self.flows:
            rate = flow.rate_func(state_dict, t)
            idx = list(self.stocks.keys()).index(flow.target)
            derivatives[idx] += rate
            
            if flow.source in self.stocks:
                src_idx = list(self.stocks.keys()).index(flow.source)
                derivatives[src_idx] -= rate
        
        return derivatives
    
    def simulate(self, time_span: Tuple[float, float], n_points: int = 1000) -> Dict[str, np.ndarray]:
        """Run simulation."""
        t = np.linspace(time_span[0], time_span[1], n_points)
        initial_state = np.array([s.value for s in self.stocks.values()])
        
        solution = odeint(self._derivatives, initial_state, t)
        
        results = {"time": t}
        for i, name in enumerate(self.stocks.keys()):
            results[name] = solution[:, i]
        
        return results
    
    def find_equilibrium(self, tolerance: float = 1e-6) -> Optional[np.ndarray]:
        """Find equilibrium point."""
        from scipy.optimize import root
        
        def equilibrium_equations(state):
            return self._derivatives(state, 0)
        
        initial = np.array([s.value for s in self.stocks.values()])
        result = root(equilibrium_equations, initial, method='hybr')
        
        if result.success and np.allclose(result.fun, 0, atol=tolerance):
            return result.x
        return None

def lotka_volterra_prey(predator_population: float, prey_birth_rate: float = 1.0,
                       prey_death_rate: float = 0.1, predation_rate: float = 0.01):
    """Lotka-Volterra prey dynamics."""
    return lambda state, t: state.get("prey_birth_rate", prey_birth_rate) * state["prey"] - \
                            state.get("predation_rate", predation_rate) * state["prey"] * state["predator"]

def lotka_volterra_predator(predator_death_rate: float = 0.1, 
                            predator_efficiency: float = 0.5, 
                            predation_rate: float = 0.01):
    """Lotka-Volterra predator dynamics."""
    return lambda state, t: state.get("predator_efficiency", predator_efficiency) * \
                            state.get("predation_rate", predation_rate) * state["prey"] * state["predator"] - \
                            state.get("predator_death_rate", predator_death_rate) * state["predator"]

class CausalLoopDiagram:
    """Analyze causal relationships in system dynamics."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_link(self, source: str, target: str, polarity: str = "+") -> None:
        """Add causal link."""
        self.graph.add_edge(source, target, polarity=polarity)
    
    def find_feedback_loops(self) -> List[List[str]]:
        """Find all feedback loops."""
        cycles = list(nx.simple_cycles(self.graph))
        return [c + [c[0]] for c in cycles]
    
    def loop_polarity(self, loop: List[str]) -> str:
        """Determine overall polarity of feedback loop."""
        polarities = []
        for i in range(len(loop) - 1):
            edge_data = self.graph.get_edge_data(loop[i], loop[i+1])
            if edge_data:
                polarities.append(edge_data.get("polarity", "+"))
        
        # Odd number of negative links = negative feedback
        negative_count = sum(1 for p in polarities if p == "-")
        return "negative" if negative_count % 2 == 1 else "positive"
```

### Prolog Causal Logic

```prolog
% System dynamics rules
causal_link(From, To, Polarity) :-
    link(From, To, Polarity).

% Feedback loop detection
feedback_loop(Start, Path) :-
    path(Start, Start, Path),
    length(Path, Len),
    Len > 2.

% System equilibrium conditions
equilibrium_reached(Variables, Thresholds) :-
    forall(member(Var-Value, Variables),
           member(Var-Threshold, Thresholds),
           abs(Value - Threshold) =< 0.01).

% Stability analysis
stable_system(Derivatives, Tolerance) :-
    findall(D, member(D, Derivatives), NonZeroDerivs),
    length(NonZeroDerivs, ZeroCount),
    ZeroCount =:= 0.

unstable_system(Derivatives, Threshold) :-
    member(D, Derivatives),
    abs(D) > Threshold.

% Causal influence propagation
influences(Variable1, Variable2, Strength) :-
    causal_link(Variable1, Variable2, _),
    compute_influence(Variable1, Variable2, Strength).

influences(Variable1, Variable3, TotalStrength) :-
    causal_link(Variable1, Variable2, _),
    influences(Variable2, Variable3, Strength2),
    TotalStrength is 0.5 * Strength2.

% Stock-flow consistency
valid_stock_flow(Stock, InFlows, OutFlows) :-
    sum_list(InFlows, TotalIn),
    sum_list(OutFlows, TotalOut),
    StockChange is TotalIn - TotalOut.

% Time delay handling
delayed_effect(Effect, Delay, CurrentTime) :-
    cause(Cause, Effect, TimeOfCause),
    Delay > 0,
    CurrentTime is TimeOfCause + Delay.
```

### Datalog Recursive Properties

```datalog
% Transitivity of causality
causes(X, Z) :- causes(X, Y), causes(Y, Z).

% Influence propagation
influences_directly(X, Y) :- causal_link(X, Y, _).
influences_directly(X, Y) :- causal_link(X, Z, _), causal_link(Z, Y, _).

% Strong connectivity
strongly_connected(X, Y) :-
    causes(X, Y),
    causes(Y, X).

% System attractors
attractor_state(S) :-
    stable(S),
    basin_of_attraction(S, Basin),
    size(Basin, Size),
    Size > 10.

% Policy impact analysis
policy_impact(Policy, Outcome, Strength) :-
    policy_link(Policy, Variable, Effect),
    influences(Variable, Outcome, Strength).

% Scenario analysis
scenario_outcome(Scenario, Variable, FinalValue) :-
    initial_state(Scenario, Initial),
    simulate(Scenario, Time, Final),
    final_value(Variable, FinalValue).

% Feedback loop polarity
negative_feedback(Loop) :-
    loop_edges(Loop, Edges),
    count_negative(Edges, NegCount),
    NegCount mod 2 = 1.

positive_feedback(Loop) :-
    loop_edges(Loop, Edges),
    count_negative(Edges, NegCount),
    NegCount mod 2 = 0.
```

## Testing

```python
# Test system dynamics
from skills.system_dynamics_modeler import SystemDynamicsModel, Stock, Flow, lotka_volterra

model = SystemDynamicsModel()
model.add_stock(Stock("prey", 40))
model.add_stock(Stock("predator", 9))

model.add_flow(Flow("prey_growth", "", "prey", 
                   lotka_volterra_prey()({"prey": 40, "predator": 9}, 0), ""))

results = model.simulate((0, 100), 1000)
assert "prey" in results
assert len(results["prey"]) == 1000
```