---
Domain: EXAMPLES
name: python-prolog-pipeline
Version: 1.0.0
Complexity: Low
Type: Graph
Category: Example Skills
Estimated Execution Time: 1-2 minutes
Source: community
---
origin: manual
triggers:
  - example
  - pipeline
  - graph
quality:
  applied_count: 0
  success_count: 0
  completion_rate: 0.0
  token_savings_avg: 0.0
created_at: "2026-05-07T21:00:00Z"
updated_at: "2026-05-07T21:00:00Z"

## Purpose

Classic Python→Prolog pipeline: find a path in a graph. Cangjie acts as the typed orchestrator passing edge lists between surfaces.

## Architecture

**Archetype**: Linear Pipeline (single-direction data flow)

```cangjie
struct GraphInput {
    edges: Array<(String, String)>;
    start: String;
    end: String;
}

struct GraphOutput {
    path: Array<String>;
    found: Bool;
}
```

## Cangjie Orchestrator

```cangjie
func main(input: GraphInput) -> GraphOutput {
    // Assert edges in Prolog (facts)
    let prolog_assert = """
edge(a, b).
edge(b, c).
edge(c, d).
"""
    // Dynamically generate edge facts from input
    var facts = "";
    for (src, dst) in input.edges {
        facts += f"edge({src}, {dst}).\n";
    }
    _ = perform EmCubed.call_surface("prolog", facts + """
path(X, X, [X]).
path(X, Y, [X|Rest]) :-
    edge(X, Z),
    path(Z, Y, Rest).
""");

    // Query
    let query = f"path({input.start}, {input.end}, Path)";
    let result = perform EmCubed.call_surface("prolog", query);

    let path = match result.get("Path") {
        Some(p) => p,
        None => []
    };

    return GraphOutput{
        path: path,
        found: len(path) > 0
    };
}
```

## Implementation

| Surface | Code | Lines |
|---------|------|-------|
| Prolog (facts + query) | Dynamic edge assertions + recursive path/3 rule | ~15 |

**No Python block needed** — this skill is pure Prolog orchestrated by Cangjie.

## Testing

```python
surface = CangjieSurface()

input = {
    "edges": [["a","b"], ["b","c"], ["c","d"]],
    "start": "a",
    "end": "d"
}

result = await surface.execute("", input)
assert result["value"]["found"] == True
assert result["value"]["path"] == ["a", "b", "c", "d"]
```

## Dependencies

- pyswip (Prolog)
- em_cubed

## Notes

- Original used Python→Prolog bridge code; Cangjie removes that glue
- LOC: expected ~40 vs 99 original (−60%)
