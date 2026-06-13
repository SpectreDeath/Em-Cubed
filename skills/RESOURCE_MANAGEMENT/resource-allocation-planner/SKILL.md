---
Domain: RESOURCE_MANAGEMENT
Version: 1.0.0
Complexity: Medium
Type: Process
Category: Planning Skills
Estimated Execution Time: 2-5 minutes
name: resource-allocation-planner
Source: community
description: Resource allocation planner for budget distribution, scheduling, and load balancing across constrained resources.
compatibility: UNIVERSAL
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
origin: manual
triggers:
  - planning
  - optimization
  - scheduling
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T09:53:00Z"
examples:
  - "Allocate CPU across containers with priority constraints"
  - "Schedule workers across projects with skill requirements"
created_at: "2026-05-02T09:53:00Z"
updated_at: "2026-05-02T09:53:00Z"

## Purpose

Multi-surface resource allocation planner that combines Python for optimization algorithms, Prolog for constraint validation, and Hy for flexible priority scoring with multi-objective optimization.

## Description

This skill handles resource allocation problems by:
- Python for linear programming, genetic algorithms, and simulation
- Prolog for constraint consistency checking and resource compatibility rules
- Hy for fuzzy priority weighting and adaptive allocation strategies

## Examples

### Container CPU Allocation

```
Input: 4 containers with CPU requests and limits
Output: Optimal CPU shares satisfying all constraints
```

## Implementation

### Python Optimization

```python
from typing import Dict, List, Tuple, Optional
import random
import math

class ResourceAllocator:
    """Multi-objective resource allocation with various strategies."""
    
    def __init__(self, resources: Dict[str, float], demands: Dict[str, Dict]):
        """
        Initialize allocator.
        
        Args:
            resources: Available resources per type (e.g., {"cpu": 4000, "memory": 8192})
            demands: Resource demands per entity (e.g., {"container1": {"cpu": 500, "priority": 8}})
        """
        self.resources = resources
        self.demands = demands
        self.allocations = {entity: {} for entity in demands}
    
    def allocate_by_priority(self) -> Dict[str, Dict[str, float]]:
        """Allocate resources by priority weight."""
        sorted_entities = sorted(
            self.demands.keys(),
            key=lambda e: self.demands[e].get("priority", 0),
            reverse=True
        )
        
        remaining = self.resources.copy()
        
        for entity in sorted_entities:
            demand = self.demands[entity]
            for resource, amount in demand.items():
                if resource == "priority":
                    continue
                if resource in remaining:
                    alloc = min(amount, remaining[resource])
                    if alloc > 0:
                        self.allocations[entity][resource] = alloc
                        remaining[resource] -= alloc
        
        return self.allocations
    
    def genetic_algorithm(self, generations: int = 100, population_size: int = 50) -> Dict:
        """Use genetic algorithm for multi-objective optimization."""
        
        def fitness(individual: Dict) -> float:
            """Calculate fitness score for allocation."""
            score = 0.0
            for entity, allocation in individual.items():
                priority = self.demands[entity].get("priority", 1)
                demand = self.demands[entity]
                
                # Reward meeting demand
                for resource, amount in allocation.items():
                    if resource in demand:
                        demand_ratio = amount / demand[resource]
                        score += demand_ratio * priority
            
            # Penalty for constraint violations
            for resource, total_available in self.resources.items():
                total_allocated = sum(
                    ind.get(resource, 0) 
                    for ind in individual.values()
                )
                if total_allocated > total_available:
                    score -= (total_allocated - total_available) * 10
            
            return score
        
        def create_random_individual() -> Dict:
            """Create random valid allocation."""
            individual = {}
            for entity in self.demands:
                individual[entity] = {}
                for resource in self.resources:
                    max_alloc = min(
                        self.demands[entity].get(resource, float("inf")),
                        self.resources[resource]
                    )
                    individual[entity][resource] = random.uniform(0, max_alloc)
            return individual
        
        def crossover(parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
            """Uniform crossover between two individuals."""
            child1, child2 = {}, {}
            for entity in self.demands:
                child1[entity] = {}
                child2[entity] = {}
                for resource in self.resources:
                    if random.random() < 0.5:
                        child1[entity][resource] = parent1[entity].get(resource, 0)
                        child2[entity][resource] = parent2[entity].get(resource, 0)
                    else:
                        child1[entity][resource] = parent2[entity].get(resource, 0)
                        child2[entity][resource] = parent1[entity].get(resource, 0)
            return child1, child2
        
        def mutate(individual: Dict, mutation_rate: float = 0.1) -> Dict:
            """Apply random mutations."""
            for entity in individual:
                for resource in individual[entity]:
                    if random.random() < mutation_rate:
                        max_val = self.demands[entity].get(resource, self.resources[resource])
                        individual[entity][resource] = random.uniform(0, max_val)
            return individual
        
        # Initialize population
        population = [create_random_individual() for _ in range(population_size)]
        
        for _ in range(generations):
            # Evaluate fitness
            fitness_scores = [(ind, fitness(ind)) for ind in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top performers
            top = [ind for ind, _ in fitness_scores[:population_size // 2]]
            
            # Create next generation
            new_population = top[:2]  # Elitism
            
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(top, 2)
                child1, child2 = crossover(parent1, parent2)
                new_population.append(mutate(child1))
                if len(new_population) < population_size:
                    new_population.append(mutate(child2))
            
            population = new_population
        
        best = max(population, key=fitness)
        return best

def calculate_fair_share(total_resources: Dict, entities: List[str], weights: Dict[str, float] = None) -> Dict[str, Dict]:
    """Calculate fair resource shares based on weights."""
    if weights is None:
        weights = {e: 1.0 for e in entities}
    
    total_weight = sum(weights.values())
    normalized_weights = {e: w / total_weight for e, w in weights.items()}
    
    allocation = {}
    for entity in entities:
        allocation[entity] = {}
        for resource, total in total_resources.items():
            allocation[entity][resource] = total * normalized_weights[entity]
    
    return allocation
```

