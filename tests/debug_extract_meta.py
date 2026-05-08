import re

content = """---
name: Math Calculator
Domain: Mathematics
Version: 1.0.0
surfaces:
  - python
---

## Purpose
Perform mathematical calculations

## Description
A simple calculator that can add, subtract, multiply, and divide numbers.

```python
def add(x, y):
    return x + y
```
"""

# Extract purpose
purpose_match = re.search(r"## Purpose\s*\n\s*(.+)", content)
print("Purpose match:", purpose_match)
if purpose_match:
    print("Purpose:", purpose_match.group(1).strip())

# Extract description
desc_match = re.search(r"## Description\s*\n\s*(.+)", content)
print("Desc match:", desc_match)
if desc_match:
    print("Desc:", desc_match.group(1).strip())
