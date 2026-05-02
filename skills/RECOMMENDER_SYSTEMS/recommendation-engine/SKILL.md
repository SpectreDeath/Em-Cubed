---
Domain: RECOMMENDER_SYSTEMS
Version: 1.0.0
Complexity: High
Type: Prediction
Category: ML Skills
Estimated Execution Time: 5-10 minutes
name: recommendation-engine
Source: community
---
origin: manual
triggers:
  - recommendation
  - collaborative_filtering
  - personalization
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:00:00Z"
updated_at: "2026-05-02T13:00:00Z"

## Purpose

Multi-surface recommendation engine combining Python for collaborative/content filtering, Prolog for logical consistency rules, and Hy for fuzzy preference aggregation.

## Implementation

### Python Recommendation Core

```python
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.sparse import csr_matrix
from sklearn.decomposition import NMF

class CollaborativeFilter:
    """Collaborative filtering recommendation."""
    
    def __init__(self, n_factors: int = 20):
        self.n_factors = n_factors
        self.user_factors = None
        self.item_factors = None
        self.user_map = {}
        self.item_map = {}
    
    def fit(self, interactions: List[Tuple[int, int, float]]) -> None:
        """Fit the model to interaction data."""
        users = list(set(i[0] for i in interactions))
        items = list(set(i[1] for i in interactions))
        self.user_map = {u: i for i, u in enumerate(users)}
        self.item_map = {i: j for j, i in enumerate(items)}
        
        rows = [self.user_map[u] for u, i, r in interactions]
        cols = [self.item_map[i] for u, i, r in interactions]
        data = [r for u, i, r in interactions]
        
        matrix = csr_matrix((data, (rows, cols)), 
                           shape=(len(users), len(items)))
        
        model = NMF(n_components=self.n_factors)
        self.user_factors = model.fit_transform(matrix)
        self.item_factors = model.components_.T
    
    def recommend(self, user_id: int, n: int = 10) -> List[Tuple[int, float]]:
        """Recommend items for user."""
        if user_id not in self.user_map:
            return []
        
        user_idx = self.user_map[user_id]
        scores = self.user_factors[user_idx] @ self.item_factors.T
        top_items = np.argsort(scores)[::-1][:n]
        return [(list(self.item_map.keys())[i], scores[i]) for i in top_items]

def content_based_similarity(user_profile: Dict, item_features: Dict) -> float:
    """Compute content-based similarity."""
    common = set(user_profile.keys()) & set(item_features.keys())
    if not common:
        return 0.0
    return np.dot([user_profile[k] for k in common], 
                  [item_features[k] for k in common])

def hybrid_scoring(collab_score: float, content_score: float, 
                   weights: Tuple[float, float] = (0.6, 0.4)) -> float:
    """Combine collaborative and content scores."""
    return weights[0] * collab_score + weights[1] * content_score
```

### Prolog Preference Logic

```prolog
% Preference consistency
consistent_preferences(Preferences) :-
    \+ contradictory_preferences(Preferences).

contradictory_preferences(Preferences) :-
    member(pref(User, Item1, Like), Preferences),
    member(pref(User, Item2, Dislike), Preferences),
    similar_items(Item1, Item2),
    different_sentiments(Like, Dislike).

% Recommendation validity
valid_recommendation(User, Item, History) :-
    compatible_with_history(User, Item, History),
    no_conflict_with_preferences(User, Item),
    meets_constraints(User, Item).

% Diversity in recommendations
recommendations_diverse(Recommendations, MinDiversity) :-
    findall(Similarity, 
            (member(Rec1, Recommendations), 
             member(Rec2, Recommendations),
             Rec1 \= Rec2,
             item_similarity(Rec1, Rec2, Similarity)), Similarities),
    average(Similarities, AvgSimilarity),
    AvgSimilarity < MinDiversity.
```

### Hy Fuzzy Aggregation

```hy
(defn preference-weighting [user-history item-features time-decay]
  "Weight preferences with temporal decay"
  (let [recency-scores (map (fn [item]
                             (let [age (get item "age" 0)]
                               (exp (* -0.1 age))))
                           user-history)
        feature-importance (normalize (map (fn [f] (get f "importance" 1.0)) item-features))
        combined (/ (+ (sum recency-scores) (sum feature-importance)) 2)]
    combined))

(defn novelty-score [item user-history global-popularity]
  "Calculate novelty score for exploration"
  (let [pop-score (get global-popularity item 0.5)
        known-score (if (in item user-history) 1.0 0.0)]
    (- 1 pop-score known-score)))

(defn serendipity-measure [recommended-items user-profile expected-items]
  "Measure unexpected but relevant recommendations"
  (let [unexpected (filter (fn [r] (not (in r expected-items))) recommended-items)
        relevant-unexpected (filter (fn [r] (> (similarity r user-profile) 0.7)) unexpected)]
    (/ (len relevant-unexpected) (max 1 (len recommended-items)))))
```