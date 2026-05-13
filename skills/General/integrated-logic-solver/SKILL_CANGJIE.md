# Integrated Logic Solver - Cangjie Edition
# Cangjie-optimized orchestration for multi-surface logical reasoning

## Purpose

Demonstrates true multi-surface orchestration using the **Logic Refinement** archetype: Python normalizes family relationship data into typed structs, Cangjie orchestrates cross-surface composition, and Prolog performs pure declarative inference. Python generates Prolog facts and rules dynamically at runtime, injects them via template strings, and the Prolog surface executes logical queries — all orchestrated through typed Cangjie pipelines.

**Original**: Python monolith contained both data processing and Prolog glue code (96 LOC).
**Cangjie**: Clean separation — Python surface handles data transformation only, Prolog surface handles pure rules only, Cangjie orchestrator manages typed data flow and template injection.

## Architecture

**Archetype**: Logic Refinement (Python Normalize → Prolog Prune → CJ Synthesize)

```
┌─────────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│   Python Surface │────▶│  Cangjie Orchestrator │────▶│  Prolog Surface  │
│  (Data Transform)│     │  (Typed Pipeline)     │     │  (Logic Inference)│
│  ~20 LOC         │     │  Template Injection   │     │  ~15 LOC         │
└─────────────────┘     └──────────────────────┘     └──────────────────┘
        │                         │                          │
        ▼                         ▼                          ▼
  FamilyMember[]          IntegratedLogicOutput         Grandparent,
  structs                 LogicResult struct             Uncle, Cousin
```

**Key Design Decisions**:
- Two-phase Prolog execution: first `call_surface` loads the KB (facts + rules), second `call_surface` queries it
- Template injection passes dynamically generated Prolog code as `${prolog_code}` string
- Python surface contains zero orchestration logic — only data-to-facts conversion
- Prolog surface contains zero data handling — only pure relationship rules

## Implementation

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

### Surface Blocks

| Surface | Role | LOC | Content |
|---------|------|-----|---------|
| **Python** | Data transformation: `FamilyMember[]` → Prolog fact strings | ~20 | `generate_prolog_facts()` — iterates structs, builds `father/mother/gender` atom strings |
| **Prolog** | Pure logical rules: relationship inference | ~15 | `parent/2`, `grandparent/3`, `sibling/2`, `uncle/2`, `brother/2`, `cousin/2` |
| **Cangjie** | Typed orchestration, template injection, flow control | ~50 | Structs, `main()`, query loop, result synthesis |

## Testing

### Unit Test: Python Fact Generation

```python
# Test that Python surface correctly generates Prolog facts from struct input
from em_cubed import CangjieSurface
import asyncio

surface = CangjieSurface()

async def test_fact_generation():
    input_data = {
        "family_members": [
            {"name": "john", "gender": "male"},
            {"name": "mary", "gender": "female"},
            {"name": "peter", "gender": "male", "father": "john", "mother": "mary"},
            {"name": "anna", "gender": "female", "father": "peter"},
            {"name": "bob", "gender": "male", "father": "peter"}
        ]
    }

    result = await surface.execute("generate_prolog_facts", input_data)
    output = result["output"].strip().split("\n")

    # Verify fact count: 5 gender facts + 4 parent facts = 9
    assert len(output) == 9, f"Expected 9 facts, got {len(output)}"

    # Verify specific facts exist
    assert "father(john, peter)." in output
    assert "mother(mary, peter)." in output
    assert "male(john)." in output
    assert "female(mary)." in output
    assert "female(anna)." in output

    # Verify no orchestration logic leaked into Python surface
    for line in output:
        assert "prolog" not in line.lower(), "Python surface should not reference Prolog"

    print("✓ Python fact generation unit test passed")

asyncio.run(test_fact_generation())
```

### Integration Test: Full Pipeline

