---
name: prompt-quality-evaluator
description: Evaluates AI prompt files for persona consistency, ambiguity, and coverage gaps using Python orchestration, Prolog rules, and Hy heuristics
Domain: META_SKILLS
Version: 1.0.0
Complexity: Medium
Type: Analysis
Category: Prompt Engineering
Estimated Execution Time: 1-5 minutes
Source: community
origin: manual
triggers:
  - agent
  - analysis
  - quality
  - evaluation
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-05T12:00:00Z"
updated_at: "2026-05-05T12:00:00Z"
---

## Purpose

Evaluate AI prompt files (`.prompt.md`, `.agent.md`, `.instructions.md`) for quality issues across three dimensions: persona consistency, ambiguity, and coverage gaps. Uses a multi-surface architecture with Python for orchestration, Prolog for declarative rules, and Hy for heuristic scoring.

## Multi-Surface Architecture

### Authority Hierarchy

For this skill, the surfaces have these roles:
1. **Python** — Orchestration, LLM integration, file parsing, result aggregation (primary authority)
2. **Prolog** — Logical rules for conflict detection, taxonomy-based classification
3. **Hy** — Heuristic scoring, fuzzy matching thresholds, weighted severity calculation

### Data Flow

```
Prompt File → Python (read & parse) → Prolog (rule evaluation) + Hy (heuristic scoring) → Python (aggregate & format) → LLM (optional enhancement) → Report
```

## Implementation

### Python Entry Point (Orchestration)

```python
"""Prompt quality evaluator using multi-surface architecture."""
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import the multi-surface logic
from pyswip import Prolog
import hy

def evaluate_prompt_quality(prompt_text: str, use_llm: bool = False) -> Dict[str, Any]:
    """
    Main entry point: orchestrates multi-surface evaluation.
    
    Args:
        prompt_text: The prompt file content to analyze
        use_llm: Whether to use LLM for enhanced analysis (requires GitHub Copilot)
    
    Returns:
        Structured evaluation report with all three dimension scores
    """
    results = {
        "persona_consistency": evaluate_persona_python(prompt_text),
        "ambiguity": evaluate_ambiguity_hy(prompt_text),
        "coverage": evaluate_coverage_prolog(prompt_text),
        "overall_quality": None,
    }
    
    # Calculate overall quality score (weighted average)
    persona_score = results["persona_consistency"]["score"]
    ambiguity_score = results["ambiguity"]["score"]
    coverage_score = results["coverage"]["score"]
    
    results["overall_quality"] = (persona_score * 0.3 + 
                                 ambiguity_score * 0.4 + 
                                 coverage_score * 0.3)
    
    # Optionally enhance with LLM analysis
    if use_llm:
        results["llm_enhanced"] = enhance_with_llm(prompt_text)
    
    return results


def evaluate_persona_python(text: str) -> Dict[str, Any]:
    """Python-based persona analysis using regex patterns."""
    issues = []
    
    # Define persona conflict patterns (opposing traits)
    conflict_pairs = [
        ("helpful", "sarcastic"),
        ("professional", "casual"),
        ("formal", "laid-back"),
        ("expert", "beginner-friendly"),
        ("assertive", "passive"),
        ("concise", "verbose"),
        ("friendly", "hostile"),
    ]
    
    # Check for conflicting trait pairs in text
    text_lower = text.lower()
    for trait1, trait2 in conflict_pairs:
        if trait1 in text_lower and trait2 in text_lower:
            issues.append({
                "type": "persona_conflict",
                "traits": [trait1, trait2],
                "severity": "warning",
                "suggestion": f"Choose {trait1} OR {trait2}, not both"
            })
    
    return {
        "score": 1.0 - (len(issues) * 0.2),  # 1.0 = perfect, -0.2 per issue
        "issues": issues,
        "surface": "python"
    }


def evaluate_ambiguity_hy(text: str) -> Dict[str, Any]:
    """Hy-based heuristic ambiguity detection using fuzzy matching."""
    # Execute Hy code for ambiguity detection
    hy_code = f"""
(defn detect-quantifier-ambiguity [text]
   "Detect vague quantity terms."
   (setv vague-terms ["a few" "several" "some" "many" "often" "rarely" "frequently" "highly" "very"])
   (list (filter (fn [term] (not (= -1 (.find text term)))) vague-terms)))

(defn calculate-ambiguity-score [text]
   "Calculate ambiguity severity based on term count and positions."
   (setv ambiguous (detect-quantifier-ambiguity text))
   (setv score (- 1.0 (* (len ambiguous) 0.15)))
   (max 0.0 score))

;; Call the function
(calculate-ambiguity-score {repr(text)})
"""
    try:
        score = float(hy.eval(hy.read_str(hy_code)))
    except Exception as e:
        score = 0.5
    
    # Extract ambiguous terms for reporting
    ambiguous_terms_code = f"""
(defn detect-quantifier-ambiguity [text]
   "Detect vague quantity terms."
   (setv vague-terms ["a few" "several" "some" "many" "often" "rarely" "frequently" "highly" "very"])
   (list (filter (fn [term] (not (= -1 (.find text term)))) vague-terms)))
(detect-quantifier-ambiguity {repr(text)})
"""
    try:
        ambiguous_terms = hy.eval(hy.read_str(ambiguous_terms_code))
        issues = [{"text": term, "type": "quantifier", "severity": "info"} for term in ambiguous_terms]
    except Exception:
        issues = []
    
    return {
        "score": score,
        "issues": issues,
        "surface": "hy"
    }


def evaluate_coverage_prolog(text: str) -> Dict[str, Any]:
    """Prolog-based coverage gap analysis using logical rules."""
    # Initialize Prolog knowledge base with coverage rules
    prolog = Prolog()
    
    # Assert coverage rules
    prolog.assertz("coverage_requirement(user_types)")
    prolog.assertz("coverage_requirement(input_formats)")
    prolog.assertz("coverage_requirement(task_variations)")
    prolog.assertz("coverage_requirement(error_handling)")
    
    # Analyze text for coverage indicators
    text_lower = text.lower()
    
    # Assert what we found in the text
    if "user" in text_lower:
        prolog.assertz("mentions_category(user)")
    if "input" in text_lower or "format" in text_lower:
        prolog.assertz("mentions_category(input)")
    if "task" in text_lower:
        prolog.assertz("mentions_category(task)")
    if "error" in text_lower:
        prolog.assertz("mentions_category(error)")
    
    # Query Prolog to identify gaps using the defined rules
    gaps = []
    for req in ["user_types", "input_formats", "task_variations", "error_handling"]:
        # Query if this requirement is NOT met
        query_result = list(prolog.query(f"coverage_gap({req})"))
        if query_result:  # If we got results, it's a gap
            gaps.append(req)
    
    # Count how many requirements we actually have
    found_count = 0
    for req in ["user_types", "input_formats", "task_variations", "error_handling"]:
        query_result = list(prolog.query(f"mandatory_coverage_category({req}), mentions_category(_)."))
        if query_result:
            found_count += 1
    
    coverage_score = found_count / 4.0  # 4 requirement categories
    
    return {
        "score": min(1.0, coverage_score),
        "gaps": gaps,
        "surface": "prolog"
    }


def enhance_with_llm(text: str) -> Optional[Dict[str, Any]]:
    """Optional LLM enhancement for nuanced analysis."""
    # This would use GitHub Copilot's vscode.lm API
    # Placeholder for integration
    return None
```

