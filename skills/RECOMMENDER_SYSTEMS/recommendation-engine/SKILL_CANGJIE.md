# Recommendation Engine - Cangjie Edition
# Cangjie-optimized multi-surface recommender

# Cangjie surface block: orchestrator
func main() {
    // Input: user interactions, item features, recommendation params
    let rec_data = context["recommendation_data"] as RecInput;

    println("Cangjie Recommender Starting...");

    // 1. Python: Compute collaborative filtering + content-based scores
    let py_result = perform EmCubed.call_surface("python", "
import numpy as np
from typing import Dict, List, Tuple

def collaborative_filter(interactions, user_id, n=10):
    '''Simplified CF: based on user similarity'''
    if user_id not in interactions:
        return []

    # Build user-item matrix
    all_users = list(interactions.keys())
    all_items = list(set([item for user_items in interactions.values() for item in user_items]))
    user_idx = {u: i for i, u in enumerate(all_users)}
    item_idx = {i: i for i, range(len(all_items))}

    # Simple user-based CF
    target_vector = [1 if item in interactions[user_id] else 0 for item in all_items]
    similarities = {}
    for other_user, other_items in interactions.items():
        if other_user == user_id:
            continue
        other_vector = [1 if item in other_items else 0 for item in all_items]
        similarity = sum(a * b for a, b in zip(target_vector, other_vector))
        similarities[other_user] = similarity

    # Recommend items that similar users liked
    recommendations = {}
    for sim_user, score in sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]:
        for item in interactions[sim_user]:
            if item not in interactions[user_id]:
                recommendations[item] = recommendations.get(item, 0) + score

    return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:n]

interactions = ${rec_data.interactions}
user_id = \"${rec_data.user_id}\"
cf_results = collaborative_filter(interactions, user_id)
{'cf': cf_results, 'user_id': user_id}
    ");

    // 2. Prolog: Validate preference consistency & diversity
    let prolog_prefs = build_preference_facts(rec_data);
    let prolog_check = perform EmCubed.call_surface("prolog", prolog_prefs + "
valid_recommendation(Item, User) :-
    recommended_for(User, Item),
    compatible_with_history(User, Item),
    not contradictory_preference(User, Item).

diverse_recommendations(Recs, MinDiversity) :-
    length(Recs, Len),
    findall(Sim, (member(R1, Recs), member(R2, Recs), R1 \\= R2, item_similarity(R1, R2, Sim)), Sims),
    average(Sims, Avg),
    Avg < (1 - MinDiversity).

?- valid_recommendation(Item, '${rec_data.user_id}').
    ");

    // 3. Hy: Adaptive fuzzy scoring with novelty & diversity
    let hy_score = perform EmCubed.call_surface("hy", "
(defn rec-score [item cf-score user-history global-popularity]
  \"Fuzzy recommendation score\"
  (let [novelty (- 1 (if (in item user-history) 1 0))
        pop-penalty (- 1 (* 0.3 global-popularity))
        relevance (* cf-score 0.7)
        diversity-bonus (* novelty 0.2)]
    (+ (* relevance 0.7) (* pop-penalty 0.1) (* diversity-bonus 0.2))))

(let [cf-results ${py_result['cf']}
      history ${rec_data.user_history}
      pop ${rec_data.global_popularity}]
  (sorted (list-comp [item score cf-results]
                     (let [s (rec-score item score history pop)]
                       [item s]))
          :key second :reverse True))
    ");

    // 4. Final recommendation synthesis
    return {
        "recommendations": hy_score.get("value", []),
        "constraint_violations": extract_violations(prolog_check),
        "base_cf_results": py_result.get("cf", [])
    };
}

func build_preference_facts(data: RecInput): String {
    let facts = StringBuilder();
    facts.append("% User preference history\n");
    for (user, items in data.user_history) {
        for (item in items) {
            facts.append("likes('").append(user).append("', '")
                .append(item).append("').\n");
        }
    }
    facts.append("\n% Item similarities (simplified)\n");
    facts.append("item_similarity(I1, I2, Sim) :- shared_features(I1, I2, Sim).\n");
    return facts.toString();
}

func extract_violations(result: Map): Int32 {
    return result.get("violations", 0);
}

struct RecInput {
    user_id: String;
    interactions: Map<String, List<String>>;
    user_history: List<String>;
    global_popularity: Map<String, Float64>;
    items: List<String>;
}
