---
name: skill-harness-builder
domain: Harness
version: 1.0.0
surfaces:
- python
- sqlite
description: 'Multi-surface skill harness builder that compiles SKILL.md definitions into operational tool harnesses. Python
  surface handles sandboxed tool mapping and execution dispatch. SQLite surface persists workspace state and harness configuration.

  '
purpose: 'Transform declarative SKILL.md definitions into an executable sandboxed harness that maps declared tools, enforces
  scoped operations, and tracks persistent workspace state across sessions.

  '
dependencies:
- durable-execution-engine
tags:
- harness
- sandbox
- tool-mapping
- workspace
- sqlite
- skill-compiler
inputs:
  skill_definition:
    type: object
    required: true
    description: Parsed SKILL.md frontmatter and body
  tool_schema:
    type: array
    required: true
    description: List of available tools for sandbox mapping
  workspace_mode:
    type: string
    required: false
    description: 'isolated or shared (default: shared)'
  sandbox_policy:
    type: object
    required: false
    description: Policy rules for sandbox permissions
outputs:
  harness_manifest:
    type: object
    description: Compiled harness configuration
  tool_map:
    type: object
    description: Tool interface mappings with permission scopes
  workspace_id:
    type: string
    description: ID of initialized workspace
  readiness_status:
    type: string
    description: build_failed | sandbox_locked | ready
---

# Skill Harness Builder

Compiles SKILL.md definitions into executable, sandboxed tool harnesses.
Python dispatches builds; SQLite persists workspace state.

## Tick Protocol

| Id | Surface       | Action                                                |
|----|---------------|-------------------------------------------------------|
| 1  | Python        | Parse SKILL.md frontmatter and body                   |
| 2  | Python        | Validate required fields (name, version, domain)      |
| 3  | Python        | Map declared tools to sandbox schema                  |
| 4  | SQLite        | INSERT workspace record if workspace_mode == shared   |
| 5  | Python        | Apply sandbox_policy to tool_map                      |
| 6  | Python        | Emit harness_manifest                                 |
| 7  | Return        | readiness_status == ready if no violations            |

## Surfaces

### Python Surface

```python
from em_cubed.skills.harness_builder import build_harness

harness = build_harness(
    skill_definition={
        "name": "world-simulator",
        "version": "1.0.0",
        "domain": "WORLD_MODELS",
        "surfaces": ["python", "datalog", "clingo"],
        "description": "...",
        "purpose": "...",
        "dependencies": [],
        "inputs": {},
        "outputs": {},
    },
    tool_schema=[
        {"name": "python_exec", "scopes": ["read", "write", "exec"]},
        {"name": "datalog_query", "scopes": ["read"]},
    ],
    workspace_mode="shared",
    sandbox_policy={"max_memory_mb": 512, "network": False},
)
```

### SQLite Surface

```sql
CREATE TABLE IF NOT EXISTS harness_workspaces (
    workspace_id TEXT PRIMARY KEY,
    skill_name TEXT NOT NULL,
    domain TEXT NOT NULL,
    tool_map JSON NOT NULL,
    sandbox_policy JSON,
    created_at INTEGER DEFAULT (strftime('%s','now')),
    state_hash TEXT
);

CREATE TABLE IF NOT EXISTS harness_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSON,
    timestamp INTEGER DEFAULT (strftime('%s','now')),
    FOREIGN KEY (workspace_id) REFERENCES harness_workspaces (workspace_id)
);
```

## Capability Contract

**Inputs:**

- `skill_definition` *(object, required)* — Parsed SKILL.md frontmatter and body.
- `tool_schema` *(array, required)* — Available tools for sandbox mapping.
- `workspace_mode` *(string, optional)* — `isolated` or `shared`. Default `shared`.
- `sandbox_policy` *(object, optional)* — Policy rules for sandbox permissions.

**Outputs:**

- `harness_manifest` *(object)* — Compiled harness configuration.
- `tool_map` *(object)* — Tool interface mappings with permission scopes.
- `workspace_id` *(string)* — ID of initialized workspace.
- `readiness_status` *(string)* — `build_failed`, `sandbox_locked`, or `ready`.

## Composition

- `durable-execution-engine` — Checkpoint harness state across sessions.
- `observability-dashboard` — Monitor harness build metrics and sandbox access patterns.
- `dag-task-scheduler` — Schedule harness build steps with dependencies.
