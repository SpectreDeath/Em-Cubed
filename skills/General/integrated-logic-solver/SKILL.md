---
name: Integrated Logic Solver
Domain: Logic and Reasoning
Version: 1.0.0
surfaces:
  - python
  - prolog
---

## Purpose
Demonstrates true multi-surface orchestration by using Python to dynamically generate and execute Prolog logic, showcasing how different surfaces can work together to solve complex problems that neither could solve alone.

## Description
This skill illustrates the power of the Em-Cubed framework's multilogic architecture by having Python generate Prolog facts and rules based on input data, then querying the Prolog surface to perform logical inference. The result is then processed further in Python. This pattern allows leveraging the strengths of each paradigm: Python for data processing and control flow, and Prolog for declarative logical reasoning.

The skill solves a classic logical reasoning problem: given a set of family relationships, determine complex familial connections that require both data processing (Python) and logical inference (Prolog).

## Implementation

### Python
```python
def process_family_data(family_members):
    """Process family data and generate Prolog facts for relationship inference.
    
    Args:
        family_members: List of dictionaries containing family member data
        
    Returns:
        Processed results from Prolog reasoning
    """
    # Generate Prolog facts from family data
    facts = []
    for member in family_members:
        # Generate parent facts
        if 'father' in member and member['father']:
            facts.append(f"father({member['father']}, {member['name']}).")
        if 'mother' in member and member['mother']:
            facts.append(f"mother({member['mother']}, {member['name']}).")
        
        # Generate gender facts
        if 'gender' in member:
            facts.append(f"{member['gender']}({member['name']}).")
    
    # Define Prolog rules for relationships
    rules = [
        "parent(X, Y) :- father(X, Y).",
        "parent(X, Y) :- mother(X, Y).",
        "grandparent(X, Z) :- parent(X, Y), parent(Y, Z).",
        "sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \\= Y.",
        "uncle(X, Y) :- brother(X, Z), parent(Z, Y).",
        "cousin(X, Y) :- parent(P1, X), parent(P2, Y), sibling(P1, P2)."
    ]
    
    # Combine facts and rules
    prolog_code = "\n".join(facts + rules)
    
    # Execute Prolog reasoning - use execute_sync for orchestration from Python
    prolog_result = context["surfaces"]["prolog"].execute_sync(prolog_code, {})
    
    if prolog_result["status"] != "ok":
        return {"error": f"Prolog execution failed: {prolog_result.get('message', 'Unknown error')}"}
    
    # Now query for specific relationships
    queries = [
        "grandparent(X, Y)",  # Find all grandparent relationships
        "uncle(X, Y)",        # Find all uncle relationships
        "cousin(X, Y)"        # Find all cousin relationships
    ]
    
    results = {}
    for query in queries:
        # Use execute_sync for synchronous query result
        query_result = context["surfaces"]["prolog"].execute_sync(query, {})
        if query_result["status"] == "ok":
            # Extract results from Prolog output
            results[query] = query_result.get("result", [])
        else:
            results[query] = {"error": query_result.get("message", "Unknown error")}
    
    return {
        "facts_generated": len(facts),
        "rules_defined": len(rules),
        "relationships": results
    }

# Example usage with sample data
sample_family = [
    {"name": "john", "gender": "male"},
    {"name": "mary", "gender": "female", "father": "john"},
    {"name": "peter", "gender": "male", "father": "john", "mother": "mary"},
    {"name": "anna", "gender": "female", "father": "peter"},
    {"name": "bob", "gender": "male", "father": "peter"}
]

result = process_family_data(sample_family)
```

### Prolog
```prolog
% No direct implementation needed - Prolog is used dynamically by Python
% The Python code generates facts and rules, then queries the Prolog surface
```

## Examples
Example usage showing how to use this skill to solve family relationship problems:

```python
# This would be called through the skill executor
input_data = {
    "family_members": [
        {"name": "alice", "gender": "female"},
        {"name": "bob", "gender": "male", "father": "alice"},
        {"name": "charlie", "gender": "male", "father": "bob", "mother": "alice"},
        {"name": "diana", "gender": "female", "father": "charlie"}
    ]
}

# Expected output would include:
# - Facts generated: 4 (gender facts for each person plus parent relationships)
# - Rules defined: 6 (parent, grandparent, sibling, uncle, cousin rules)
# - Relationships: Contains results for grandparent, uncle, and cousin queries
```

## Notes
- This skill requires both Python and Prolog surfaces to be available
- Demonstrates true cross-surface orchestration where Python controls the flow and Prolog handles logical inference
- Shows how context["surfaces"] injection enables skills to leverage multiple execution paradigms
- The Prolog surface is used dynamically - no static Prolog code is needed in the skill definition

````
