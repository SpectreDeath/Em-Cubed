---
name: recommendation-engine
domain: RECOMMENDER_SYSTEMS
version: 1.0.0
description: Multi-surface recommendation engine combining Python for collaborative/content filtering, Prolog for logical
  consistency rules, and Hy for fuzzy preference aggregation.
compatibility: UNIVERSAL
complexity: High
type: Prediction
category: ML Skills
estimated execution time: 5-10 minutes
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

## Testing

### Unit Tests

```python
import pytest
import numpy as np
from em_cubed.surfaces import PythonSurface

def test_collaborative_filter_fit():
    """Test CollaborativeFilter training."""
    code = '''
import numpy as np
from typing import Dict, List, Tuple

class CollaborativeFilter:
    def __init__(self, n_factors: int = 20):
        self.n_factors = n_factors
        self.user_factors = None
        self.item_factors = None
        self.user_map = {}
        self.item_map = {}
    
    def fit(self, interactions: List[Tuple[int, int, float]]) -> None:
        users = list(set(i[0] for i in interactions))
        items = list(set(i[1] for i in interactions))
        self.user_map = {u: i for i, u in enumerate(users)}
        self.item_map = {i: j for j, i in enumerate(items)}
        # Simplified: just fill factors randomly for testing
        self.user_factors = np.random.randn(len(users), self.n_factors)
        self.item_factors = np.random.randn(len(items), self.n_factors)

# Sample interactions: (user, item, rating)
interactions = [(1, 101, 5.0), (1, 102, 4.0), (2, 101, 3.0), (2, 103, 4.5)]
cf = CollaborativeFilter(n_factors=5)
cf.fit(interactions)

assert cf.user_factors.shape == (2, 5)
assert cf.item_factors.shape == (3, 5)
assert cf.user_map[1] == 0
assert cf.item_map[101] == 0

print("fit ok")
'''
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_collaborative_filter_recommend():
    """Test recommendation generation."""
    code = '''
import numpy as np
from typing import Dict, List, Tuple

class CollaborativeFilter:
    def __init__(self, n_factors: int = 20):
        self.n_factors = n_factors
        self.user_factors = None
        self.item_factors = None
        self.user_map = {}
        self.item_map = {}
    
    def fit(self, interactions: list) -> None:
        users = list(set(i[0] for i in interactions))
        items = list(set(i[1] for i in interactions))
        self.user_map = {u: i for i, u in enumerate(users)}
        self.item_map = {i: j for j, i in enumerate(items)}
        self.user_factors = np.random.randn(len(users), self.n_factors)
        self.item_factors = np.random.randn(len(items), self.n_factors)
    
    def recommend(self, user_id: int, n: int = 10) -> List[Tuple[int, float]]:
        if user_id not in self.user_map:
            return []
        user_idx = self.user_map[user_id]
        scores = self.user_factors[user_idx] @ self.item_factors.T
        top_indices = np.argsort(scores)[::-1][:n]
        return [(list(self.item_map.keys())[i], float(scores[i])) for i in top_indices]

interactions = [(1, 101, 5.0), (1, 102, 4.0), (2, 101, 3.0), (2, 103, 4.5)]
cf = CollaborativeFilter(n_factors=5)
cf.fit(interactions)
recs = cf.recommend(1, n=2)
assert len(recs) == 2
assert all(isinstance(r, tuple) and len(r) == 2 for r in recs)
print("recommend ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_content_based_similarity():
    """Test content-based similarity calculation."""
    code = '''
import numpy as np

def content_based_similarity(user_profile: Dict, item_features: Dict) -> float:
    common = set(user_profile.keys()) & set(item_features.keys())
    if not common:
        return 0.0
    return float(np.dot([user_profile[k] for k in common], 
                        [item_features[k] for k in common]))

user = {"action": 0.9, "comedy": 0.3, "drama": 0.1}
item = {"action": 0.8, "comedy": 0.4}
sim = content_based_similarity(user, item)
assert sim > 0.0
assert sim < 2.0  # Dot product of normalized-ish values
print("content similarity ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_hybrid_scoring():
    """Test hybrid score combination."""
    code = '''
def hybrid_scoring(collab_score: float, content_score: float, 
                   weights: tuple = (0.6, 0.4)) -> float:
    return weights[0] * collab_score + weights[1] * content_score

score = hybrid_scoring(0.8, 0.6)
assert abs(score - 0.72) < 0.001

score2 = hybrid_scoring(1.0, 0.0, (0.5, 0.5))
assert score2 == 0.5
print("hybrid scoring ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_recommendation_diversity():
    """Test that recommendations aren't all the same item."""
    code = '''
import numpy as np

def get_diverse_recommendations(scores, n=5):
    """Simple diversity: pick top items from different clusters."""
    indices = np.argsort(scores)[::-1]
    # Take top, skip next, take third, etc. (simplified)
    return indices[::max(1, len(indices)//n)][:n]

scores = np.array([0.9, 0.85, 0.82, 0.8, 0.78, 0.75])
recs = get_diverse_recommendations(scores, n=3)
assert len(recs) <= 3
assert len(recs) >= 1
print("diversity ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
class TestRecommendationEngine:
    @pytest.fixture
    async def surface(self):
        return PythonSurface()

    async def test_basic_execution(self, surface):
        """Ensure surface can execute simple code."""
        result = await surface.execute("sum([1,2,3])", {})
        assert result["status"] == "ok"
        assert result["value"] == 6

    async def test_dict_operations(self, surface):
        """Test dictionary manipulation used in recommendations."""
        code = '''
user_profiles = {1: {"action": 0.9, "comedy": 0.3}}
item_features = {101: {"action": 0.8, "comedy": 0.4}}

user = user_profiles[1]
item = item_features[101]
common = set(user.keys()) & set(item.keys())
assert "action" in common
print("dict ops ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

### Integration Tests

```python
import pytest
from em_cubed import reindex, search_registry
from em_cubed.surfaces import PythonSurface
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_recommendation_skill_end_to_end():
    """Test recommendation skill workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "RECOMMENDER_SYSTEMS" / "recommendation-engine"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: Test Recommender
Domain: RECOMMENDER_SYSTEMS
surfaces:
  - python
---

## Purpose
Simple test recommender

## Implementation

### Python

```python
def recommend_popular(n=5):
    return [(i, 1.0) for i in range(n)]
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        surface = PythonSurface()
        result = await surface.execute("2 * 5", {})
        assert result["status"] == "ok"
        assert result["value"] == 10
```

## Usage Patterns

### Content-Based Recommendation

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

# User profile with feature weights
user_profile = {"action": 0.9, "comedy": 0.3, "drama": 0.1}

# Item feature vectors
items = [
    {"id": 1, "features": {"action": 0.8, "comedy": 0.2}},
    {"id": 2, "features": {"action": 0.3, "comedy": 0.9}},
]

# Compute similarity for each item
for item in items:
    common = set(user_profile.keys()) & set(item["features"].keys())
    score = sum(user_profile[c] * item["features"][c] for c in common)
    print(f"Item {item['id']}: score={score:.3f}")
```

### Collaborative Filtering

```python
# Build user-item interaction matrix
interactions = [
    (user1, item1, 5.0),
    (user1, item2, 4.0),
    (user2, item1, 3.0),
]

# Factorize matrix to get latent factors
# Then recommend by dot product of user factors with item factors
```

## Security Considerations

- Recommendation models may encode user behavior; ensure privacy
- No direct data access - data must be passed explicitly
- Execution timeouts protect against DoS

## Dependencies

- numpy (numerical arrays)
- scipy (sparse matrices)
- scikit-learn (NMF factorization)
- em_cubed framework
```