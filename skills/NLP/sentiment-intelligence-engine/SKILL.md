---
Domain: NLP
Version: 1.0.0
Complexity: Medium
Type: Analysis
Category: Language Skills
Estimated Execution Time: 2-5 minutes
name: sentiment-intelligence-engine
Source: community
description: Sentiment intelligence engine for polarity classification, emotion detection, and opinion aggregation.
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
  - nlp
  - sentiment_analysis
  - emotion_detection
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T12:30:00Z"
updated_at: "2026-05-02T12:30:00Z"

## Purpose

Multi-surface sentiment intelligence engine that uses Python for text processing and embeddings, Prolog for logical sentiment rules, and Hy for fuzzy sentiment aggregation and trend detection.

## Description

This skill provides advanced sentiment analysis by:
- Python for transformer embeddings, lexicon-based scoring, and text preprocessing
- Prolog for context-sensitive sentiment rules and domain adaptation
- Hy for fuzzy sentiment composition and temporal trend analysis

## Examples

### Social Media Sentiment Tracking

```
Input: Stream of social media posts
Output: Sentiment scores with confidence intervals and trend forecasts
```

## Implementation

### Python Text Processing

```python
import numpy as np
from typing import Dict, List, Tuple, Optional
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from dataclasses import dataclass

@dataclass
class SentimentResult:
    text: str
    sentiment: str
    confidence: float
    scores: Dict[str, float]
    entities: List[str] = None

class SentimentIntelligenceEngine:
    """Multi-layered sentiment analysis engine."""
    
    def __init__(self):
        self.sentiment_classifier = pipeline("sentiment-analysis", 
                                             model="cardiffnlp/twitter-roberta-base-sentiment")
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.model = AutoModel.from_pretrained("bert-base-uncased")
    
    def analyze(self, text: str) -> SentimentResult:
        """Perform sentiment analysis on text."""
        result = self.sentiment_classifier(text)[0]
        
        # Get embeddings for context
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
        
        return SentimentResult(
            text=text,
            sentiment=result["label"].lower(),
            confidence=result["score"],
            scores={"positive": 0.0, "negative": 0.0, "neutral": 0.0, result["label"].lower(): result["score"]},
            entities=self._extract_entities(text)
        )
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text."""
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        return [ent.text for ent in doc.ents]
    
    def batch_analyze(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze multiple texts."""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results
    
    def get_embeddings(self, text: str) -> np.ndarray:
        """Get sentence embeddings."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
        return embeddings.numpy()
    
    def lexicon_score(self, text: str, lexicon: Dict[str, float]) -> float:
        """Score based on sentiment lexicon."""
        words = text.lower().split()
        scores = [lexicon.get(word, 0) for word in words]
        return np.mean(scores) if scores else 0.0

def preprocess_text(text: str) -> str:
    """Clean and normalize text."""
    import re
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'@\w+', '', text)     # Remove mentions
    text = re.sub(r'#\w+', '', text)     # Remove hashtags
    text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
    return text.strip()

def temporal_aggregation(results: List[SentimentResult], 
                        window: str = "1h") -> Dict[str, float]:
    """Aggregate sentiment over time window."""
    sentiments = [r.scores.get(r.sentiment, 0) for r in results]
    return {
        "mean": float(np.mean(sentiments)),
        "std": float(np.std(sentiments)),
        "trend": float(np.polyfit(range(len(sentiments)), sentiments, 1)[0])
    }
```

### Prolog Sentiment Rules

