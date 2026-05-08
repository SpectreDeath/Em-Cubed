import tempfile
from pathlib import Path
from em_cubed.indexer import get_skill_metadata

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir_p = Path(tmpdir)
    skills_dir = tmpdir_p / "skills"
    skills_dir.mkdir()
    skill_dir = skills_dir / "math_calculator"
    skill_dir.mkdir()

    skill_file = skill_dir / "SKILL.md"
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
    skill_file.write_text(content)

    metadata = get_skill_metadata(skill_file, skills_dir)
    print("Metadata:", metadata)
    print("Purpose repr:", repr(metadata.get("purpose")))
    print("Description repr:", repr(metadata.get("description")))
