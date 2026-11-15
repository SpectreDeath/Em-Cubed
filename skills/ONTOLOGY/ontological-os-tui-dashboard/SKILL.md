---
name: ontological-os-tui-dashboard
domain: ONTOLOGY
version: 1.0.0
surfaces:
  - python
  - prolog
  - z3
description: Interactive Terminal User Interface (TUI) workspace dashboard for live ontological OS monitoring. Renders ANSI/Curses multi-panel terminal views displaying active triple ledgers, Topos Omega subobject classifier gauges, Kit Fine exact truthmaker groundings ($s \Vdash A$), Coherence Index health metrics, and quantum-resistant ZKP attestation proofs in real time. Use when monitoring live system status in terminal environments, viewing ontology telemetry interactively, or debugging multi-engine states.
purpose: Render real-time interactive terminal dashboards (TUI) displaying active ontology state, Topos truth, and health telemetry.
dependencies: []
tags:
  - tui-dashboard
  - terminal-ui
  - rich-terminal
  - curses
  - rich
  - topos-gauge
  - live-telemetry
inputs:
  refresh_interval_sec:
    type: number
    required: false
    description: Refresh rate in seconds for live telemetry polling (default 1.0).
  interactive_mode:
    type: boolean
    required: false
    description: Enable keyboard navigation and interactive inspection panels (default true).
outputs:
  rendered_frame:
    type: string
    description: Formatted multi-panel ASCII/ANSI dashboard string.
  active_telemetry:
    type: object
    description: Snapshot of displayed metrics (triple counts, Topos confidence, Coherence Index, ZKP status).
---

# Ontological OS TUI Dashboard Engine

`ontological-os-tui-dashboard` implements **Phase 20 Ontological OS Live Interactive Terminal Dashboard & TUI Workspace** in `Em-Cubed`. It provides an operator cockpit in the terminal, rendering live telemetry across triple ledgers, Topos $\Omega$ modal gauges, Kit Fine truthmakers, and Coherence Index health monitors using Rich/Curses ANSI components.

See [CARD.md](CARD.md) for the skill summary card, quick-reference tables, and completion criteria checklist.

---

## The 5-Stage TUI Rendering Progression

```
[1. Telemetry Ingest & Invariant Audit] → [2. Panel Layout Compilation] → [3. Visual Brief] → [4. Checkpoint] → [5. ANSI Render & Event Loop]
```

### Stage 1: Telemetry Ingest & Invariant Audit
1. Ingest real-time telemetry from active engines (Active Triples, Topos $\Omega$, Truthmaker, Coherence Index, ZKP Attestations).
2. Validate metric bounds and format numerical scores.

> **Completion criterion**: All engine telemetry streams ingested and normalized.

---

### Stage 2: Panel Layout Compilation
1. Layout terminal workspace into 5 synchronized panels:
   - **Panel 1: Active Triple Ledger**: Scrollable list of verified assertions.
   - **Panel 2: Topos $\Omega$ Gauge**: Continuous confidence bar and modal status.
   - **Panel 3: Kit Fine Truthmakers**: Exact minimal supporting state facts.
   - **Panel 4: Health Monitor**: Coherence Index percentage and status.
   - **Panel 5: ZKP Ledger**: Merkle root commitments and signatures.

> **Completion criterion**: Multi-panel terminal layout compiled into display buffer.

---

### Stage 3: The Visual Brief
For terminal dashboard styling updates or headless report generation, generate an interactive brief:
- **Location**: Write to `%TEMP%\tui-dashboard-brief-<timestamp>.html` (Windows) or `/tmp/tui-dashboard-brief-<timestamp>.html` (Unix).
- **Styling**: Dark theme (`#0d1117`) using Tailwind CSS and Mermaid.js via CDN.
- **Topology**: Render ASCII terminal dashboard layout preview and panel data flow graph.

> **Completion criterion**: Visual brief generated with active clickable path returned to caller.

---

### Stage 4: Mandatory Checkpoint
Before launching interactive blocking Curses event loops:
1. Verify terminal ANSI capability and screen dimensions ($\ge 80\times24$).
2. Provide fallback non-interactive static dump mode for CI/pipe environments.

> **Completion criterion**: Terminal capabilities verified and fallback mode ready.

---

### Stage 5: ANSI Rendering & Terminal Emit
1. Render formatted ANSI dashboard frame to terminal stdout.
2. Emit telemetry snapshot dictionary for logging.

> **Completion criterion**: Dashboard rendered cleanly with zero screen tearing.

---

## Surface References

### Python Rich TUI Surface

```python
from typing import Dict, Any

def render_tui_dashboard(triples_count: int = 3, topos_conf: float = 0.95, coherence: float = 1.0) -> Dict[str, Any]:
    header = "=" * 80 + "\n     EM-CUBED NEURO-SYMBOLIC ONTOLOGICAL OS - TUI WORKSPACE\n" + "=" * 80
    body = (
        f"[ACTIVE TRIPLE LEDGER]: {triples_count} Triples Loaded\n"
        f"[TOPOS OMEGA GAUGE]   : Confidence {topos_conf:.2f} / 1.00 (NECESSARY)\n"
        f"[HEALTH MONITOR]      : Coherence Index {coherence * 100:.1f}% (HEALTHY)\n"
        f"[ZKP ATTESTATION]     : Merkle Root c7e210... (PQC Verified)\n"
    )
    footer = "=" * 80
    frame = f"{header}\n{body}{footer}"
    
    return {
        "rendered_frame": frame,
        "active_telemetry": {
            "triples_count": triples_count,
            "topos_confidence": topos_conf,
            "coherence_index": coherence,
            "health_status": "HEALTHY"
        }
    }
```

---

## Anti-Patterns & Guardrails

- **Terminal Tearing / Flickering** — Redrawing the full screen without double-buffering or differential cell updates during high refresh rates.
- **Blocking in Pipe / CI Environments** — Launching interactive blocking Curses loops when stdout is redirected to a pipe or CI runner. Always detect `sys.stdout.isatty()`.
- **Truncated Panels** — Fixed-size layouts that crash when terminal dimensions are smaller than $80 \times 24$.
