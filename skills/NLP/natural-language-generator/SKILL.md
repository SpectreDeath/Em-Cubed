---
name: natural-language-generator
domain: "NLP"
description: Skill for natural-language-generator.
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
﻿---
name: natural-language-generator
Domain: NLP
Version: 1.0.0
surfaces:
  - python
  - prolog
  - hy
---

## Purpose

Multi-surface natural language generator using template expansion, Prolog grammatical constraints, and Hy for style transfer.

## Description

Generates text from templates and constraints using pure Python with optional logical and stylistic refinements.

## Implementation

### Python Template Generator

```python
from typing import Dict, List, Optional

def template_fill(template: str, values: Dict[str, str]) -> str:
    """Fill template with values."""
    result = template
    for key, value in values.items():
        result = result.replace("{" + key + "}", value)
    return result

def constrained_generate(prompt: str, constraints: List[str]) -> str:
    """Generate text ensuring it contains all constraints."""
    base = f"Generated response to: {prompt[:40]}..."
    for constraint in constraints:
        if constraint.lower() not in base.lower():
            base += f" {constraint}"
    return base

def generate_multiple_variants(prompt: str, count: int = 3) -> List[str]:
    """Generate multiple text variants."""
    return [f"Variant {i+1}: {prompt} (variant {i+1})" for i in range(count)]
```

### Prolog Grammar Rules

```prolog
% Grammatical structure validation
valid_sentence_structure(Words) :-
    length(Words, Len),
    Len >= 3.

% Style constraints
matches_style(Text, Style) :-
    (Style == "formal" -> contains_no_contractions(Text)) ;
    (Style == "casual" -> contains_casual_words(Text)) ;
    true.

contains_no_contractions(Text) :-
    not(sub_string(Text, "don
t)),
    not(sub_string(Text, cant")).

contains_casual_words(Text) :-
    (sub_string(Text, "cool") ; sub_string(Text, "yeah") ; sub_string(Text, "awesome")).
```

### Hy Style Transfer

```hy
(defn style-features [text]
  "Extract stylistic features from text"
  (let [words (split text " ")
        sentences (split text ".!?")
        avg-word-len (/ (sum (map len words)) (len words))
        complexity-score (/ (len (filter (fn [w] (> (len w) 6)) words)) (len words))]
    {:avg-word-len avg-word-len :complexity complexity-score}))

(defn apply-style [text target-style]
  "Apply basic style transformation"
  (if (= target-style "formal")
    (.replace text " yeah " " indeed ")
    (.replace text " cool " " impressive "))
```

## Testing

### Unit Tests

```python
import pytest

def test_template_fill():
    template = "Hello, {name}!"
    result = template_fill(template, {"name": "World"})
    assert result == "Hello, World!"

def test_constraints():
    constr = ["important", "crucial"]
    result = constrained_generate("test", constr)
    assert "important" in result.lower()
```

## Security Considerations

- No external API calls or network access.
- Pure string manipulation only.
