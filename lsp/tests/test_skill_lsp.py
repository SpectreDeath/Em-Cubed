"""Tests for Em-Cubed Skill LSP server logic (frontmatter validation & completions)."""

from lsprotocol.types import DiagnosticSeverity
from lsp.src.skill_lsp import (
    _validate_frontmatter,
    _frontmatter_completions,
)


def test_valid_frontmatter_produces_no_diagnostics():
    doc = """---
name: Test Skill
domain: ANALYTICS
surfaces:
  - python
---
# Test Skill Body
"""
    diags = _validate_frontmatter(doc)
    assert len(diags) == 0


def test_missing_frontmatter_delimiter_produces_error():
    doc = "# Just a header\nname: Test"
    diags = _validate_frontmatter(doc)
    assert len(diags) == 1
    assert "Expected --- at start and end" in diags[0].message
    assert diags[0].severity == DiagnosticSeverity.Error


def test_missing_required_fields_produces_error():
    doc = """---
domain: ANALYTICS
---
"""
    diags = _validate_frontmatter(doc)
    missing = [d.message for d in diags if "Missing required field" in d.message]
    assert len(missing) == 2  # name, surfaces missing
    assert any("name" in m for m in missing)
    assert any("surfaces" in m for m in missing)


def test_unknown_domain_produces_warning():
    doc = """---
name: Test Skill
domain: INVALID_DOMAIN_1234
surfaces:
  - python
---
"""
    diags = _validate_frontmatter(doc)
    domain_warns = [d for d in diags if "Unknown domain" in d.message]
    assert len(domain_warns) == 1
    assert domain_warns[0].severity == DiagnosticSeverity.Warning


def test_unknown_surface_produces_warning():
    doc = """---
name: Test Skill
domain: ANALYTICS
surfaces:
  - unknown_surface_99
---
"""
    diags = _validate_frontmatter(doc)
    surf_warns = [d for d in diags if "Unknown surface" in d.message]
    assert len(surf_warns) == 1
    assert surf_warns[0].severity == DiagnosticSeverity.Warning


def test_top_level_completions():
    items = _frontmatter_completions("")
    labels = [item.label for item in items]
    assert "name" in labels
    assert "domain" in labels
    assert "surfaces" in labels


def test_domain_completions():
    items = _frontmatter_completions("domain:")
    labels = [item.label for item in items]
    assert "ANALYTICS" in labels
    assert "STATISTICS" in labels
    assert "OPTIMIZATION" in labels


def test_surface_completions():
    items = _frontmatter_completions("surfaces:")
    labels = [item.label for item in items]
    assert "python" in labels
    assert "prolog" in labels
    assert "z3" in labels
