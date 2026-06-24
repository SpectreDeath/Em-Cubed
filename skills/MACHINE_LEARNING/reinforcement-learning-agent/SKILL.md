---
name: reinforcement-learning-agent
domain: MACHINE_LEARNING
version: 1.0.0
description: Skill for reinforcement-learning-agent.
compatibility: UNIVERSAL
complexity: High
type: Process
category: AI Skills
estimated execution time: 10-30 minutes
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
  - reinforcement_learning
  - autonomous_agent
  - decision_making
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:59:00Z"
updated_at: "2026-05-02T12:59:00Z"

## Purpose

Multi-surface reinforcement learning agent that uses Python for Q-learning and policy gradients, Prolog for logical policy constraints, and Hy for exploration strategy optimization.

## Description

This skill implements RL agents by:
- Python for environment interaction, Q-learning, and deep RL
- Prolog for logical policy validation and safety constraints
- Hy for fuzzy exploration and adaptive learning rate adjustment

## Implementation

### Python RL Core

```python
import numpy as np
from typing import Dict, List, Tuple, Callable, Optional
from collections import deque
import random

class QLearningAgent:
    """Q-learning agent with multi-surface support."""
    
    def __init__(self, states: int, actions: int, 
                 learning_rate: float = 0.1, 
                 discount: float = 0.95,
                 epsilon: float = 1.0,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        self.q_table = np.zeros((states, actions))
        self.learning_rate = learning_rate
        self.discount = discount
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.memory = deque(maxlen=10000)
    
    def act(self, state: int) -> int:
        """Choose action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            return random.randint(0, self.q_table.shape[1] - 1)
        return np.argmax(self.q_table[state])
    
    def learn(self, state: int, action: int, reward: float, 
              next_state: int, done: bool) -> None:
        """Q-learning update."""
        current_q = self.q_table[state, action]
        next_max_q = np.max(self.q_table[next_state]) if not done else 0
        
        new_q = (1 - self.learning_rate) * current_q + \
                self.learning_rate * (reward + self.discount * next_max_q)
        self.q_table[state, action] = new_q
        
        self.memory.append((state, action, reward, next_state, done))
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class PolicyGradientAgent:
    """Policy gradient agent."""
    
    def __init__(self, state_dim: int, action_dim: int, lr: float = 0.01):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.theta = np.random.randn(state_dim, action_dim) * 0.01
        self.lr = lr
    
    def policy(self, state: np.ndarray) -> np.ndarray:
        """Softmax policy."""
        logits = state @ self.theta
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / exp_logits.sum()
    
    def act(self, state: np.ndarray) -> int:
        probs = self.policy(state)
        return np.random.choice(self.action_dim, p=probs)

def multi_agent_rl(agents: List[QLearningAgent], 
                   environment) -> Dict[str, np.ndarray]:
    """Coordinate multiple RL agents."""
    trajectories = {}
    for i, agent in enumerate(agents):
        trajectory = []
        state = environment.reset()
        done = False
        while not done:
            action = agent.act(state)
            next_state, reward, done, _ = environment.step(action)
            agent.learn(state, action, reward, next_state, done)
            trajectory.append((state, action, reward))
            state = next_state
        trajectories[f"agent_{i}"] = np.array(trajectory)
    return trajectories

def experience_replay(agent: QLearningAgent, batch_size: int = 32) -> None:
    """Train from experience replay."""
    if len(agent.memory) < batch_size:
        return
    
    batch = random.sample(agent.memory, batch_size)
    for state, action, reward, next_state, done in batch:
        current_q = agent.q_table[state, action]
        next_max_q = np.max(agent.q_table[next_state]) if not done else 0
        new_q = (1 - agent.learning_rate) * current_q + \
                agent.learning_rate * (reward + agent.discount * next_max_q)
        agent.q_table[state, action] = new_q
```

### Prolog Policy Logic

```prolog
% Policy constraint rules
valid_action(State, Action, Policy) :-
    policy_rule(State, Action, RequiredConditions),
    satisfies_conditions(RequiredConditions, State).

% Safety constraints
safe_action(Action, CurrentState) :-
    safety_constraint(Action, Constraints),
    check_constraints(Constraints, CurrentState, Valid),
    Valid = true.

% Multi-agent coordination
coordinated_actions(AgentActions, GlobalState) :-
    findall(Agent-Action, member(agent_action(Agent, Action), AgentActions), Pairs),
    valid_joint_action(Pairs, GlobalState).

% Exploration constraints
exploration_allowed(State, Action) :-
    visited(State, Action),
    visit_count(State, Action, Count),
    Count < 10.  % Allow exploration of visited states up to 10 times

% Reward shaping
shaped_reward(OriginalReward, State, NextState, ShapedReward) :-
    potential(State, Potential1),
    potential(NextState, Potential2),
    gamma(Gamma),
    ShapedReward is OriginalReward + Gamma * Potential2 - Potential1.

% Convergence detection
converged(QTable, Threshold) :-
    findall(V, member(V, QTable), Values),
    variance(Values, Var),
    Var < Threshold.
```

### Hy Exploration Optimization

```hy
(defn adaptive-exploration [q-values state action-counts]
  "Adaptive exploration strategy based on Q-value uncertainty"
  (let [q-std (numpy.std (get q-values state))
        visits (get action-counts state)
        uncertainty-bonus (* 1.0 (/ 1 (+ 1 (sum visits))))]
    (+ (get (get q-values state) action) (* 0.5 uncertainty-bonus))))

(defn learning-rate-schedule [episode total-episodes]
  "Decay learning rate over episodes"
  (/ 1 (+ 1 (* 0.01 episode))))

(defn multi-armed-bandit [rewards n-arms n-pulls]
  "Multi-armed bandit action selection"
  (let [successes (map (fn [r] (sum (map (fn [x] (if (>= x 0) 1 0)) r))) (partition 1 rewards))
        totals (map len (partition 1 rewards))]
    (map (fn [s t] (+ 1 (/ s (+ 2 t)))) successes totals)))

(defn policy-entropy [policy]
  "Calculate policy entropy for exploration measurement"
  (* -1 (sum (map (fn [p] (* p (numpy.log p))) policy))))

(defn curiosity-driven-action [state visited-states intrinsic-reward]
  "Select actions based on novelty"
  (let [novelty (if (in state visited-states) 0.1 1.0)
        combined-reward (+ intrinsic-reward novelty)]
    combined-reward))
```

## Testing

```python
# Test Q-learning agent
from skills.reinforcement_learning_agent import QLearningAgent

agent = QLearningAgent(states=10, actions=4)
action = agent.act(5)
assert 0 <= action <= 3
agent.learn(5, action, 1.0, 6, False)
assert agent.epsilon < 1.0  # Epsilon should decay
```