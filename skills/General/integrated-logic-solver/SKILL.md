---
name: Integrated Logic Solver
Domain: Logic and Reasoning
Version: 1.0.0
surfaces:
  - python
  - prolog
---
  - cangjie

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
### Cangjie Orchestrator

```cangjie
// ============================================================
// Typed Structs — Single Source of Truth for cross-surface data
// ============================================================

struct FamilyMember {
    name: String;
    father: Option<String>;
    mother: Option<String>;
    gender: String;       // "male" | "female"
}

struct RelationshipQuery {
    query_type: String;   // "grandparent" | "uncle" | "cousin"
    args: List<String>;   // variable bindings for the query
}

struct LogicResult {
    query: String;
    bindings: List<Map<String, String>>;
    success: Bool;
}

struct IntegratedLogicOutput {
    facts_generated: Int32;
    rules_defined: Int32;
    relationships: List<LogicResult>;
}

// ============================================================
// Surface: Python — Data transformation only (~20 LOC)
// ============================================================
// Generates Prolog fact strings from typed FamilyMember structs.
// No orchestration logic, no Prolog knowledge — pure data mapping.

func generate_prolog_facts(members: List<FamilyMember>): String {
    let py_code = """
import json

members = ${members}
facts = []

for m in members:
    if m.get("father"):
        facts.append(f"father({m['father']}, {m['name']}).")
    if m.get("mother"):
        facts.append(f"mother({m['mother']}, {m['name']}).")
    if m.get("gender"):
        facts.append(f"{m['gender']}({m['name']}).")

print("\\n".join(facts))
"""
    let py_result = perform EmCubed.call_surface("python", py_code);
    let output = py_result.get("output", "");
    return output;
}

// ============================================================
// Surface: Prolog — Pure relationship rules (~15 LOC)
// ============================================================
// Declarative logic only. Zero data handling or orchestration.
// These rules are static and defined once.

func build_prolog_rules(): String {
    return """
parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \\= Y.
uncle(X, Y) :- brother(X, Z), parent(Z, Y).
brother(X, Y) :- male(X), sibling(X, Y).
cousin(X, Y) :- parent(P1, X), parent(P2, Y), sibling(P1, P2).
""";
}

// ============================================================
// Main Orchestration Flow
// ============================================================

func main(input: Map<String, Dynamic>) -> IntegratedLogicOutput {
    println("Integrated Logic Solver — Cangjie Orchestrator Starting...");

    // Step 1: Parse input into typed structs
    let raw_members = input["family_members"] as List<Map<String, Dynamic>>;
    var members: List<FamilyMember> = [];
    for m in raw_members {
        members.append(FamilyMember{
            name: m["name"] as String,
            father: m.get("father") as Option<String>,
            mother: m.get("mother") as Option<String>,
            gender: m.get("gender", "unknown") as String
        });
    }

    // Step 2: Generate Prolog facts via Python surface (data transformation)
    let facts_code = generate_prolog_facts(members);

    // Step 3: Build static Prolog rules
    let rules_code = build_prolog_rules();

    // Step 4: Load KB — inject facts + rules into Prolog surface via template
    let prolog_code = f"{facts_code}\n{rules_code}";
    let kb_result = perform EmCubed.call_surface("prolog", prolog_code);

    if kb_result.get("status", "") != "ok" {
        println("Prolog KB load failed: " + kb_result.get("message", "Unknown error"));
        return IntegratedLogicOutput{
            facts_generated: 0,
            rules_defined: 0,
            relationships: []
        };
    }

    // Step 5: Query Prolog for complex relationships
    let queries = [
        RelationshipQuery{query_type: "grandparent", args: ["X", "Y"]},
        RelationshipQuery{query_type: "uncle",      args: ["X", "Y"]},
        RelationshipQuery{query_type: "cousin",     args: ["X", "Y"]}
    ];

    var results: List<LogicResult> = [];
    var facts_count: Int32 = 0;
    var rules_count: Int32 = 6; // parent, grandparent, sibling, uncle, brother, cousin

    for q in queries {
        let query_str = f"{q.query_type}({q.args.join(", ")})";
        let query_result = perform EmCubed.call_surface("prolog", query_str);

        if query_result.get("status", "") == "ok" {
            let bindings = query_result.get("bindings", []) as List<Map<String, String>>;
            results.append(LogicResult{
                query: query_str,
                bindings: bindings,
                success: true
            });
        } else {
            results.append(LogicResult{
                query: query_str,
                bindings: [],
                success: false
            });
        }
    }

    // Count generated facts from Python surface output
    facts_count = prolog_code.split("\n").filter(line => line.contains(".")).size() as Int32 - rules_count;

    // Step 6: Synthesize typed output
    return IntegratedLogicOutput{
        facts_generated: facts_count,
        rules_defined: rules_count,
        relationships: results
    };
}
```
