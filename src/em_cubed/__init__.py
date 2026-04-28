"""Em-Cubed: Multi-Surface Skill Framework.

Supports Python, Prolog, and Hy execution surfaces with unified indexing and search.
"""
from .indexer import reindex, get_skill_metadata
from .search import search_registry
from .surfaces import PrologSurface, HySurface, JanusSurface

__version__ = "0.1.0"
__all__ = [
    "reindex",
    "get_skill_metadata",
    "search_registry",
    "PrologSurface",
    "HySurface",
    "JanusSurface",
]
