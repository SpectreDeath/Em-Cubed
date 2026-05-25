# Cross-Surface Data Type Standardization

## Overview

Em-Cubed now includes a unified type system that enables seamless data exchange between different execution surfaces (Python, Prolog, Hy, Z3, Datalog). This eliminates the need for manual data conversion when building multi-surface skills and ensures type safety across surface boundaries.

## Features

### Automatic Type Conversion
- Built-in support for basic types: integer, float, boolean, string, list, dict
- Automatic conversion between Python and surface-specific representations
- Extensible type system for adding custom types

### Surface-Specific Representations
Each surface has its own natural representation for data types:
- **Python**: Native Python objects
- **Prolog**: Prolog terms (integers, floats, atoms, lists, etc.)
- **Hy**: Hy Lisp literals
- **Z3**: Z3 sorts and expressions
- **Datalog**: Datalog terms and tuples

### Type Safety
- Type inference reduces need for explicit type annotations
- Runtime validation helps catch type mismatches early
- Fallback mechanisms prevent execution failures

## Architecture

### TypeRegistry
Maintains definitions of data types and their representations across surfaces:
- Maps type names to conversion functions
- Knows how to represent each type in each surface
- Extensible for custom types

### TypeConverter
Handles actual conversion between Python and surface representations:
- Converts Python values to surface-specific forms
- Converts surface values back to Python
- Handles bidirectional conversion for all registered types

## Usage

### Automatic Integration
The type system is automatically integrated into the SkillExecutor:
- No changes needed to existing skills
- Type conversion happens at surface boundaries
- Works with existing substrate sharing mechanism

### Manual Usage
For advanced use cases, developers can access the type system directly:

```python
from em_cubed.context import get_type_converter

converter = get_type_converter()

# Convert Python to Prolog representation
prolog_value = converter.convert_to_surface(42, "prolog", "integer")
# Result: "42"

# Convert Prolog back to Python
python_value = converter.convert_from_surface("true", "prolog", "boolean")
# Result: True
```

### In Skills
Skills can rely on the type system working automatically when sharing data through the substrate:

```python
# Python skill that prepares data for Prolog
def skill_code(context):
    # Input data comes in as Python objects
    input_data = context["skill_input"]
    
    # Process data...
    result = {"count": len(input_data.get("items", [])),
              "items": input_data.get("items", [])}
    
    # Result is automatically converted when accessed by Prolog skill
    # through context["surfaces"]["prolog"]
    return {"status": "ok", "value": result}
```

## Supported Types

### Primitive Types
- **integer**: 42 → "42" (Prolog), 42 (Hy), etc.
- **float**: 3.14 → "3.14" (Prolog), 3.14 (Hy), etc.
- **boolean**: True → "true" (Prolog), true (Hy), etc.
- **string**: "hello" → '"hello"' (Prolog), "hello" (Hy), etc.

### Container Types
- **list**: [1,2,3] → "[1,2,3]" (Prolog), [1 2 3] (Hy), etc.
- **dict**: {"a": 1} → '{"a":1}' (Prolog), {"a" 1} (Hy), etc.

## Extending the Type System

To add custom types, extend the `TypeRegistry` with new `TypeDefinition` objects:

```python
from em_cubed.context import TypeRegistry, TypeDefinition

registry = TypeRegistry()
registry.register_type(TypeDefinition(
    name="custom_type",
    python_type=MyCustomClass,
    prolog_term="custom",
    hy_form="custom",
    z3_sort="Custom",
    datalog_predicate="custom",
    to_python=lambda x: MyCustomClass.from_string(x),
    from_python=lambda x: x.to_string(),
    to_prolog=lambda x: f"custom({x.to_prolog()})",
    from_prolog=lambda x: MyCustomClass.from_prolog(x),
    # ... other conversions
))
```

## Benefits

1. **Eliminates Manual Conversion**: No more needing to manually convert data types between surfaces
2. **Reduces Errors**: Automatic handling reduces type mismatch bugs
3. **Improves Developer Experience**: Focus on logic rather than data plumbing
4. **Enables Complex Workflows**: Makes sophisticated multi-surface pipelines practical
5. **Maintains Performance**: Conversions are lightweight and only happen at surface boundaries

## Future Enhancements

1. **Schema-Based Type Hints**: Use skill input/output schemas to guide type conversion
2. **Complex Types**: Support for user-defined classes, tuples, sets, etc.
3. **Validation**: Runtime type validation with configurable strictness
4. **Performance Optimization**: Caching of conversion functions
5. **Visual Debugging**: Tools to visualize type conversions during execution

## Conclusion

The cross-surface data type standardization feature significantly improves the developer experience when building multi-surface skills in Em-Cubed. By handling the complexity of data conversion automatically, developers can focus on the core logic of their skills while relying on the type system to ensure data flows correctly between different execution surfaces.

This feature addresses the sixth item from the development ideas file: **"Cross-Surface Data Type Standardization"** and provides a solid foundation for building sophisticated multi-surface workflows.