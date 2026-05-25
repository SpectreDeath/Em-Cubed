# Resource Allocation Planner - Cangjie Edition
# Cangjie-orchestrated multi-surface resource optimization

# Cangjie surface block: orchestrator
func main() {
    // Input: resources, demands, constraints
    let alloc_data = context["allocation_data"] as AllocInput;

    println("Cangjie Resource Allocator Starting...");

    // 1. Python: Compute priority-based allocation + GA optimization
    let py_result = perform EmCubed.call_surface("python", "
import random
import math
from typing import Dict, List, Tuple

def allocate_by_priority(resources, demands):
    \"\"\"Greedy allocation by priority.\"\"\"
    sorted_entities = sorted(demands.keys(),
                             key=lambda e: demands[e].get('priority', 0),
                             reverse=True)
    remaining = resources.copy()
    allocations = {entity: {} for entity in demands}

    for entity in sorted_entities:
        demand = demands[entity]
        for resource, amount in demand.items():
            if resource == 'priority':
                continue
            if resource in remaining:
                alloc = min(amount, remaining[resource])
                if alloc > 0:
                    allocations[entity][resource] = alloc
                    remaining[resource] -= alloc
    return allocations

def genetic_allocation(resources, demands, generations=50, pop_size=30):
    \"\"\"GA for multi-objective allocation.\"\"\"
    def fitness(individual):
        score = 0.0
        # Reward meeting demand proportionally to priority
        for entity, allocation in individual.items():
            priority = demands[entity].get('priority', 1)
            for resource, amount in allocation.items():
                if resource in demands[entity]:
                    ratio = amount / demands[entity][resource]
                    score += ratio * priority
        # Penalty for resource overflow
        for resource, total_avail in resources.items():
            total_alloc = sum(ind.get(resource, 0) for ind in individual.values())
            if total_alloc > total_avail:
                score -= (total_alloc - total_avail) * 10
        return score

    def create_individual():
        ind = {}
        for entity in demands:
            ind[entity] = {}
            for resource in resources:
                max_alloc = min(demands[entity].get(resource, float('inf')),
                               resources[resource])
                ind[entity][resource] = random.uniform(0, max_alloc)
        return ind

    population = [create_individual() for _ in range(pop_size)]
    for gen in range(generations):
        fitness_scores = [(ind, fitness(ind)) for ind in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        top = [ind for ind, _ in fitness_scores[:pop_size//2]]
        new_pop = top[:2]  # Elitism
        while len(new_pop) < pop_size:
            p1, p2 = random.sample(top, 2)
            child = {}
            for entity in demands:
                child[entity] = {}
                for resource in resources:
                    child[entity][resource] = p1[entity].get(resource, 0) if random.random() < 0.5 else p2[entity].get(resource, 0)
            new_pop.append(child)
        population = new_pop

    best = max(population, key=fitness)
    return best

resources = ${alloc_data.resources}
demands = ${alloc_data.demands}
greedy = allocate_by_priority(resources, demands)
ga_opt = genetic_allocation(resources, demands, 30, 20)
{'greedy': greedy, 'ga': ga_opt}
    ");

    // 2. Prolog: Validate constraint satisfaction
    let prolog_constraints = build_constraint_facts(alloc_data);
    let prolog_validate = perform EmCubed.call_surface("prolog", prolog_constraints + "
% Check if allocation satisfies all constraints
check_allocation(Alloc, Resources) :-
    forall(member(Resource-Amount, Alloc),
           (member(Resource, Resources),
            Amount >= 0,
            Amount =< Resource)).

check_allocation(Alloc, _) :-
    format('ERROR: Allocation ~w violates constraints~n', [Alloc]),
    fail.

% Verify greedy solution
valid_greedy = check_allocation(${py_result['greedy']}, ${alloc_data.resources}).
    ");

    // 3. Hy: Fuzzy fairness & efficiency scoring
    let hy_score = perform EmCubed.call_surface("hy", "
(defn fairness-index [allocations]
  \"Calculate Gini-like fairness score\"
  (let [values (list (map (fn [entity] (sum (vals entity))) allocations))
        sorted (sorted values)
        n (len sorted)
        cumsum (accumulate sorted)
        total (sum sorted)]
    (- 1 (/ (* 2 (sum (map (fn [i c] (* i c)) (range n) cumsum)))
            (* n total)))))

(defn efficiency-score [allocations demands]
  \"How well demands are satisfied\"
  (let [scores (list-comp
                 (/ (sum (vals (get allocations e))) (sum (vals (get demands e))))
                 [e (keys allocations)])
    (mean scores)))

(let [greedy ${py_result['greedy']}
      ga ${py_result['ga']}
      demands ${alloc_data.demands}]
  {:greedy_fair (fairness-index greedy)
   :greedy_eff (efficiency-score greedy demands)
   :ga_fair (fairness-index ga)
   :ga_eff (efficiency-score ga demands)})
    ");

    // 4. Synthesize best allocation
    let fairness_scores = hy_score.get("value", {});
    let best = select_best_solution(py_result, fairness_scores);

    return {
        "allocation": best,
        "fairness": fairness_scores,
        "constraints_ok": prolog_validate.get("status") == "ok"
    };
}

func build_constraint_facts(data: AllocInput): String {
    let facts = StringBuilder();
    facts.append("% Resource limits\n");
    for (resource, amount in data.resources) {
        facts.append("resource_limit(").append(resource).append(", ")
            .append(amount).append(").\n");
    }
    facts.append("\n% Demands\n");
    for (entity, demand in data.demands) {
        for (resource, amount in demand) {
            if (resource != "priority") {
                facts.append("demand(").append(entity).append(", ")
                    .append(resource).append(", ").append(amount).append(").\n");
            }
        }
    }
    return facts.toString();
}

func select_best_solution(py: Map, fairness: Map): Map {
    // Simple selection: prefer GA if fairness > greedy fairness
    let greedy_fair = fairness.get("greedy_fair", 0.0);
    let ga_fair = fairness.get("ga_fair", 0.0);
    if (ga_fair > greedy_fair) {
        return py.get("ga", {});
    }
    return py.get("greedy", {});
}

struct AllocInput {
    resources: Map<String, Float64>;
    demands: Map<String, Map<String, Float64>>;
}
