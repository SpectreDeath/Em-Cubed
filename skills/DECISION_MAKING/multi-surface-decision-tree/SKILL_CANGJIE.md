# Multi-Surface Decision Tree - Cangjie Edition
# Cangjie-optimized orchestration for decision analysis

# Cangjie surface block: orchestrator
func main() {
    // Input: options with criteria scores, weights, constraints
    let decision_data = context["decision_data"] as DecisionInput;

    println("Cangjie Decision Orchestrator Starting...");

    // 1. Python: Compute weighted scores efficiently
    let py_scores = perform EmCubed.call_surface("python", "
import numpy as np

def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)

options = ${decision_data.options}
weights = ${decision_data.weights}

# Extract all numeric values per criterion
criteria = list(weights.keys())
scores = {}
for opt in options:
    name = opt['name']
    scores[name] = 0.0
    for crit in criteria:
        val = opt.get(crit, 0)
        # Simple min-max normalization
        all_vals = [o.get(crit, 0) for o in options]
        norm = normalize(val, min(all_vals), max(all_vals))
        scores[name] += weights[crit] * norm

{scores}
    ");

    // 2. Prolog: Validate constraints and dominance
    let prolog_rules = build_prolog_constraints(decision_data);
    let prolog_check = perform EmCubed.call_surface("prolog", prolog_rules);

    // 3. Hy: Fuzzy multi-criteria scoring with uncertainty
    let hy_fuzzy = perform EmCubed.call_surface("hy", "
(defn fuzzy-membership [value low medium high]
  (cond [(and (>= value low) (< value medium))
         (/ (- value low) (- medium low))]
        [(and (>= value medium) (<= value high))
         (/ (- high value) (- high medium))]
        [true 0.0]))

(defn score-option [option-criteria weights]
  (let [normalized (list-comp (fuzzy-membership s 0.0 0.5 1.0) [s option-criteria]]
    (/ (sum (map * normalized weights)) (sum weights))))

; Score each option
(def scores ${py_scores})
(def weights ${decision_data.weights})
(sorted scores :key second :reverse True)
    ");

    // 4. Synthesize final ranking
    return {
        "ranked_options": hy_fuzzy.get("value", []),
        "constraint_violations": count_violations(prolog_check),
        "raw_scores": py_scores["value"]
    };
}

func build_prolog_constraints(data: DecisionInput): String {
    let prolog = StringBuilder();
    prolog.append("% Option constraints\n");
    prolog.append("valid_option(Option) :-\n");
    for (i, criterion in enumerate(data.criteria)) {
        let threshold = data.thresholds.get(criterion, 0.5);
        prolog.append("    option_score(Option, ").append(criterion).append(", Score),\n");
        prolog.append("    Score >= ").append(threshold).append(".");
        if (i < data.criteria.size() - 1) { prolog.append("\n"); }
    }
    prolog.append("\n\n");
    prolog.append("% Pareto dominance\n");
    prolog.append("pareto_optimal(Option, All) :-\n");
    prolog.append("    member(Option, All),\n");
    prolog.append("    not((member(Other, All), dominates(Other, Option))).\n");
    return prolog.toString();
}

func count_violations(prolog_result: Map): Int32 {
    // Parse Prolog result for constraint violations
    let status = prolog_result.get("status", "error");
    if (status == "ok") {
        return 0;
    }
    return 1; // Simplified
}

struct DecisionInput {
    options: List<DecisionOption>;
    criteria: List<String>;
    weights: Map<String, Float64>;
    thresholds: Map<String, Float64>;
}

struct DecisionOption {
    name: String;
    scores: Map<String, Float64>;
}