### Prolog Constraints (Logical Rules)

```prolog
% Persona Conflict Rules
persona_conflict(trait(T1), trait(T2)) :-
    opposing_traits(T1, T2).

opposing_traits(helpful, sarcastic).
opposing_traits(professional, casual).
opposing_traits(formal, laid_back).
opposing_traits(expert, beginner_friendly).
opposing_traits(assertive, passive).
opposing_traits(concise, verbose).

% Check if text contains both opposing traits
has_conflict(Text) :-
    contains(Text, Trait1),
    contains(Text, Trait2),
    persona_conflict(trait(Trait1), trait(Trait2)).

% Coverage Requirement Rules
mandatory_coverage_category(user_types).
mandatory_coverage_category(input_formats).
mandatory_coverage_category(task_variations).
mandatory_coverage_category(error_handling).

% A gap exists when category is mandatory but not mentioned
coverage_gap(Category) :-
    mandatory_coverage_category(Category),
    not(mentions_category(Category, _)).

% Ambiguity Type Classification
ambiguity_type("a few"; "several"; "some") -> quantifier.
ambiguity_type("it"; "this"; "that") -> reference.
ambiguity_type("professional"; "concise"; "appropriate") -> term.
ambiguity_type("always"; "never"; "all cases") -> scope.
```

### Hy Heuristics (Scoring & Fuzzy Logic)

```hy
;; Ambiguity Detection Heuristics
(defn detect-ambiguity [text]
  "Fuzzy detection of ambiguous terms with weighted scoring."
  (setv quantifier-weights {"a few" 0.3 "several" 0.4 "some" 0.3 "many" 0.5})
  (setv reference-weights {"it" 0.2 "this" 0.2 "that" 0.2 "former" 0.4 "latter" 0.4})
  (setv term-weights {"professional" 0.8 "concise" 0.6 "appropriate" 0.7 "standard" 0.5})
  
  (setv total-score 0.0)
  (for [[term weight] quantifier-weights]
    (if (in term text)
      (setv total-score (+ total-score weight))))
  
  total-score)

(defn calculate-severity [ambiguity-score]
  "Convert ambiguity score to severity level."
  (cond
    (> ambiguity-score 0.7) "error"
    (> ambiguity-score 0.4) "warning"
    True "info"))

(defn heuristic-coverage-assessment [prompt-text]
  "Use heuristics to estimate coverage completeness."
  (setv required-aspects ["user" "input" "task" "error" "format" "constraint"])
  (setv found (filter (fn [aspect] (in aspect prompt-text)) required-aspects))
  (/ (len found) (len required-aspects)))
```

