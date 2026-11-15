# Skill Summary Card: `mcp-interagent-gateway`

```
┌────────────────────────────────────────────────────────┐
│               SKILL SUMMARY CARD                       │
├────────────────────────────────────────────────────────┤
│ Name:        mcp-interagent-gateway                    │
│ Category:    ONTOLOGY / Model Context Protocol (MCP)   │
│ Invocation:  /mcp-interagent-gateway                   │
│ Trigger:     "start mcp server", "mcp tool dispatch",  │
│              "model context protocol", "interagent bus"│
│ Version:     1.0.0                                     │
├────────────────────────────────────────────────────────┤
│ Target:      Standard MCP JSON-RPC gateway server      │
│              exposing core Em-Cubed neurosymbolic      │
│              tools over STDIO/SSE transports.          │
└────────────────────────────────────────────────────────┘
```

---

## The 5-Stage Progression

| Stage | Objective | Primary Artifact / Output | Completion Gate |
|---|---|---|---|
| **1. Request Audit** | Validate JSON-RPC envelope & tool schema | Validated MCP Request | Schema validation passed |
| **2. Route Dispatch**| Map tool name to internal engine controller | Target Engine Route | Valid controller mapped |
| **3. Visual Brief** | Render client-gateway sequence diagram | `%TEMP%\mcp-gateway-brief-*.html`| Dark theme HTML sequence brief |
| **4. Checkpoint** | Validate client authorization and safety gates | Permission Status | Gated on state-mutating actions |
| **5. Execution & Emit**| Run tool and format standard MCP response | Standard MCP Payload | `{"content": [...], "isError": false}` emitted |

---

## Invariants & Guardrails

- [ ] **JSON-RPC 2.0 Compliance**: All responses must adhere to RFC JSON-RPC standards.
- [ ] **Strict Timeout**: Tool executions must terminate within 30 seconds.
- [ ] **Explicit Error Reporting**: Any failure must set `"isError": true` with actionable details.
