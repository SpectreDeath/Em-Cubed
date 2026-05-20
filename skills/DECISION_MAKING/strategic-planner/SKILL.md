---
name: Strategic Planner
Domain: DECISION_MAKING
Version: 1.0.0
surfaces:
  - llm
---

## Purpose
A Strategic Planner skill.

## Description
Detailed description for Strategic Planner.

## Implementation

### LLM Decision Maker
```python
from typing import Dict, Any, List, Optional
import json

def make_decision(context: Dict[str, Any], options: List[str], criteria: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Make a decision based on context and available options using LLM reasoning.
    
    Args:
        context: Context information for the decision
        options: List of available options to choose from
        criteria: Optional list of criteria to consider
        
    Returns:
        Dictionary containing the decision and reasoning
    """
    # Prepare prompt for LLM
    prompt = f"""
    Context: {json.dumps(context, indent=2)}
    
    Available options:
    {chr(10).join(f"- {option}" for option in options)}
    
    """
    
    if criteria:
        prompt += f"\nDecision criteria:\n{chr(10).join(f'- {criterion}' for criterion in criteria)}\n"
    
    prompt += """
    Please select the best option and explain your reasoning.
    Respond in JSON format:
    {
        "selected_option": "the chosen option",
        "reasoning": "explanation of why this option was selected",
        "confidence": 0.0-1.0
    }
    """
    
    # In a real implementation, this would call the LLM surface
    # For now, we'll return a structured response
    return {
        "selected_option": options[0] if options else None,
        "reasoning": "Selected first option as default (LLM integration pending)",
        "confidence": 0.5
    }

# Execute decision making
result = make_decision(skill_input.get("context", {}), 
                      skill_input.get("options", []),
                      skill_input.get("criteria"))
```
## Examples
```python
context = {"task": "Choose best approach for data processing"}
options = ["Approach A: Batch processing", "Approach B: Stream processing", "Approach C: Hybrid"]
criteria = ["Cost efficiency", "Processing speed", "Scalability"]

# Expected output format:
# {
#     "selected_option": "Approach A: Batch processing",
#     "reasoning": "explanation of why this option was selected",
#     "confidence": 0.8
# }
```