---
name: ontological-os-cli-suite
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
  - datalog
description: End-to-end command-line terminal suite (em3 ontology) for orchestrating the ontological OS. Dispatches subcommands for triple validation, 6-stage knowledge elicitation, Kit Fine truthmaker extraction, Description Logic concept induction, interactive HTML visualization, schema migration, and health auditing. Use when automating ontology workflows via shell scripts, managing CI/CD semantic validation pipelines, or executing CLI commands against Em-Cubed.
purpose: Provide a unified terminal CLI suite (`em3 ontology`) for executing, testing, and managing ontological OS operations.
dependencies: []
tags:
  - cli-suite
  - terminal-commands
  - shell-automation
  - bash
  - em3-cli
  - ci-cd-pipelines
inputs:
  subcommand:
    type: string
    required: true
    description: "Target CLI action: validate | elicit | truthmaker | induce | visualize | migrate | health"
  cli_args:
    type: array
    required: false
    description: Flag arguments passed to the subcommand (e.g. `['--subject', 'USO_1001', '--predicate', 'has_origin']`).
outputs:
  exit_code:
    type: integer
    description: Process exit code (0 for success, non-zero for error).
  stdout_output:
    type: string
    description: CLI stdout text stream and diagnostic logs.
  generated_artifacts:
    type: array
    description: File paths to generated artifacts (HTML visualizations, Turtle exports, reports).
---

# Ontological OS CLI Suite Engine

`ontological-os-cli-suite` implements **Phase 11 End-to-End Ontological OS CLI Suite** in `Em-Cubed`. It wraps all neurosymbolic engines into a modular, production-ready terminal tool (`em3 ontology`), enabling automated scripting, continuous integration validation, and interactive administrative operations.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage CLI Execution Progression

```
[1. Command & Arg Invariant Audit] → [2. Subcommand Dispatch] → [3. Visual Brief] → [4. Checkpoint] → [5. Execution & Exit Code Emit]
```

### Stage 1: Command & Arg Invariant Audit
1. Ingest `subcommand` and flag options.
2. Validate required arguments for selected subcommand (e.g., `--subject` for `validate`, `--domain-prompt` for `elicit`).

> **Completion criterion**: CLI command and flags parsed into valid configuration AST.

---

### Stage 2: Subcommand Engine Dispatch
1. Map CLI command to target engine implementation:
   - `validate`: Dispatches to OWL/Prolog door validator.
   - `elicit`: Dispatches to 6-stage PMEST elicitation engine.
   - `truthmaker`: Dispatches to Kit Fine truthmaker classifier.
   - `induce`: Dispatches to DL concept induction engine.
   - `visualize`: Dispatches to SVG/HTML knowledge graph visualizer.
   - `migrate`: Dispatches to schema evolution migrator.
   - `health`: Dispatches to self-healing Coherence Index auditor.

> **Completion criterion**: Engine dispatched and execution context initialized.

---

### Stage 3: The Visual Brief
For terminal visualization commands or failed validations, generate an interactive brief:
- **Location**: Write to `%TEMP%\cli-suite-brief-<timestamp>.html` (Windows) or `/tmp/cli-suite-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render command execution pipeline, argument flags, and stdout stream.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before executing mutating CLI commands (e.g. `em3 ontology migrate`):
1. Prompt for user confirmation if `--dry-run` is not specified.
2. Verify that state backups exist in the Merkle replay engine.

> **Completion criterion**: Mutating CLI actions certified safe or validated in dry-run mode.

---

### Stage 5: Execution & Exit Code Emit
1. Execute core logic, format terminal ANSI outputs, and write generated artifacts to disk.
2. Return exit code `0` on success or `1` / `2` on validation / syntax failure.

> **Completion criterion**: Subcommand execution terminates with clean exit code and formatted stdout.

---

## Surface References

### Bash / Terminal CLI Surface

```bash
# 1. Door & Ledger Rule Validation
em3 ontology validate --subject USO_1001 --predicate has_origin --object Uruguay

# 2. 6-Stage Knowledge Elicitation
em3 ontology elicit --domain-prompt "Supply Chain Folic Acid Sourcing"

# 3. Kit Fine's Truthmaker Semantics
em3 ontology truthmaker --proposition "Ingredient Compliance"

# 4. Interactive Visualization Export
em3 ontology visualize --output-html /tmp/graph_dashboard.html
```

---

## Anti-Patterns & Guardrails

- **Silent Exit Failures** — Returning exit code `0` when validation fails or syntax errors occur. Always return non-zero exit codes on failure.
- **Unformatted Output Flooding** — Dumping 5,000 lines of unformatted debug text to stdout. Format summaries cleanly with optional `--verbose` flags.
- **Destructive Defaults** — Executing schema migrations without requiring explicit `--confirm` or `--dry-run` flags.
