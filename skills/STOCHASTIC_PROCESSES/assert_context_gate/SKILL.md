---
name: assert_context_gate
domain: STOCHASTIC_PROCESSES
version: 1.0.0
surfaces:
  - prolog
  - python
description: Symbolic context-gating engine evaluating whether candidate stochastic state transitions should be permitted under the agent's current working memory and operational state. Extends standard Markov chains into controlled Markov processes where transition probabilities depend on agent context $P(s' \mid s, \text{context})$, verifying agent capabilities, resource budgets, recency loop penalties, and target safety in Prolog. Use when disambiguating stochastic branches, preventing cyclic loops, or enforcing policy constraints during Markov graph traversal.
purpose: Evaluate and enforce symbolic context gates on Markov state transitions using Prolog first-order logic and working-memory context.
dependencies:
  - STOCHASTIC_PROCESSES/generate_transition_matrix
tags:
  - context-gate
  - controlled-markov-chain
  - symbolic-guard
  - capability-gating
  - loop-prevention
  - prolog-reasoning
inputs:
  from_state:
    type: string
    required: true
    description: Source state of the proposed transition.
  to_state:
    type: string
    required: true
    description: Candidate target state of the proposed transition.
  agent_state:
    type: object
    required: true
    description: 'Agent working memory snapshot `{capability: str, resource_level: int, recent_transitions: [...], safe_targets: [...]}`.'
outputs:
  allowed:
    type: boolean
    description: True if all four symbolic gates (capability, resource, recency, safety) pass.
  blocks:
    type: array
    description: List of gate violation identifiers if blocked (e.g. `['no_capability', 'insufficient_resource']`).
  gate_breakdown:
    type: object
    description: Detailed status of each evaluated gate component.
---

# Assert Context Gate Engine

`assert_context_gate` extends classical memoryless Markov chains $P(s_{t+1} \mid s_t)$ into **controlled stochastic processes** where transitions are mediated by the agent's internal working-memory belief state $P(s_{t+1} \mid s_t, \text{context})$. It enforces **first-order logic constraints in Prolog** across four gating dimensions:

$$\text{Gate}(\text{From}, \text{To}) = \text{Capability}(\text{To}) \land \text{Resource}(\text{To}) \land \neg \text{RecentLoop}(\text{From}, \text{To}) \land \text{SafeTarget}(\text{To})$$

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage Context Gate Progression

```
[1. Working Memory Ingest & State Audit] → [2. Prolog Fact Synthesis] → [3. Visual Brief] → [4. Checkpoint] → [5. Gating Decision & Belief Emit]
```

### Stage 1: Working Memory Ingest & State Audit
1. Ingest `from_state`, `to_state`, and `agent_state` dictionary.
2. Assert that `capability` and `resource_level` fields are defined.
3. Validate recent transition history buffer.

> **Completion criterion**: Clean agent state context payload verified.

---

### Stage 2: Prolog Fact Synthesis & Assertion
1. Synthesize dynamic Prolog facts from working memory:
   - `capability_permits(Cap, Action)`
   - `resource_context(Level)`
   - `recent_transition(From, To)`
   - `safe_target(To)`
2. Query Prolog gate engine for structural admissibility.

> **Completion criterion**: Dynamic facts asserted into belief store.

---

### Stage 3: The Visual Brief
For controlled Markov decisions and policy gating, generate an interactive brief:
- **Location**: Write to `%TEMP%\context-gate-brief-<timestamp>.html` (Windows) or `/tmp/context-gate-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render state transition decision tree with active/blocked paths, 4-gate status checklist (Capability, Budget, Loop, Safety), and transition cost breakdown.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before finalizing gating permission:
1. Inspect loop detection: if $(\text{From}, \text{To})$ was traversed within the last 3 steps, flag `recent_loop` block.
2. Verify resource balance: ensure remaining budget $\ge \text{Cost}(\text{To})$.

> **Completion criterion**: Loop prevention and budget bounds evaluated.

---

### Stage 5: Gating Decision & Belief Emission
1. Compile composite `allowed` boolean flag and list of `blocks`.
2. Format full diagnostic gate breakdown.
3. Emit complete `GateResult` record.

> **Completion criterion**: Full gating result record emitted.

---

## Surface References

### Prolog Gate Surface

```prolog
:- module(context_gate, [
    assert_valid_transition/3,
    capability_permits/2,
    resource_sufficient/2,
    recently_visited/2,
    safe_target/1
]).

