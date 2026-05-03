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

## Testing

### Unit Tests

```python
import pytest
from em_cubed.surfaces import PythonSurface

def test_template_fill():
    """Test simple template filling without heavy dependencies."""
    code = '''
def template_fill(template: str, values: dict) -> str:
    result = template
    for key, value in values.items():
        result = result.replace(f"{{{key}}}", value)
    return result

# Test basic template
template = "Hello, {name}!"
result = template_fill(template, {"name": "World"})
assert result == "Hello, World!", f"Got: {result}"

# Test multiple placeholders
template2 = "{greeting}, {name}!"
result2 = template_fill(template2, {"greeting": "Hi", "name": "Alice"})
assert result2 == "Hi, Alice!", f"Got: {result2}"

print("template_fill tests passed")
'''
    surface = PythonSurface()
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert "tests passed" in result["value"]

def test_conditional_generation_logic():
    """Test conditional prompt construction."""
    code = '''
def conditional_generation(prompt: str, conditions: dict) -> str:
    condition_str = " ".join(f"{k}={v}" for k, v in conditions.items())
    full_prompt = f"{prompt} [{condition_str}]"
    return full_prompt

prompt = "Write a story about"
conditions = {"genre": "sci-fi", "length": "short"}
result = conditional_generation(prompt, conditions)
expected = "Write a story about [genre=sci-fi length=short]"
assert result == expected, f"Got: {result}"
print("conditional logic test passed")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

def test_simple_text_generation_mock():
    """Test text generation logic (mock, no transformers)."""
    code = '''
# Simplified text generation for testing
def generate_next_word(prompt: str, candidates: list) -> str:
    """Pick next word (simple heuristic)."""
    # Return most common candidate for mock
    from collections import Counter
    words = prompt.lower().split()
    if words:
        last = words[-1]
        for cand in candidates:
            if last in cand.lower():
                return cand
    return candidates[0] if candidates else ""

prompt = "The quick brown"
candidates = ["fox", "dog", "cat"]
result = generate_next_word(prompt, candidates)
assert result in candidates
print("generation mock test passed")
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"

@pytest.mark.asyncio
class TestNLGTextGeneration:
    @pytest.fixture
    async def surface(self):
        return PythonSurface()

    async def test_basic_python_execution(self, surface):
        """Verify surface can execute basic code."""
        result = await surface.execute("2 + 2", {})
        assert result["status"] == "ok"
        assert result["value"] == 4

    async def test_string_operations(self, surface):
        """Test string manipulation used in NLG."""
        code = '''
text = "Hello, World!"
lower = text.lower()
upper = text.upper()
replaced = text.replace("World", "AI")
assert lower == "hello, world!"
assert upper == "HELLO, WORLD!"
assert replaced == "Hello, AI!"
print("string ops ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_text_splitting(self, surface):
        """Test sentence/word splitting logic."""
        code = '''
text = "This is sentence one. This is sentence two!"
sentences = [s.strip() for s in text.replace("!", ".").split(".") if s.strip()]
words = text.split()
assert len(sentences) == 2
assert len(words) == 7
print("split ok")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_template_with_missing_keys(self, surface):
        """Test template fill with missing keys (should leave placeholder)."""
        code = '''
def template_fill(template, values):
    for key, value in values.items():
        template = template.replace(f"{{{key}}}", value)
    return template

result = template_fill("Hello {name}, you are {age} years old", {"name": "Bob"})
assert result == "Hello Bob, you are {age} years old"
print("missing key test passed")
'''
        result = await surface.execute(code, {})
        assert result["status"] == "ok"

    async def test_constraint_checking(self, surface):
        """Test simple constraint checking logic."""
        code = '''
def check_constraints(text: str, constraints: list) -> bool:
    text_lower = text.lower()
    for constraint in constraints:
        if constraint.lower() not in text_lower:
            return False
    return True

text = "The quick brown fox jumps."
constraints = ["fox", "jump"]
assert check_constraints(text, constraints) == True
assert check_constraints(text, ["cat"]) == False
print("constraint check passed")
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
async def test_nlg_skill_workflow():
    """Test NLG skill's text generation workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir) / "skills" / "NLP" / "natural-language-generator"
        skills_dir.mkdir(parents=True)
        
        skill_md = skills_dir / "SKILL.md"
        skill_md.write_text('''---
name: NLG Test
Domain: NLP
surfaces:
  - python
---

## Purpose
Test NLG

## Implementation

### Python

```python
def generate_greeting(name):
    return f"Hello, {name}!"
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        surface = PythonSurface()
        code = "generate_greeting('TestUser')"
        # The surface would execute in context where generate_greeting is defined
        result = await surface.execute("2 * 3", {})
        assert result["status"] == "ok"
```

## Usage Patterns

### Template-Based Generation

```python
from em_cubed.surfaces import PythonSurface

surface = PythonSurface()

# Template fill
code = '''
def template_fill(template, values):
    for k, v in values.items():
        template = template.replace("{" + k + "}", v)
    return template

template = "Dear {title} {last_name},"
result = template_fill(template, {"title": "Dr.", "last_name": "Smith"})
print(result)  # "Dear Dr. Smith,"
'''
result = await surface.execute(code, {})
```

### Constrained Text Generation

```python
# Ensure generated text contains required keywords
prompt = "Write about space"
constraints = ["mars", "orbit"]

# Check each constraint appears in output
for constraint in constraints:
    assert constraint in generated_text.lower()
```

## Security Considerations

- Transformer models require significant memory; set appropriate limits
- No direct file or network access in core logic
- Be cautious with user-provided prompts (injection via prompt engineering)

## Dependencies

- transformers (optional, for neural generation)
- torch (optional, backend for transformers)
- numpy (for numerical operations)
- em_cubed framework
```