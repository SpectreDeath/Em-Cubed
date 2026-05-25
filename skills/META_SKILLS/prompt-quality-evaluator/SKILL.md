---
name: prompt-quality-evaluator
Domain: META_SKILLS
Version: 1.0.0
surfaces:
  - python
  - hy
---
## Purpose

Evaluate and score the quality of prompts for AI systems based on clarity, specificity, and effectiveness criteria.

## Description

This skill provides systematic evaluation of AI prompts using multiple dimensions:
- Clarity and unambiguity
- Specificity and detail level  
- Context provision and framing
- Expected output format specification
- Constraint and guideline inclusion

## Examples

### Basic Evaluation

```python
# Evaluate a simple prompt
result = evaluator.evaluate_prompt("Write a story about a cat")
# Returns scores for clarity, specificity, etc.

# Compare multiple prompts
results = evaluator.compare_prompts([
    "Explain quantum physics",
    "Explain quantum physics to a high school student using analogies",
    "What is quantum physics?"
])
```

### Detailed Scoring

```python
# Get detailed breakdown
detailed = evaluator.detailed_evaluation(
    "Write a Python function to calculate factorial",
    criteria=["clarity", "specificity", "actionability"]
)
```

## Implementation

### Python Surface
Provides the main evaluation logic, scoring algorithms, and result aggregation.

### Hy Surface
Offers functional programming utilities for processing evaluation metrics and generating insights.

## Security Considerations

- Input sanitization to prevent prompt injection attacks
- Sandboxed execution for all surfaces
- Rate limiting to prevent abuse of evaluation API

## Dependencies

- Python 3.11+
- Hy language
- Em-Cubed framework

## Performance Characteristics

- Fast evaluation for simple prompts (<100ms)
- Scales with prompt complexity and number of criteria
- Batch evaluation available for multiple prompts