### Prolog Constraint Validation

```prolog
% Resource allocation constraints
valid_allocation(Resources, Demands, Allocations) :-
    % Total allocated should not exceed available
    forall(member(Resource-Allocated, Allocations),
           lookup_dict(Resource, Resources, Available),
           sum_allocation(Resource, Allocations, Total),
           Total =< Available).

% Resource type constraints
valid_resource_type(cpu, Value) :-
    number(Value),
    Value >= 0,
    Value =< 1000000.

valid_resource_type(memory, Value) :-
    number(Value),
    Value >= 0,
    Value =< 1000000.

valid_resource_type(storage, Value) :-
    number(Value),
    Value >= 0,
    Value =< 10000000.

% Priority constraints
min_priority(Min) :- Min >= 1, Min =< 10.

max_priority(Max) :- Max >= 1, Max =< 10.

% Allocation satisfaction
allocation_satisfies_demand(Entity, Allocation, Demand) :-
    forall(member(Resource-Request, Demand),
           (Resource \= priority,
            get_allocation(Resource, Allocation, Allocated),
            Allocated >= 0.8 * Request)).  % At least 80% of demand

% Conflict detection
allocation_conflict(Entity1, Entity2, Resource, Allocations) :-
    get_allocation(Resource, Allocations.Entity1, Amount1),
    get_allocation(Resource, Allocations.Entity2, Amount2),
    Amount1 + Amount2 > Available(Resource).
```

### Hy Adaptive Scoring

```hy
(defn exponential-weighting [weights decay-factor]
  "Apply exponential decay to weights for priority scoring"
  (let [sorted (sorted weights :key (fn [pair] (get pair 1]) >)]
    (for [i (range (len sorted))]
      (let [item (get sorted i)
            adjusted-priority (* (get item 1) (exp (* -decay-factor i)))]
        [item adjusted-priority])))

(defn penalty-score [allocations demands resources]
  "Calculate penalty score for constraint violations"
  (for [resource resources]
    (let [total-alloc (sum (get allocations resource))
          available (get resources resource)]
      (if (> total-alloc available)
          (* -100 (- total-alloc available))
          0)))

(defn efficiency-score [allocations demands]
  "Calculate efficiency based on demand fulfillment"
  (sum (map (fn [entity]
              (let [demand (get demands entity)
                    allocation (get allocations entity)
                    fulfilled (sum (filter (fn [r] (>= (get allocation r 0) (get demand r 0))) (keys demand)))]
                (/ fulfilled (len demand))))
            (keys demands))))

(defn fairness-index [allocations weights]
  "Calculate fairness index (Gini coefficient approximation)"
  (let [weighted (map (fn [pair] (* (get pair 0) (get weights (get pair 1)))) (items allocations))
        sorted (sorted weighted)
        cumsum (accumulate sorted)
        total (sum weighted)]
    (- 1 (/ (* 2 (sum (map (fn [i c] (* i c)) (range (len cumsum)) cumsum)))
             (* (len cumsum) total)))))

(defn adaptive-rebalance [current-allocations demands resources utilization-target]
  "Adaptively rebalance based on actual utilization"
  (let [utilization (map (fn [r] (/ (get current-allocations r 0) (get resources r 1))) (keys resources))
        over-allocated (filter (fn [r] (> (get utilization r) (* utilization-target 1.2))) (keys utilization))
        under-allocated (filter (fn [r] (< (get utilization r) (* utilization-target 0.8))) (keys utilization))]
    {:over-allocate over-allocated :under-allocate under-allocated}))
```

## Testing

```python
# Test resource allocator
from skills.resource_allocation_planner import ResourceAllocator

resources = {"cpu": 4000, "memory": 8192}
demands = {
    "container1": {"cpu": 1000, "memory": 2048, "priority": 8},
    "container2": {"cpu": 500, "memory": 1024, "priority": 5},
    "container3": {"cpu": 300, "memory": 512, "priority": 3}
}

allocator = ResourceAllocator(resources, demands)
result = allocator.allocate_by_priority()
assert result["container1"]["cpu"] == 1000
assert result["container2"]["cpu"] == 500
```