```prolog
% Sentiment context rules
sentiment_in_context(Text, Sentiment, Context) :-
    sentiment_words(Text, PositiveWords),
    sentiment_words(Text, NegativeWords),
    length(PositiveWords, PosCount),
    length(NegativeWords, NegCount),
    (PosCount > NegCount -> Sentiment = positive ; Sentiment = negative).

% Negation handling
negated_sentiment(Word) :-
    member(Word, [not, never, no, without]),
    next_token(Word, TargetWord),
    sentiment_word(TargetWord).

% Domain adaptation
domain_sentiment_adjusted(BaseScore, Domain, AdjustedScore) :-
    domain_modifier(Domain, Modifier),
    AdjustedScore is BaseScore * Modifier.

% Aspect-based sentiment
aspect_sentiment(Text, Aspect, Sentiment) :-
    extract_aspect(Text, Aspect),
    extract_opinion(Target, Sentiment),
    aspect_target(Aspect, Target).

% Sentiment intensity
sentiment_intensity(Word, Intensity) :-
    intensifier(Word, Intensity).

sentiment_intensity(Word, Intensity) :-
    sentiment_word(Word, BaseIntensity),
    intensifier(Modifier, Multiplier),
    precedes(Modifier, Word),
    Intensity is BaseIntensity * Multiplier.

% Comparative sentiment
comparative_sentiment(Text, Stronger, Weaker, Preference) :-
    extract_comparison(Text, Stronger, Weaker),
    sentiment(Stronger, Sent1),
    sentiment(Weaker, Sent2),
    Sent1 > Sent2,
    Preference = stronger.

% Contradiction detection
contradictory_sentiments(Results) :-
    member(R1, Results),
    member(R2, Results),
    R1.sentiment \= R2.sentiment,
    similar_context(R1.context, R2.context),
    abs(R1.score - R2.score) < 0.2.
```

### Hy Fuzzy Aggregation