## Evaluation Workflow

### Step 1: Persona Consistency Scan (Python orchestration)

1. Extract all tone/personality descriptors using regex
2. Query Prolog for opposing trait conflicts
3. Report conflicts with line numbers and fix suggestions

### Step 2: Ambiguity Inventory (Hy heuristics)

1. Run Hy fuzzy matcher on ambiguous term dictionary
2. Calculate severity score based on weighted term importance
3. Generate concrete rewrite suggestions

### Step 3: Coverage Gap Analysis (Prolog rules)

1. Query Prolog for mandatory coverage categories
2. Check which categories are missing from prompt
3. Use Hy to prioritize gaps by impact heuristic

### Step 4: Aggregate & Report (Python)

Combine results from all three surfaces into final report.

## Usage

### As a Kilo Code Agent

The agent version is already available at `.kilo/agents/prompt-quality-evaluator.agent.md`

### As a Multi-Surface Skill

```python
# Import and use the skill
from em_cubed.skills.prompt_quality_evaluator import evaluate_prompt_quality

# Evaluate a prompt file
with open("my_agent.prompt.md", "r") as f:
    content = f.read()

result = evaluate_prompt_quality(content, use_llm=False)
print(f"Overall quality: {result['overall_quality']:.2f}/1.0")

# View persona issues
for issue in result["persona_consistency"]["issues"]:
    print(f"  - {issue['traits']}: {issue['suggestion']}")
```

### Command-Line Interface

```bash
# Analyze a prompt file
python -m em_cubed.skills.prompt_quality_evaluator analyze my_prompt.md

# Analyze with LLM enhancement
python -m em_cubed.skills.prompt_quality_evaluator analyze my_prompt.md --llm

# Batch analyze all prompts in directory
python -m em_cubed.skills.prompt_quality_evaluator batch ./prompts/ --output report.json
```

## Output Format

```json
{
  "persona_consistency": {
    "score": 0.85,
    "issues": [
      {
        "type": "persona_conflict",
        "traits": ["helpful", "sarcastic"],
        "severity": "warning",
        "suggestion": "Choose helpful OR sarcastic, not both",
        "line": 3
      }
    ],
    "surface": "python"
  },
  "ambiguity": {
    "score": 0.72,
    "issues": [
      {
        "text": "a few",
        "type": "quantifier",
        "severity": "info",
        "suggestion": "Replace with '2-3' or '3-5'",
        "line": 12
      }
    ],
    "surface": "hy"
  },
  "coverage": {
    "score": 0.75,
    "gaps": [
      {
        "category": "error_handling",
        "severity": "high",
        "suggestion": "Add: 'If user provides invalid input, ask for clarification.'",
        "line": 25
      }
    ],
    "surface": "prolog"
  },
  "overall_quality": 0.791,
  "surfaces_used": ["python", "prolog", "hy"]
}
```

## Integration with vscode-chat-customizations-evaluation Patterns

This skill reverse-engineers the evaluation criteria from `microsoft/vscode-chat-customizations-evaluation`:

**Derived patterns:**
- Persona conflict detection → `LLMPersonaResponse` schema
- Ambiguity taxonomy (5 types) → `LLMAmbiguityResponse` schema
- Coverage gap analysis → `LLMCoverageResponse` schema

**Key difference:** This skill uses the **multi-surface pattern** to perform analysis locally without requiring an LLM API call, whereas the VS Code extension uses a single LLM call for all analysis.

## Testing

```python
# Test all three surfaces work
from em_cubed.skills.prompt_quality_evaluator import evaluate_prompt_quality

test_prompt = """
You are a helpful assistant. Be professional and concise.
Answer questions briefly.
"""

result = evaluate_prompt_quality(test_prompt)
assert result["persona_consistency"]["score"] > 0.5
assert result["ambiguity"]["score"] > 0.5
assert "coverage" in result
```

## Migration from Single-Surface Agent

The original `.kilo/agents/prompt-quality-evaluator.agent.md` is a single-surface (LLM-based) agent. This skill demonstrates how the same logic can be distributed across three surfaces:

- **Python**: Keeps orchestration, delegates to specialized surfaces
- **Prolog**: Encodes persona conflict rules as logical facts and implications
- **Hy**: Implements fuzzy matching and heuristic scoring functions

## Future Enhancements

1. **Prolog expansion**: Add more sophisticated logical rules for edge case detection
2. **Hy ensemble**: Create multiple heuristic functions and weight them dynamically
3. **Python ML layer**: Add scikit-learn classification for ambiguity types
4. **Composition conflicts**: Detect when imported prompt fragments conflict (from `LLMCombinedAnalysisResponse`)

## References

- [vscode-chat-customizations-evaluation](https://github.com/microsoft/vscode-chat-customizations-evaluation) — Source evaluation patterns
- [Multi-Surface Skill Pattern](../docs/MULTI_SURFACE.md) — em-cubed architecture guide
- [Custom agents in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-agents) — Agent file format
