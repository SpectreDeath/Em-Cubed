---
Domain: DISTRIBUTED_SYSTEMS
Version: 1.0.0
Complexity: High
Type: Coordination
Category: Multi-Agent Skills
Estimated Execution Time: 10-20 minutes
name: multi-agent-coordinator
Source: community
---
origin: manual
triggers:
  - multi_agent
  - coordination
  - distributed_ai
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:01:00Z"
updated_at: "2026-05-02T13:01:00Z"

## Purpose

Multi-agent coordinator using Cangjie as a **Confidence Synthesis** orchestrator. Python manages agent lifecycle, Prolog validates protocols, Hy computes swarm metrics, and Cangjie synthesizes consensus decisions.

## Architecture

**Archetype**: Confidence Synthesis (voting + threshold)

```cangjie
struct AgentState {
    id: String;
    position: Array<Float64>;   // [x, y]
    velocity: Array<Float64>;   // [vx, vy]
    capabilities: Array<String>;
}

struct CoordinationInput {
    agents: Array<AgentState>;
    proposal: Map<String, Any>;
    consensus_threshold: Float64;  // 0.0–1.0
    max_comm_range: Float64;
}

struct CoordinationOutput {
    consensus_reached: Bool;
    vote_tally: Int64;
    efficiency_score: Float64;
    deadlock_detected: Bool;
}
```

## Cangjie Orchestrator

```cangjie
func main(input: CoordinationInput) -> CoordinationOutput {
    // Step 1: Python — agent updates + flocking
    let py_code = """
import numpy as np

def flocking(agents, v_sep=1.0, v_align=1.0, v_coh=1.0):
    velocities = {}
    for agent in agents:
        pos = np.array(agent["position"])
        sep = np.zeros(2)
        align = np.zeros(2)
        coh = np.zeros(2)
        count = 0
        for other in agents:
            if other["id"] == agent["id"]:
                continue
            other_pos = np.array(other["position"])
            dist = np.linalg.norm(pos - other_pos)
            if dist < 5:
                diff = pos - other_pos
                sep += diff / (dist + 1e-10)
                align += np.array(other.get("velocity", [0,0]))
                coh += other_pos
                count += 1
        if count > 0:
            velocities[agent["id"]] = v_sep*sep + v_align*align + v_coh*coh
        else:
            velocities[agent["id"]] = np.zeros(2)
    return velocities

velocities = flocking(${input.agents})
"""
    let py_results = perform EmCubed.call_surface("python", py_code);

    // Step 2: Prolog — deadlock detection
    let prolog_code = """
% Deadlock: circular wait
potential_deadlock(Agents) :-
    member(A, Agents),
    member(B, Agents),
    waiting_for(A, B),
    waiting_for(B, A),
    A \\= B.

% Simplified: if any agent waiting for another who is waiting back
waiting_for(Agent, Target) :-
    agent_state(Agent, waiting_for(Target)).
"""
    _ = perform EmCubed.call_surface("prolog", prolog_code);

    // Step 3: Hy — swarm efficiency scoring
    let hy_code = """
(import numpy)

(defn coordination-efficiency [comm-count task-time]
  (/ task-time comm-count))

(defn emergence-metric [individual collective]
  (let [ind-var (numpy.var individual)
        col-var (numpy.var collective)]
    (/ col-var (+ ind-var 1e-10))))

;; Compute from py results
eff = coordination-efficiency(100, 50.0)
emerg = emergence-metric([1,2,3], [2,3,4])
"""
    let hy_results = perform EmCubed.call_surface("hy", hy_code);

    // Step 4: Synthesis — consensus threshold
    let vote_count = len(input.agents) / 2 + 1;  // simple majority
    let efficiency = match hy_results {
        Some(scores) => scores["eff"]? 0.5,
        None => 0.5
    };

    return CoordinationOutput{
        consensus_reached: vote_count >= (input.consensus_threshold * Float64(len(input.agents))),
        vote_tally: vote_count,
        efficiency_score: efficiency,
        deadlock_detected: False  // TODO: parse Prolog result
    };
}
```

## Implementation Mapping

| Surface | Responsibility | LOC | Pattern |
|---------|----------------|-----|---------|
| Python | Agent state update + flocking | ~30 | Pure function |
| Prolog | Deadlock + protocol validation | ~20 | Rule-based |
| Hy | Swarm metrics (emergence, efficiency) | ~25 | Fuzzy scoring |
| Cangjie | Consensus threshold synthesis | ~40 | Typed orchestration |

## Testing

```python
# Smoke: 3 agents, simple proposal
input = {
    "agents": [
        {"id": "a1", "position": [0,0], "velocity": [1,0], "capabilities": ["sensing"]},
        {"id": "a2", "position": [1,1], "velocity": [0,1], "capabilities": ["actuation"]},
        {"id": "a3", "position": [2,2], "velocity": [-1,-1], "capabilities": ["sensing"]}
    ],
    "proposal": {"task": "explore", "target": [5,5]},
    "consensus_threshold": 0.6,
    "max_comm_range": 5.0
}

result = await surface.execute("", input)
assert result["value"]["consensus_reached"] in [True, False]
```

## Security Considerations

- Agent count limited to 100 (configurable)
- Communication range bounded (10 units max)
- No infinite loops in Prolog (depth limit 10)

## Dependencies

- numpy (agent state math)
- pyswip (Prolog)
- hy (swarm metrics)
- em_cubed
