# Em-Cubed MCP Gateway Server

Connects **Em-Cubed**'s polyglot reasoning engine (148+ skills, 11 execution surfaces, formal ontology verification) to any Model Context Protocol (MCP) client such as **Claude Desktop**, **Cursor**, or **VS Code**.

---

## Capabilities & Tools Exposed

| Tool Name | Description |
|-----------|-------------|
| `em_cubed_search_skills` | Search 148+ skills by keyword, domain, or surface |
| `em_cubed_list_surfaces` | List all 11 polyglot surfaces (Python, Prolog, Z3, Datalog, Hy, SQLite, QuickJS, WASM, Clingo, Kanren, Janus) and health status |
| `em_cubed_execute_skill` | Execute a skill on any supported reasoning surface |
| `em_cubed_validate_triple` | Validate OWL functional & disjointness rules on ontology triples |
| `em_cubed_elicit_ontology` | Extract BFO/OntoClean OWL triples from natural language prompts |
| `em_cubed_evaluate_topos` | Evaluate confidence scores into Topos Ω modal truth (NECESSARY, POSSIBLE) |
| `em_cubed_extract_truthmakers` | Isolate Kit Fine exact truthmaker state fragments ($s \Vdash A$) |
| `em_cubed_prove_zkp` | Generate quantum-resistant Zero-Knowledge proof attestation commitments |
| `em_cubed_check_health` | Audit live Coherence Index (%) & self-healing guardrail metrics |
| `em_cubed_run_monad` | Execute surface functor monadic workflow mapping Python → Prolog → Z3 |
| `em_cubed_run_geopolitical_sim` | Run tri-engine simulation combining SME perception feeds, Topos Ω guards, and ABM |

---

## Client Setup

### Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "em-cubed": {
      "command": "uvx",
      "args": ["em-cubed[mcp]", "em3-mcp"]
    }
  }
}
```

Or for local development:

```json
{
  "mcpServers": {
    "em-cubed": {
      "command": "python",
      "args": ["-m", "em_cubed.gateway.mcp_server"],
      "cwd": "/path/to/em-cubed"
    }
  }
}
```

### Cursor / VS Code MCP Extension

Configure the stdio command:
- Command: `uvx`
- Arguments: `em-cubed[mcp]` `em3-mcp`
