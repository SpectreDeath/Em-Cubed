# ADR 003: YAML Frontmatter Skill Metadata Format

## Status

Accepted

## Context

Skills need rich metadata for discovery, validation, and execution. Need a format that's human-readable, machine-parseable, and supports complex data structures like input/output schemas and dependencies.

## Decision

Use YAML frontmatter in SKILL.md files with:

1. YAML header delimited by ---
2. Markdown body for documentation and code blocks
3. Structured metadata including schemas, dependencies, capabilities
4. Automatic tag extraction from code blocks

## Consequences

### Positive
- Human-readable: Easy to edit and understand
- Structured: Supports complex nested data
- Documentation: Markdown body allows rich formatting
- Tooling: Standard YAML parsers available
- Validation: Can validate against JSON schemas

### Negative
- Complexity: YAML syntax can be error-prone
- Parsing: Need custom frontmatter parsing logic
- Size: Large metadata can make files unwieldy
- Versioning: Schema changes require migration logic

## Alternatives Considered

1. JSON files - Less human-readable, separate from documentation
2. TOML - Less widespread, similar complexity
3. Database storage - Requires additional infrastructure
4. Inline comments - Not structured, hard to parse