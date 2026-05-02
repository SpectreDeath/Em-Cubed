---
Domain: NLP
Version: 1.0.0
Complexity: Medium
Type: Generation
Category: Language Skills
Estimated Execution Time: 2-5 minutes
name: natural-language-generator
Source: community
---
origin: manual
triggers:
  - text_generation
  - nlp
  - content_creation
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-02T13:00:00Z"
updated_at: "2026-05-02T13:00:00Z"

## Purpose

Multi-surface natural language generator using Python for neural text generation, Prolog for grammatical constraints, and Hy for style transfer and coherence optimization.

## Implementation

### Python Text Generation

```python
import numpy as np
from typing import List, Dict, Optional, Tuple
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import torch

class TextGenerator:
    """Neural text generation with constraints."""
    
    def __init__(self, model_name: str = "gpt2"):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.generator = pipeline("text-generation", model=model_name)
    
    def generate(self, prompt: str, max_length: int = 100, 
                 temperature: float = 0.7, 
                 num_return_sequences: int = 1) -> List[str]:
        """Generate text from prompt."""
        outputs = self.generator(prompt, 
                                max_length=max_length,
                                temperature=temperature,
                                num_return_sequences=num_return_sequences)
        return [o["generated_text"] for o in outputs]
    
    def constrained_generate(self, prompt: str, constraints: List[str]) -> str:
        """Generate text satisfying constraints."""
        output = self.generator(prompt, max_length=200)[0]["generated_text"]
        for constraint in constraints:
            if constraint.lower() not in output.lower():
                output += f" {constraint}"
        return output

def template_fill(template: str, values: Dict[str, str]) -> str:
    """Fill template with values."""
    result = template
    for key, value in values.items():
        result = result.replace(f"{{{key}}}", value)
    return result

def conditional_generation(prompt: str, conditions: Dict[str, any]) -> str:
    """Generate conditional text."""
    condition_str = " ".join(f"{k}={v}" for k, v in conditions.items())
    full_prompt = f"{prompt} [{condition_str}]"
    return pipeline("text-generation")(full_prompt, max_length=100)[0]["generated_text"]
```

### Prolog Grammar Rules

```prolog
% Grammatical correctness
valid_sentence(Sentence) :-
    sentence_structure(Sentence, Structure),
    grammatical_structure(Structure).

% Style constraints
matches_style(Text, Style) :-
    complexity_matches(Style, Text, Target),
    sentiment_matches(Style, Text, Sentiment).

% Coherence constraints
coherent_text(Text, Context) :-
    no_contradictions(Text, Context),
    logical_flow(Text).

valid_transformation(Original, Transformed) :-
    preserves_meaning(Original, Transformed),
    improves_clarity(Original, Transformed).
```

### Hy Style Transfer

```hy
(defn style-features [text]
  "Extract stylistic features"
  (let [word-count (len (split text " "))
        sentence-count (len (re.findall r"[.!?]+" text))
        avg-sentence-len (/ word-count sentence-count)
        complex-words (len (filter (fn [w] (> (len w) 6)) (split text " ")))]
    {:avg-sentence-len avg-sentence-len :complex-ratio (/ complex-words word-count)}))

(defn rewrite-coherence [text coherence-target]
  "Improve coherence through rewriting"
  (let [sentences (split text "[.!?]")
        coherence-scores (map sentence-coherence sentences)
        improved-sentences (map (fn [s c] (if (< c coherence-target) (improve-sentence s) s)) sentences coherence-scores)]
    (join ". " improved-sentences)))

(defn tone-adjustment [text target-tone]
  "Adjust text tone"
  (let [current-tone (detect-tone text)
        adjustments (tone-mapping target-tone current-tone)]
    (apply-adjustments text adjustments)))
```