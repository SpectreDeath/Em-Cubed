"""Interactive Visual Graph & Trajectory Explorer Renderer.

Generates standalone HTML/SVG interactive visualizations for Knowledge Graph paths,
LoopTrajectory step metrics, and Topos Omega truth classifications.
"""

from __future__ import annotations

import logging

from em_cubed.loopy.audit import AuditReport
from em_cubed.ontology.graph_rag import SubgraphPath

logger = logging.getLogger(__name__)


class KnowledgeGraphVisualizer:
    """Visualizer producing interactive HTML graph and trajectory renderers."""

    @staticmethod
    def render_subgraph_html(paths: list[SubgraphPath], title: str = "Knowledge Graph Explorer") -> str:
        """Render a list of SubgraphPaths into a standalone HTML visualization document."""
        path_list_items = "".join([f"<li><code>{p.to_summary_string()}</code></li>" for p in paths])

        html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #1e293b; padding-bottom: 0.5rem; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        code {{ background: #0284c7; color: #ffffff; padding: 0.2rem 0.5rem; border-radius: 4px; font-family: monospace; }}
        ul {{ list-style-type: square; line-height: 1.8; }}
    </style>
</head>
<body>
    <h1>🧠 {title}</h1>
    <div class="card">
        <h3>Discovered Subgraph Traversal Paths ({len(paths)})</h3>
        <ul>
            {path_list_items if paths else "<li>No paths discovered</li>"}
        </ul>
    </div>
</body>
</html>"""
        logger.info("Rendered Knowledge Graph HTML document (%d bytes).", len(html_doc))
        return html_doc

    @staticmethod
    def render_audit_report_html(report: AuditReport) -> str:
        """Render an AuditReport into an interactive HTML proof log viewer."""
        proof_items = ""
        for p in report.proof_annotations:
            status_color = "#22c55e" if p.verified else "#ef4444"
            status_text = "VERIFIED" if p.verified else "RETRY HYPOTHESIS"
            proof_items += f"""
            <div style="background: #1e293b; border-left: 4px solid {status_color}; padding: 1rem; margin-bottom: 0.8rem; border-radius: 4px;">
                <strong>Step {p.iteration} [{p.proof_type}]</strong> - <span style="color: {status_color};">{status_text}</span><br>
                <small>Solver: {p.solver_used}</small><br>
                <p style="margin-top: 0.4rem; color: #cbd5e1;">{p.proof_details}</p>
            </div>"""

        html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Audit Trail: {report.skill_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }}
        h1 {{ color: #38bdf8; }}
    </style>
</head>
<body>
    <h1>📜 Mechanistic Proof Audit Log: {report.skill_name}</h1>
    <p>Overall Result: <strong>{"PASSED" if report.success else "FAILED"}</strong></p>
    {proof_items}
</body>
</html>"""
        return html_doc
