---
name: JS Text Transformer
Domain: NLP
Version: 1.0.0
surfaces:
  - python
  - quickjs
---

## Purpose
Apply JavaScript-based string transformations (tokenization, slug generation, etc.) from within Python skills.

## Description
Leverage QuickJS for text transformations that are more naturally expressed in JavaScript (e.g., regex-based cleaning, slug generation). Python orchestrates data loading and result handling.

## Implementation

### Python
```python
def main(skill_input):
    """Main orchestrator."""
    text = skill_input.get("text", "")
    transform_type = skill_input.get("transform", "slug")

    # Map transform type to JS code (in practice, fetched from SKILL body)
    js_code = get_js_for_transform(transform_type)

    # Inject text into JS context
    context = {"text": text}

    result = context["surfaces"]["quickjs"].execute_sync(js_code, context)

    if result["status"] != "ok":
        return {"status": "error", "message": result.get("message")}

    return {"status": "ok", "transformed": result["value"]}


def get_js_for_transform(transform_type):
    """Return JS code snippet based on requested transformation."""
    if transform_type == "slug":
        return """
            var result = text.toLowerCase()
                .trim()
                .replace(/[^\\w\\s-]/g, '')
                .replace(/[\\s_-]+/g, '-')
                .replace(/^-+|-+$/g, '');
        """
    elif transform_type == "upper":
        return "var result = text.toUpperCase();"
    else:
        return "var result = text;"
```

### QuickJS
```javascript
// Transformation logic injected via context
// The result is stored in `result` variable and returned to Python
```

## Examples
```python
input_data = {"text": "  Hello, World!  ", "transform": "slug"}
# Expected output: {"status": "ok", "transformed": "hello-world"}
```
