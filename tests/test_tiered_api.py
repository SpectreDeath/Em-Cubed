"""Tests for Tiered Public API and PEP 562 deprecation handling in em_cubed."""

import pytest
import warnings
import em_cubed


def test_public_all_contains_primary_api():
    """__all__ should contain only the ~18 primary public symbols."""
    assert len(em_cubed.__all__) <= 20
    expected = {
        "reindex",
        "get_skill_metadata",
        "search_registry",
        "PythonSurface",
        "PrologSurface",
        "Z3Surface",
        "DatalogSurface",
        "SQLiteSurface",
        "HySurface",
        "QuickJSSurface",
        "WASMSurface",
        "ClingoSurface",
        "KanrenSurface",
        "JanusSurface",
        "SkillRegistry",
        "SkillExecutor",
        "SkillValidator",
        "__version__",
    }
    assert set(em_cubed.__all__) == expected


def test_primary_api_direct_access():
    """Primary symbols are accessible directly from em_cubed without warnings."""
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        _ = em_cubed.PythonSurface
        _ = em_cubed.reindex
        _ = em_cubed.SkillRegistry
    assert len(recorded) == 0


def test_legacy_symbol_deprecation_warning():
    """Legacy internal symbols emit DeprecationWarning but return the object."""
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        validator_cls = getattr(em_cubed, "OntologyLedgerValidator")
        assert validator_cls is not None
        mcp_cls = getattr(em_cubed, "EmCubedMCPServer")
        assert mcp_cls is not None

    dep_warnings = [w for w in recorded if issubclass(w.category, DeprecationWarning)]
    assert len(dep_warnings) == 2
    assert "OntologyLedgerValidator" in str(dep_warnings[0].message)
    assert "em_cubed.ontology" in str(dep_warnings[0].message)
    assert "EmCubedMCPServer" in str(dep_warnings[1].message)
    assert "em_cubed.gateway" in str(dep_warnings[1].message)


def test_invalid_attribute_raises_attribute_error():
    """Non-existent attribute raises AttributeError."""
    with pytest.raises(AttributeError):
        _ = getattr(em_cubed, "NonExistentClass12345")
