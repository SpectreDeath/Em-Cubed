"""Em-Cubed: Multi-Surface Skill Framework.

Supports Python, Prolog, and Hy execution surfaces with unified indexing and search.
"""

from .indexer import reindex, get_skill_metadata  # noqa: E402
from .search import search_registry  # noqa: E402
from .surfaces import PrologSurface, HySurface, PythonSurface  # noqa: E402

# JanusSurface is not implemented
class JanusSurface:
    """Janus surface is not implemented."""
    def __init__(self):
        raise NotImplementedError("JanusSurface is not implemented. Requires janus-swi package and SWI-Prolog system installation.")

__version__ = "0.3.0"
__all__ = [
    "reindex",
    "get_skill_metadata",
    "search_registry",
    "PrologSurface",
    "HySurface",
    "JanusSurface",
    "PythonSurface",
]
