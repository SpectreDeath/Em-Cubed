---
Domain: NLP
Version: 1.0.0
Complexity: Medium
Type: Analysis
Category: Language Skills
Estimated Execution Time: 2-5 minutes
name: sentiment-intelligence-engine
Source: community
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
```

## Testing

```python
# Test sentiment engine
from skills.sentiment_intelligence_engine import SentimentIntelligenceEngine

engine = SentimentIntelligenceEngine()
result = engine.analyze("I love this product! It's amazing.")
assert result.sentiment in ["positive", "negative", "neutral"]
assert 0 <= result.confidence <= 1
```