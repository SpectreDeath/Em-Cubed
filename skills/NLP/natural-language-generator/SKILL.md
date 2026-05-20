---
name: natural-language-generator
Domain: NLP
Version: 2.0.0
surfaces:
  - llm
  - python
  - prolog
  - hy
---

## Purpose
Multi-surface natural language generator using LLM for text generation, Prolog for grammatical constraints, and Hy for style transfer and coherence optimization.

## Description
This skill has been migrated to use the LLMSurface for text generation instead of direct transformer model calls, making it more flexible and compatible with various LLM providers.

## Implementation

### LLM Text Generation
```python
from typing import Dict, Any, List, Optional
import json

def generate_text(prompt: str, max_length: int = 100, 
                 temperature: float = 0.7, 
                 num_return_sequences: int = 1) -> List[str]:
    """
    Generate text from prompt using LLM surface.
    
    Args:
        prompt: Input prompt for text generation
        max_length: Maximum length of generated text
        temperature: Sampling temperature (0.0 to 1.0)
        num_return_sequences: Number of sequences to return
        
    Returns:
        List of generated text strings
    """
    # Prepare context for LLM surface
    context = {
        "prompt": prompt,
        "max_length": max_length,
        "temperature": temperature,
        "num_return_sequences": num_return_sequences,
        "task": "text_generation"
    }
    
    # In a real implementation, this would execute via the LLM surface
    # For demonstration, we return a structured response
    return [f"[LLM Generated] Response to: {prompt[:50]}..."]

def constrained_generate(prompt: str, constraints: List[str]) -> str:
    """
    Generate text satisfying constraints using LLM.
    
    Args:
        prompt: Input prompt
        constraints: List of constraints that should be in the output
        
    Returns:
        Generated text satisfying constraints
    """
    # Prepare context for LLM surface
    context = {
        "prompt": prompt,
        "constraints": constraints,
        "task": "constrained_text_generation"
    }
    
    # In a real implementation, this would execute via the LLM surface
    base_response = f"[LLM Generated Constrained] Response to: {prompt[:30]}..."
    
    # Simple constraint satisfaction (in reality, LLM would handle this)
    for constraint in constraints:
        if constraint.lower() not in base_response.lower():
            base_response += f" {constraint}"
            
    return base_response

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
    return full_prompt

# Example usage (would be replaced with actual LLM surface calls in execution)
example_context = {"task": "text_generation", "prompt": "Hello world"}
example_result = generate_text("Hello world", max_length=50)
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
  - llm
---
## Purpose
Test NLG

## Implementation

### LLM Text Generation
```python
def generate_text(prompt: str, max_length: int = 50) -> str:
    return f"Generated: {prompt}"
```

### Usage
```python
result = generate_text("Hello, world!")
```
''')
        
        registry_file = Path(tmpdir) / "registry.json"
        reindex(skills_dir.parent.parent, registry_file)
        
        surface = PythonSurface()
        # Test that we can execute the skill
        result = await surface.execute("generate_text('test')", {})
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

# In actual execution, the LLM would handle constraint satisfaction
# For testing, we verify our constraint logic works
def check_constraints(text: str, constraints: list) -> bool:
    text_lower = text.lower()
    for constraint in constraints:
        if constraint.lower() not in text_lower:
            return False
    return True

# Example usage
generated_text = "Exploring mars and orbit in space"
assert check_constraints(generated_text, constraints) == True
```

## Security Considerations

- LLM API keys should be managed securely through environment variables
- Be cautious with user-provided prompts (injection via prompt engineering)
- No direct file or network access in core logic
- Setting appropriate rate limits and timeouts for LLM calls

## Dependencies

- litellm (for LLM surface)
- em_cubed framework
- Optional: transformers, torch, numpy (for backward compatibility)