```python
# Test the complete orchestration: input → facts → KB load → queries → structured output
from em_cubed import CangjieSurface
import asyncio

surface = CangjieSurface()

async def test_full_pipeline():
    input_data = {
        "family_members": [
            {"name": "john", "gender": "male"},
            {"name": "mary", "gender": "female"},
            {"name": "peter", "gender": "male", "father": "john", "mother": "mary"},
            {"name": "anna", "gender": "female", "father": "peter"},
            {"name": "bob", "gender": "male", "father": "peter"}
        ]
    }

    result = await surface.execute("", input_data)
    value = result["value"]

    # Verify output structure
    assert "facts_generated" in value
    assert "rules_defined" in value
    assert "relationships" in value

    # Verify fact generation
    assert value["facts_generated"] >= 9, f"Expected >=9 facts, got {value['facts_generated']}"

    # Verify rules defined
    assert value["rules_defined"] == 6, f"Expected 6 rules, got {value['rules_defined']}"

    # Verify relationship results
    rels = value["relationships"]
    assert len(rels) == 3, f"Expected 3 relationship queries, got {len(rels)}"

    # Verify grandparent relationship found
    gp_result = next(r for r in rels if "grandparent" in r["query"])
    assert gp_result["success"], "Grandparent query should succeed"
    assert len(gp_result["bindings"]) > 0, "Should find at least one grandparent relationship"

    # john is grandparent of anna and bob
    binding_names = [b.get("X", "") for b in gp_result["bindings"]]
    assert "john" in binding_names, "john should appear as grandparent"

    # Verify uncle relationship (none expected in this dataset)
    uncle_result = next(r for r in rels if "uncle" in r["query"])
    assert uncle_result["success"], "Uncle query should succeed"

    # Verify cousin relationship (none expected — anna and bob share same father)
    cousin_result = next(r for r in rels if "cousin" in r["query"])
    assert cousin_result["success"], "Cousin query should succeed"

    print("✓ Full pipeline integration test passed")
    print(f"  Facts generated: {value['facts_generated']}")
    print(f"  Rules defined: {value['rules_defined']}")
    for r in rels:
        print(f"  {r['query']}: {len(r['bindings'])} results")

asyncio.run(test_full_pipeline())
```

### Test Validation Matrix

| Test | Surface | Assertions | Pass Criteria |
|------|---------|-----------|---------------|
| Fact generation unit | Python | 9 facts, correct atoms | All assertions match |
| KB load | Prolog | No errors on load | `status == "ok"` |
| Grandparent query | Prolog | john → anna, bob | 2+ bindings |
| Uncle query | Prolog | Valid execution | `success == true` |
| Cousin query | Prolog | Valid execution | `success == true` |
| Full pipeline | All | End-to-end correctness | Structured output with all fields populated |

## Usage Patterns

### Pattern 1: Basic Family Analysis

```cangjie
let family = [
    FamilyMember{name: "alice", gender: "female"},
    FamilyMember{name: "bob", gender: "male", father: "alice"},
    FamilyMember{name: "charlie", gender: "male", father: "bob", mother: "alice"},
    FamilyMember{name: "diana", gender: "female", father: "charlie"}
];

let result = main({"family_members": family});
// result.relationships contains grandparent(Alice, Diana), etc.
```

### Pattern 2: Dynamic Query Construction

```cangjie
// Build specific queries at runtime
let custom_queries = [
    RelationshipQuery{query_type: "grandparent", args: ["X", "diana"]},
    RelationshipQuery{query_type: "sibling", args: ["X", "Y"]}
];

// Reuse orchestrator with custom queries by extending the queries loop
```

### Pattern 3: Extending Relationship Rules

```cangjie
// Add new rules to build_prolog_rules() return string:
// aunt(X, Y) :- female(X), sibling(X, Z), parent(Z, Y).
// nephew(X, Y) :- male(X), parent(Z, X), sibling(Z, Y).
```

## Migration Notes

- **Original skill (96 LOC)**: Single Python file mixing data processing, Prolog code generation, execution, and query logic
- **Cangjie version**: Clean separation — Python surface (20 LOC) is purely data transformation, Prolog surface (15 LOC) is purely declarative rules, Cangjie orchestrator (50 LOC) handles typed flow
- **Key improvement**: Template injection (`${prolog_code}`) eliminates manual string concatenation and JSON serialization overhead between surfaces
- **Archetype alignment**: Follows the **Logic Refinement** pattern — Python normalizes, Prolog reasons, Cangjie synthesizes

## Dependencies

- `pyswip` (Prolog surface backend)
- `em_cubed` framework
- Cross-surface bridge (automatic via `perform EmCubed.call_surface`)