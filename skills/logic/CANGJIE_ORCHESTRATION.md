---
name: MultiSurfaceLogic
Domain: Logic
Version: 0.1.0
surfaces:
  - cangjie
  - python
  - prolog
purpose: Demonstrate Cangjie as a high-performance orchestrator for Python and Prolog.
description: This skill uses Cangjie to coordinate a Prolog fact-check and a Python data transformation.
---

## Multi-Surface Orchestration

```cangjie
// This is the orchestrator
func main() {
    // Effect handling would happen here in a real scenario
    // For now, we demonstrate the logical structure
    println("Cangjie Orchestrator Starting...")
    
    // 1. Call Prolog to verify a condition
    // In a real implementation, this would be an effect:
    // let result = perform EmCubed.call_surface("prolog", "fact(x).")
    
    // 2. Call Python to process data
    // let processed = perform EmCubed.call_surface("python", "def process(x): return x * 2")
    
    println("Orchestration Complete.")
}
```

```prolog
% Logic base
valid_data(test_id).
```

```python
# Transformation logic
def transform(data):
    return f"Processed: {data}"
```
