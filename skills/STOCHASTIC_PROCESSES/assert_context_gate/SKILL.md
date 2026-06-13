---
name: assert_context_gate
domain: STOCHASTIC_PROCESSES
version: "1.0.0"
surfaces: [prolog]
description: |
  Symbolic guard that evaluates whether a stochastic transition
  should be permitted under the current agent context.  Used to
  resolve ambiguous tokens or actions where environment state
  disambiguates which branch of the transition matrix is valid.
compatibility: PROLOG
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

# Assert Context Gate

## Purpose
Implement first-order logic rules to determine whether a proposed stochastic transition (or next-token prediction) is valid under the current agent context. Resolves ambiguity in Markov chain traversal where the transition matrix alone is insufficient to decide if a transition should be allowed.

## Connection to Veritasium Concepts
- **Context-gated state transitions**: Unlike simple Markov chains where the chain's future depends only on the current state, an M³ agent's state includes working memory. A context gate adds an extra dimension: P(s' | s, context) ≠ P(s' | s).
- **Disambiguation**: When two states share a common prefix n-gram or are reachable from the same node, the context gate selects the valid one.
- **Markov property with side information**: The gate effectively defines a "controlled" Markov chain where the control signal is drawn from the agent's belief state.

## Description
Pure symbolic skill. Rules encode:
1. **Agent capability gate**: Can the agent actually execute the next action in its current state?
2. **Resource gate**: Does the agent have sufficient remaining tokens/budget/credits for the proposed transition?
3. **Memory consistency gate**: Has the agent already traversed this transition recently (recent-visit penalty)?
4. **Safety gate**: Is the target state known-safe (no infinite loops or dead-ends)?

### Being State-Dependent, Not Memoryless
```prolog
% The M³ agent's context is a belief store, not the chain state.
% assert_context_gate reads from the agent's working memory:

% ?- agent_context(current_task, Task), safe_transition(From, To, Task)
% This extends the Markov chain into a "semi-Markov" decision process.

assert_valid_transition(From, To) :-
    agent_context(current_capability, Cap),
    capability_permits(Cap, To),
    agent_context(resource_level, Res),
    resource_sufficient(Res, To),
    \+ recently_visited(From, To).
```

## Prolog Surface (prelude.pl)

```prolog
:- module(context_gate, [
    assert_valid_transition/2,
    capability_permits/2,
    resource_sufficient/2,
    recently_visited/2,
    safe_target/1,
    gate_result/3
]).

% ============================================================
% 1. Agent capability matrix
%    Dynamically asserted by Python orchestration layer.
%    e.g., assertz(capability_permits(nlp_predict, generate_token)).
% ============================================================
:- dynamic capability_permits/2.
:- dynamic resource_sufficient/2.
:- dynamic recently_visited/2.
:- dynamic safe_target/1.

% Default capability table (extended at runtime)
capability_permits(nlp_predict, generate_token).
capability_permits(nlp_predict, end_sequence).
capability_permits(walk, follow_link).
capability_permits(walk, teleport).
capability_permits(optimize, take_step).

% ============================================================
% 2. Resource sufficiency gate
%    Resource levels are source-of-truth from agent state.
%    Returns sufficient if the transition cost < available resource.
% ============================================================
resource_sufficient(ResourceLevel, _) :-
    ResourceLevel > 0.

% Override for high-cost transitions
resource_sufficient(ResourceLevel, Transition) :-
    transition_cost(Transition, Cost),
    ResourceLevel >= Cost.

transition_cost(follow_link, 1).
transition_cost(teleport, 3).
transition_cost(generate_token, 1).
transition_cost(take_step, 5).

% ============================================================
% 3. Recency penalty (prevents tight loops)
% ============================================================
recently_visited(From, To) :-
    % A transition is "recent" if it was traversed in the last 3 steps
    last_transitions(RecentList),
    length(RecentList, Len),
    Len >= 3,
    member(transition(From, To), RecentList).

% Keep last 5 transitions in working memory
last_transitions(List) :-
    findall(transition(A, B), recent_transition(A, B), All),
    length(All, Len),
    ( Len > 5 -> length(Prefix, 5), append(Prefix, _, All) ; All = List ).

% ============================================================
% 4. Safety gate
% ============================================================
safe_target(To) :-
    \+ dead_end(To).

% ============================================================
% 5. Main gate predicate
% ============================================================
assert_valid_transition(From, To, Result) :-
    ( capability_permits(_, To)
    -> CapResult = ok
    ;   CapResult = blocked(no_capability)
    ),
    ( resource_sufficient(_, To)
    -> ResResult = ok
    ;   ResResult = blocked(insufficient_resource)
    ),
    \+ recently_visited(From, To)
    -> RecResult = ok
    ;   RecResult = blocked(recent_loop)
    ),
    safe_target(To)
    -> SafeResult = ok
    ;   SafeResult = blocked(unsafe_target)
    ),
    ( CapResult = ok, ResResult = ok, RecResult = ok, SafeResult = ok
    -> Result = allowed
    ;   Result = blocked(CapResult, ResResult, RecResult, SafeResult)
    ).

% ============================================================
% 6. Python bridge for context injection
% ============================================================
:- meta_predicate call_python(+, +, -).
```