:- dynamic capability_permits/2.
:- dynamic resource_context/1.
:- dynamic recent_transition/2.
:- dynamic safe_target/1.

transition_cost(follow_link, 1).
transition_cost(teleport, 3).
transition_cost(generate_token, 1).
transition_cost(take_step, 5).

resource_sufficient(ResourceLevel, Action) :-
    transition_cost(Action, Cost),
    ResourceLevel >= Cost.
resource_sufficient(ResourceLevel, _) :-
    ResourceLevel > 0.

recently_visited(From, To) :-
    findall(transition(A, B), recent_transition(A, B), All),
    member(transition(From, To), All).

safe_target(To) :- \+ dead_end(To).

assert_valid_transition(From, To, Result) :-
    ( capability_permits(_, To) -> CapResult = ok ; CapResult = blocked(no_capability) ),
    ( (resource_context(R), resource_sufficient(R, To)) -> ResResult = ok ; ResResult = blocked(insufficient_resource) ),
    ( \+ recently_visited(From, To) -> RecResult = ok ; RecResult = blocked(recent_loop) ),
    ( safe_target(To) -> SafeResult = ok ; SafeResult = blocked(unsafe_target) ),
    ( CapResult = ok, ResResult = ok, RecResult = ok, SafeResult = ok
    -> Result = allowed
    ; Result = blocked([CapResult, ResResult, RecResult, SafeResult])
    ).
```

### Python Calculation Surface

```python
from typing import Dict, List, Any, Tuple

def evaluate_context_gate(from_state: str, to_state: str, agent_state: Dict[str, Any]) -> Dict[str, Any]:
    cap = agent_state.get("capability", "default")
    res_level = int(agent_state.get("resource_level", 0))
    recent = agent_state.get("recent_transitions", [])
    safe_targets = agent_state.get("safe_targets", [])
    
    blocks = []
    
    # 1. Capability gate
    allowed_caps = {"generate_token", "follow_link", "teleport", "take_step", "default"}
    if cap not in allowed_caps and to_state not in allowed_caps:
        blocks.append("no_capability")
        
    # 2. Resource sufficiency gate
    cost_map = {"follow_link": 1, "teleport": 3, "generate_token": 1, "take_step": 5}
    cost = cost_map.get(to_state, 1)
    if res_level < cost:
        blocks.append("insufficient_resource")
        
    # 3. Recency loop penalty (last 3 transitions)
    last_3 = recent[-3:] if len(recent) >= 3 else recent
    if any(f == from_state and t == to_state for f, t in last_3):
        blocks.append("recent_loop")
        
    # 4. Safety gate
    if safe_targets and to_state not in safe_targets:
        blocks.append("unsafe_target")
        
    is_allowed = len(blocks) == 0
    return {
        "from_state": from_state,
        "to_state": to_state,
        "allowed": is_allowed,
        "blocks": blocks,
        "gate_breakdown": {
            "capability_ok": "no_capability" not in blocks,
            "resource_ok": "insufficient_resource" not in blocks,
            "recency_ok": "recent_loop" not in blocks,
            "safety_ok": "unsafe_target" not in blocks
        }
    }
```

---

## Anti-Patterns & Guardrails

- **Unchecked Cyclic Looping** — Allowing stochastic walks to bounce indefinitely between two states without recency memory tracking.
- **Resource Depletion Bypass** — Permitting high-cost transitions (e.g. teleportation) when agent token budget is exhausted ($R \le 0$).
- **Dead-End Trapping** — Routing to terminal dead-end states when safe alternative branches exist.