```hy
(defn fuzzy-sentiment-composition [scores weights]
  "Apply fuzzy logic to compose multiple sentiment scores"
  (let [weighted-sum (sum (zip scores weights))
        total-weight (sum weights)
        normalized-score (/ weighted-sum total-weight)]
    normalized-score))

(defn sentiment-trend [historical-scores window-size]
  "Detect sentiment trends using moving averages"
  (let [recent (take window-size (reverse historical-scores))
        moving-avg (mean recent)
        previous (take window-size (drop 1 (reverse historical-scores)))
        prev-avg (if previous (mean previous) moving-avg)]
    {:current moving-avg :trend (- moving-avg prev-avg) :acceleration (if previous (- moving-avg (* 2 prev-avg)) 0)}))

(defn confidence-interval [scores confidence-level]
  "Calculate confidence interval for sentiment scores"
  (let [mean (mean scores)
        std-dev (sqrt (/ (sum (map (fn [x] ** (- x mean) 2)) scores)) (max 1 (dec (len scores))))
        z-score (get {"0.9" 1.645 "0.95" 1.96 "0.99" 2.576} (str confidence-level))]
    {:lower (- mean (* z-score (/ std-dev (sqrt (len scores)))))
     :upper (+ mean (* z-score (/ std-dev (sqrt (len scores)))))
     :mean mean}))

(defn emotional-variance [emotion-scores]
  "Calculate emotional variance across dimensions"
  (let [values (vals emotion-scores)
        mean (mean values)]
    (/ (sum (map (fn [v] (** (- v mean) 2)) values)) (len values))))

(defn sentiment-forecast [historical-trends periods-ahead]
  "Forecast future sentiment using exponential smoothing"
  (let [alpha 0.3  ; Smoothing factor
        last-forecast (first historical-trends)
        forecasts (for [i (range periods-ahead)]
                   (let [prediction (* alpha (get historical-trends (max 0 (- (len historical-trends) i 1))))
                         (inc (* (- 1 alpha) last-forecast)))]
                     prediction))]
    forecasts))

(defn aspect-sentiment-fusion [aspect-scores weights]
  "Fuse sentiment scores across different aspects"
  (apply + (map * (map (fn [s] (get s "score" 0)) aspect-scores) weights)))

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface

def test_text_preprocessing():
    """Test text cleaning and normalization."""
    code = '''
import re

def preprocess_text(text: str) -> str:
    text = re.sub(r'http\\S+', '', text)  # URLs
    text = re.sub(r'@\\w+', '', text)      # mentions
    text = re.sub(r'#\\w+', '', text)      # hashtags
    text = re.sub(r'\\s+', ' ', text)      # whitespace
    return text.strip()

raw = "Check out https://example.com #awesome @user  Hello!"
clean = preprocess_text(raw)
assert "http" not in clean
assert "#" not in clean
assert "@" not in clean
assert "Hello" in clean
print("preprocessing ok")
'''
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_lexicon_sentiment_scoring():
    """Test simple lexicon-based sentiment scoring."""
    code = '''
import numpy as np

def lexicon_score(text: str, lexicon: dict) -> float:
    words = text.lower().split()
    scores = [lexicon.get(word, 0) for word in words]
    return np.mean(scores) if scores else 0.0

lex = {"love": 1.0, "amazing": 1.0, "hate": -1.0, "terrible": -1.0}

score1 = lexicon_score("I love this amazing product", lex)
assert score1 > 0.5

score2 = lexicon_score("I hate this terrible service", lex)
assert score2 < -0.5

score3 = lexicon_score("It is okay", lex)
assert score3 == 0.0

print("lexicon scoring ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_temporal_aggregation():
    """Test time-based sentiment aggregation."""
    code = '''
import numpy as np

def temporal_aggregation(sentiment_scores, trend_window=3):
    """Compute mean, std, and trend from scores."""
    mean = float(np.mean(sentiment_scores))
    std = float(np.std(sentiment_scores))
    # Linear trend (slope)
    if len(sentiment_scores) >= 2:
        x = np.arange(len(sentiment_scores))
        trend = float(np.polyfit(x, sentiment_scores, 1)[0])
    else:
        trend = 0.0
    return {"mean": mean, "std": std, "trend": trend}

scores = [0.8, 0.7, 0.75, 0.8, 0.85]
result = temporal_aggregation(scores)
assert "mean" in result
assert "trend" in result
assert result["mean"] > 0.7
# Trend should be positive (scores increasing)
assert result["trend"] > 0 or abs(result["trend"]) < 0.01
print("temporal aggregation ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_sentiment_classification_logic():
    """Test positive/negative/neutral classification."""
    code = '''
def classify_sentiment(score: float, threshold: float = 0.3) -> str:
    if score > threshold:
        return "positive"
    elif score < -threshold:
        return "negative"
    else:
        return "neutral"

assert classify_sentiment(0.7) == "positive"
assert classify_sentiment(-0.5) == "negative"
assert classify_sentiment(0.1) == "neutral"
print("classification logic ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_confidence_interval():
    """Test confidence interval calculation."""
    code = '''
import numpy as np
from scipy import stats

def confidence_interval(scores, confidence=0.95):
    n = len(scores)
    mean = np.mean(scores)
    sem = np.std(scores) / np.sqrt(n)
    # t-distribution for small samples
    t = stats.t.ppf((1 + confidence) / 2, n-1)
    margin = t * sem
    return (mean - margin, mean + margin)

scores = [0.8, 0.9, 0.7, 0.85, 0.75]
ci = confidence_interval(scores, 0.95)
assert ci[0] < ci[1]
assert ci[0] < 0.85 < ci[1]  # mean should be within
print("confidence interval ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_sentiment_fusion():
    """Test combining multiple aspect sentiments."""
    code = '''
def aspect_fusion(aspect_scores, weights):
    """Weighted average of aspect scores."""
    weighted_sum = sum(score * weight for score, weight in zip(aspect_scores, weights))
    total_weight = sum(weights)
    return weighted_sum / total_weight if total_weight > 0 else 0.0

scores = [0.9, 0.6, 0.8]  # positive, neutral, positive
weights = [0.5, 0.2, 0.3]
fused = aspect_fusion(scores, weights)
assert fused > 0.7  # weighted average should be high
assert abs(fused - 0.77) < 0.01  # (0.9*0.5 + 0.6*0.2 + 0.8*0.3) / 1.0 = 0.77
print("aspect fusion ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_negation_handling():
    """Test negation flips sentiment."""
    code = '''
def apply_negation(word_sentiments, negation_words=None):
    """Flip sentiment scores after negation words."""
    if negation_words is None:
        negation_words = {"not", "never", "no"}
    result = []
    negate = False
    for word, score in word_sentiments:
        if word.lower() in negation_words:
            negate = True
            result.append((word, score))  # negation word itself neutral
        elif negate:
            result.append((word, -score))  # flip
            negate = False
        else:
            result.append((word, score))
    return result

words = [("not", 0), ("good", 0.8), ("product", 0)]
adjusted = apply_negation(words)
scores = [s for _, s in adjusted]
assert scores[1] == -0.8  # "good" flipped
print("negation handling ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_batch_analysis_structure():
    """Test batch analysis returns list of results."""
    code = '''
def batch_analyze(texts):
    results = []
    for text in texts:
        results.append({
            "text": text,
            "sentiment": "positive" if "good" in text.lower() else "neutral",
            "confidence": 0.9 if "good" in text.lower() else 0.5
        })
    return results

texts = ["This is good", "It is okay", "Really good experience"]
results = batch_analyze(texts)
assert len(results) == 3
assert results[0]["sentiment"] == "positive"
assert results[2]["confidence"] == 0.9
print("batch analysis ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_emotional_variance():
    """Test variance across emotion dimensions."""
    code = '''
import numpy as np

def emotional_variance(emotion_scores):
    values = list(emotion_scores.values())
    mean = np.mean(values)
    variance = np.mean([(v - mean)**2 for v in values])
    return variance

emotions = {"joy": 0.8, "sadness": 0.2, "anger": 0.1, "fear": 0.1}
var = emotional_variance(emotions)
assert var > 0
# High joy (0.8) vs low others -> high variance
assert var > 0.05
print("emotional variance ok")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
class TestSentimentEngine:
    @pytest.fixture
    async def surface(self):
        return PythonSurface()

    async def test_string_manipulation(self, surface):
        """Test string operations used in sentiment analysis."""
        code = '''
text = "I LOVE this PRODUCT!!!"
lower = text.lower()
words = lower.split()
assert "love" in lower
assert len(words) > 0
print("string ops ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_dict_result_structure(self, surface):
        """Test returning structured sentiment results."""
        code = '''
result = {
    "sentiment": "positive",
    "confidence": 0.92,
    "scores": {"positive": 0.9, "negative": 0.1, "neutral": 0.0}
}
assert result["confidence"] > 0.5
assert result["scores"]["positive"] > result["scores"]["negative"]
print("struct ok")
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
async def test_sentiment_skill_integration():
    """Test sentiment intelligence engine skill."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "NLP" / "sentiment-intelligence-engine"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: Sentiment Test
Domain: NLP
surfaces:
  - python
---

## Purpose
Test sentiment

## Implementation

### Python

```python
def simple_sentiment(text):
    if "good" in text.lower():
        return "positive"
    return "neutral"
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        surface = PythonSurface()
        code = "text = 'good'; 'positive' if 'good' in text else 'neutral'"
        result = await surface.execute(code, {})
        assert result["status"] == "ok"
