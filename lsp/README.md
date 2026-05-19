# Em-Cubed Skill Language Server

A Language Server Protocol implementation for SKILL.md files in Em-Cubed, providing:
- Autocomplete for SKILL.md frontmatter fields
- Validation of required fields and data types
- YAML syntax checking
- Hover documentation
- Document symbol support

## Features

### Autocomplete
- Suggests valid frontmatter fields (name, domain, version, surfaces, triggers, description)
- Provides surface type suggestions (python, prolog, hy, z3, janus, sqlite, quickjs, cangjie, llm)
- Offers list item completion for arrays like `surfaces`

### Validation
- Checks for required fields (name, domain, surfaces)
- Validates data types (strings vs lists)
- YAML syntax error detection
- Missing field warnings

### Documentation
- Hover tooltips showing field descriptions
- Context-sensitive help

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Installation
```bash
pip install -r requirements.txt
```

### Usage
```bash
python -m em_cubed_lsp
```

Or run directly:
```bash
python lsp/src/skill_lsp.py
```

## Configuration

The language server automatically activates for `.skill.md` files and standard `SKILL.md` files.

## Supported SKILL.md Format

```yaml
---
name: Skill Name
domain: Skill Domain
version: 1.0.0  # optional
surfaces:
  - python
  - llm
triggers:       # optional
  - example
  - test
description:    # optional
  Brief description of the skill
---

## Skill documentation goes here
```

## Development

To run in development mode:
```bash
python lsp/src/skill_lsp.py
```

## License

MIT