## Python Surface (executor.py)

```python
"""
assert_context_gate
=====================
Bridge between Prolog symbolic context gates and the M³ agent's
working memory.  Reads agent state, asserts Prolog facts, and
queries gate permits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class GateResult:
    from_state: str
    to_state: str
    allowed: bool
    blocks: Tuple[str, ...]

    def to_dict(self):
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "allowed": self.allowed,
            "blocks": list(self.blocks),
        }


def build_context_facts(agent_state: dict) -> List[str]:
    """Synthesize Prolog fact assertions from agent working memory.

    Parameters
    ----------
    agent_state : dict
        M³ agent's current working memory snapshot.  Expected keys:
          - "capability": str
          - "resource_level": int
          - "recent_transitions": list of (from, to) tuples
          - "safe_targets": list of str or None

    Returns
    -------
    list of str
        Prolog fact strings to assert into the belief store.
    """
    facts: List[str] = []

    if "capability" in agent_state:
        facts.append(
            f"capability_permits({agent_state['capability']}, CURRENT_ACTION)."
        )

    if "resource_level" in agent_state:
        res = agent_state["resource_level"]
        facts.append(f"resource_context({res}).")

    if "recent_transitions" in agent_state:
        for i, (f, t) in enumerate(agent_state["recent_transitions"][-5:]):
            facts.append(f"recent_transition({f}, {t}).")

    if "safe_targets" in agent_state and agent_state["safe_targets"]:
        for t in agent_state["safe_targets"]:
            facts.append(f"safe_target({t}).")

    return facts
```

## Inputs

| name | type | description |
|---|---|---|
| from_state | str | Source state of proposed transition |
| to_state | str | Target state of proposed transition |
| agent_state | dict | M³ agent working-memory snapshot |
| agent_context | dict | Agent's current context (capabilities, resources, history) |

## Outputs

| name | type | description |
|---|---|---|
| allowed | bool | True if all gates pass |
| blocks | tuple[str] | List of gate names that blocked the transition |

## Gate Categories

| Gate | Block Label | Resolution |
|---|---|---|
| Agent capability | no_capability | Agent cannot perform To action |
| Resource sufficiency | insufficient_resource | Insufficient budget/tokens |
| Recency penalty | recent_loop | Transition recently traversed |
| Safety | unsafe_target | Target flagged as dead-end or unsafe |

## State Updates
```
belief_assert(capability_permits(Cap, Action))
belief_assert(recent_transition(From, To))
belief_add(context_gate_result(From, To, Result, Blocks))
```

## Error Handling
| Error | Condition |
|---|---|
| unbound_capability | No capability_permits fact for current action |
| unbound_resource | resource_context not asserted |

## Security
- Pure Prolog reasoning. No I/O.
- `agent_state` is not logged; only gating decisions are recorded.
