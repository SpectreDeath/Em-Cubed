# System Dynamics Modeler - Cangjie Edition
# Cangjie-orchestrated system dynamics with causal reasoning

# Cangjie surface block: orchestrator
func main() {
    // Input: system stocks, flows, parameters, simulation horizon
    let sd_data = context["system_data"] as SDInput;

    println("Cangjie System Dynamics Starting...");

    // 1. Python: Solve ODE system, simulate dynamics
    let py_sim = perform EmCubed.call_surface("python", "
import numpy as np
from scipy.integrate import odeint
from typing import Dict, Callable, Tuple

class SystemDynamicsModel:
    def __init__(self):
        self.stocks = {}
        self.flows = []
        self.vars = {}

    def add_stock(self, name, initial):
        self.stocks[name] = initial

    def add_flow(self, name, source, target, rate_func):
        self.flows.append({'name': name, 'source': source, 'target': target, 'rate': rate_func})

    def derivatives(self, state, t):
        dstate = np.zeros_like(state)
        state_dict = dict(zip(self.stocks.keys(), state))
        for flow in self.flows:
            rate = flow['rate'](state_dict, t)
            src_idx = list(self.stocks.keys()).index(flow['source']) if flow['source'] else -1
            tgt_idx = list(self.stocks.keys()).index(flow['target'])
            if src_idx >= 0:
                dstate[src_idx] -= rate
            dstate[tgt_idx] += rate
        return dstate

    def simulate(self, t_span, n_points=1000):
        t = np.linspace(t_span[0], t_span[1], n_points)
        initial = np.array(list(self.stocks.values()))
        solution = odeint(self.derivatives, initial, t)
        return {'time': t.tolist(),
                'stocks': {k: solution[:,i].tolist() for i,k in enumerate(self.stocks.keys())}}

# Build model
model = SystemDynamicsModel()
model.add_stock('prey', ${sd_data.initial_prey})
model.add_stock('predator', ${sd_data.initial_predator})

# Lotka-Volterra flows
model.add_flow('prey_growth', None, 'prey',
              lambda s, t: s['prey'] * (${sd_data.prey_growth} - ${sd_data.predation_rate} * s['predator']))
model.add_flow('predation', 'prey', 'predator',
              lambda s, t: ${sd_data.predation_rate} * s['prey'] * s['predator'])
model.add_flow('predator_death', None, 'predator',
              lambda s, t: -${sd_data.predator_death} * s['predator'])

results = model.simulate((${sd_data.t_start}, ${sd_data.t_end}), ${sd_data.n_points})
{'stocks': results['stocks'], 'time': results['time']}
    ");

    // 2. Prolog: Causal loop detection and stability analysis
    let prolog_knowledge = build_causal_graph(sd_data);
    let prolog_analysis = perform EmCubed.call_surface("prolog", prolog_knowledge + "
% Causal loop analysis
feedback_loop(Start, Path) :-
    path(Start, Start, Path),
    length(Path, Len),
    Len > 2.

loop_polarity(Loop, Polarity) :-
    findall(P, (member(Edge, Loop), edge(Edge, P)), Polars),
    odd_negative(Polars, NegCount),
    (NegCount mod 2 =:= 1 -> Polarity = negative ; Polarity = positive).

odd_negative([P|Rest], Count) :-
    (P = '-' -> Count1 = 1 ; Count1 = 0),
    odd_negative(Rest, Count1).

% Stability criteria
stable_system(Derivatives) :-
    forall(member(D, Derivatives), abs(D) < 0.01).

% Detect potential equilibria
equilibrium(State) :-
    derivatives(State, Derivatives),
    stable_system(Derivatives).

% Find all feedback loops
find_loops(Paths) :-
    findall(P, feedback_loop(_, P), Paths).

?- find_loops(Loops).
    ");

    // 3. Hy: Fuzzy system classification and regime detection
    let hy_classify = perform EmCubed.call_surface("hy", "
(defn system-regime [prey predator]
  \"Classify system state (stable, oscillating, chaotic)\"
  (let [p-mean (mean prey)
        p-std (numpy.std prey)
        ratio (/ (last predator) (last prey))
        oscillation-score (* (numpy.std prey) (+ p-mean 1))]
    (cond [(< oscillation-score 0.1) :stable]
          [(and (> oscillation-score 0.1) (< oscillation-score 1.0)) :oscillatory]
          [True :chaotic])))

(defn equilibrium-search [trajectory tolerance]
  \"Find approximate equilibrium point in trajectory\"
  (let [velocities (list-comp (- (get trajectory i) (get trajectory (- i 1)))
                              (range 1 (len trajectory)))
        stationary (filter (fn [v] (< (abs v) tolerance)) velocities)]
    (if stationary
      {:found true :point (mean stationary)}
      {:found false :point nil})))

(let [stocks ${py_sim['stocks']}
      prey (stocks 'prey)
      pred (stocks 'predator')]
  {:regime (system-regime prey pred)
   :final_state {:prey (last prey) :predator (last pred)}
   :equilibrium_found ( equilibrium-search prey 0.01)})  ; simplified
    ");

    let regime = hy_classify.get("value", {});
    return {
        "simulation": py_sim,
        "causal_loops": extract_loops(prolog_analysis),
        "regime": regime.get("regime", "unknown"),
        "final_state": regime.get("final_state", {})
    };
}

func build_causal_graph(data: SDInput): String {
    let graph = StringBuilder();
    graph.append("% Causal graph for Lotka-Volterra\n");
    graph.append("edge(prey_growth, prey, '+').\n");  // prey growth increases prey
    graph.append("edge(predation, prey, '-').\n");     // predation decreases prey
    graph.append("edge(predation, predator, '+').\n"); // predation increases predator
    graph.append("edge(predator_death, predator, '-').\n");
    graph.append("\n% Derivatives calculation (simplified)\n");
    graph.append("derivatives(State) :- compute_rates(State, Derivatives).\n");
    return graph.toString();
}

func extract_loops(result: Map): List<String> {
    // Parse Prolog loop detection results
    return result.get("loops", List<String>());
}

struct SDInput {
    initial_prey: Float64;
    initial_predator: Float64;
    prey_growth: Float64;
    predation_rate: Float64;
    predator_death: Float64;
    t_start: Float64;
    t_end: Float64;
    n_points: Int32;
}
