---
name: skill-harness-builder
domain: Harness
version: 1.0.0
surfaces:
  - python
  - sqlite
description: Compile declarative SKILL.md definitions into executable, sandboxed tool harnesses. Dispatch tool mapping via Python and persist workspace state in SQLite. Use when transforming skill definitions into operational sandboxes, enforcing scoped tool permissions, or tracking persistent workspace sessions.
purpose: Transform declarative SKILL.md definitions into an executable sandboxed harness that maps declared tools, enforces scoped operations, and tracks persistent workspace state across sessions.
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
    description: Parsed SKILL.md frontmatter and body.
  tool_schema:
    type: array
    required: true
    description: List of available tools for sandbox mapping.
  workspace_mode:
    type: string
    required: false
    description: "isolated or shared (default: shared)"
  sandbox_policy:
    type: object
    required: false
    description: Policy rules for sandbox permissions and resource bounds.
outputs:
  harness_manifest:
    type: object
    description: Compiled harness configuration manifest.
  tool_map:
    type: object
    description: Tool interface mappings with permission scopes.
  workspace_id:
    type: string
    description: ID of initialized workspace.
  readiness_status:
    type: string
    description: "build_failed | sandbox_locked | ready"
---

# Skill Harness Builder Engine

`skill-harness-builder` compiles declarative `SKILL.md` blueprints into isolated, sandboxed execution harnesses. It maps tools to granular capability scopes, enforces resource bounds, and persists state across execution sessions.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 6-Stage Harness Compilation & Execution Loop

Execute this sequence when building, sandboxing, or validating a skill harness:

```
[1. Audit & Parse] → [2. Scope Formulation] → [3. Visual Brief] → [4. Checkpoint] → [5. Compilation & State Lock] → [6. Smoke Test]
```

### Stage 1: Definition Audit & Invariant Validation
1. Parse the target `SKILL.md` frontmatter and body.
2. Validate required specification invariants: `name`, `version`, `domain`, `surfaces`, `inputs`, and `outputs`.
3. Extract declared tool requirements and cross-reference against system capabilities.

> **Completion criterion**: Frontmatter and body parsed into structured AST with zero validation errors.

---

### Stage 2: Tool Scope & Sandbox Formulation
1. Map declared tool identifiers against `tool_schema`.
2. Construct granular capability scopes (`read`, `write`, `exec`, `network`, `ipc`) for each mapped tool.
3. Formulate sandbox resource bounds (`max_memory_mb`, `timeout_ms`, `filesystem_isolation`) according to `sandbox_policy`.

> **Completion criterion**: Complete `tool_map` generated with explicit least-privilege permission masks for every tool.

---

### Stage 3: The Visual Brief
For complex tool mappings or multi-surface harness topologies, generate an interactive HTML brief:
- **Location**: Write to `%TEMP%\harness-build-brief-<timestamp>.html` (Windows) or `/tmp/harness-build-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render the dependency graph, tool permission matrix, and surface interactions.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before initializing live processes or modifying SQLite workspace registries:
1. Verify workspace isolation mode (`isolated` vs `shared`).
2. If destructive schema mutations or permission elevations are detected, generate an `implementation_plan.md` checkpoint with `RequestFeedback: true` and halt for approval.

> **Completion criterion**: Execution plan reviewed and verified against sandbox security constraints.

---

### Stage 5: Manifest Compilation & SQLite State Locking
1. Emit compiled `harness_manifest` binding Python dispatch handlers to scoped tools.
2. If `workspace_mode == "shared"`, persist workspace record and metadata into SQLite:
   ```sql
   INSERT INTO harness_workspaces (workspace_id, skill_name, domain, tool_map, sandbox_policy, state_hash)
   VALUES (:workspace_id, :skill_name, :domain, :tool_map, :sandbox_policy, :state_hash);
   ```
3. Record initial lifecycle telemetry event in `harness_events`.

> **Completion criterion**: Harness manifest emitted and SQLite state atomically committed.

---

### Stage 6: Sandbox Verification & Smoke Testing
1. Execute a non-mutating probe call through the Python dispatch surface.
2. Verify boundary confinement (attempted out-of-scope operations are intercepted and denied).
3. Set `readiness_status` to `ready` (or `sandbox_locked` / `build_failed` upon constraint failure).

> **Completion criterion**: Smoke test probe succeeds with confirmed sandbox confinement and `readiness_status == "ready"`.

---

## Surface References

### Python Surface

```python
from em_cubed.skills.harness_builder import build_harness

harness = build_harness(
    skill_definition={
        "name": "world-simulator",
        "version": "1.0.0",
        "domain": "WORLD_MODELS",
        "surfaces": ["python", "datalog", "clingo"],
        "description": "Deterministic world simulation engine.",
        "purpose": "Compile and execute simulated environment ticks.",
        "dependencies": ["durable-execution-engine"],
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

### SQLite Surface Schema

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

---

## Capability Contract

### Inputs
- `skill_definition` *(object, required)* — Parsed `SKILL.md` frontmatter and structured body.
- `tool_schema` *(array, required)* — Available tools for sandbox mapping.
- `workspace_mode` *(string, optional)* — `isolated` or `shared` (default: `shared`).
- `sandbox_policy` *(object, optional)* — Policy rules for sandbox permissions and limits.

### Outputs
- `harness_manifest` *(object)* — Compiled harness configuration.
- `tool_map` *(object)* — Tool interface mappings with permission scopes.
- `workspace_id` *(string)* — ID of initialized workspace.
- `readiness_status` *(string)* — `build_failed`, `sandbox_locked`, or `ready`.

---

## Composition
- `durable-execution-engine` — Checkpoint and recover harness state across sessions.
- `observability-dashboard` — Monitor harness build metrics and sandbox access patterns.
- `dag-task-scheduler` — Schedule harness build steps with dependency tracking.

---

## Anti-Patterns & Guardrails

- **Unscoped Tool Execution** — Exposing uncurated host tools directly to the execution runtime without scope enforcement. Always wrap tools with granular permission masks (`read`, `write`, `exec`).
- **Sandbox Drift & Escape** — Allowing sandboxed processes unrestricted network or filesystem access outside workspace root. Always enforce explicit boundary policies.
- **Session State Desync** — Mutating workspace configurations without recording an event in `harness_events`. Maintain atomic state hashes in `harness_workspaces`.
- **Silent Fallback** — Masking build errors by continuing with an invalid manifest. Terminate build immediately and return `readiness_status == "build_failed"`.