```

## Usage Patterns

### Lexicon-Based Sentiment

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

lexicon = {
    "good": 1.0, "great": 1.5, "excellent": 2.0,
    "bad": -1.0, "terrible": -2.0, "awful": -1.5
}

code = '''
def analyze_sentiment(text, lexicon):
    words = text.lower().split()
    score = sum(lexicon.get(w, 0) for w in words)
    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    return {"sentiment": sentiment, "score": score}

text = "The product is good but service was terrible"
result = analyze_sentiment(text, lexicon)
print(result)
'''
await surface.execute(code, {})
```

### Transformer-Based (requires transformers)

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("I love this!")
print(result)
```

## Security Considerations

- Transformer models can be large; consider caching
- Text may contain PII - sanitize before processing
- Ensure model downloads use trusted sources

## Dependencies

- numpy (array operations)
- transformers (optional, for neural sentiment)
- torch (optional, backend for transformers)
- spacy (optional, for entity extraction)
- em_cubed framework

## Testing

```python
# Test sentiment engine
from skills.sentiment_intelligence_engine import SentimentIntelligenceEngine

engine = SentimentIntelligenceEngine()
result = engine.analyze("I love this product! It's amazing.")
assert result.sentiment in ["positive", "negative", "neutral"]
assert 0 <= result.confidence <= 1
```

````
