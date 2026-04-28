"""Em-Cubed: Multi-Surface Skill Framework.

Supports Python, Prolog, and Hy execution surfaces with unified indexing and search.
"""

import structlog

# Configure basic logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

from .indexer import reindex, get_skill_metadata  # noqa: E402
from .search import search_registry  # noqa: E402
from .surfaces import PrologSurface, HySurface, JanusSurface, PythonSurface  # noqa: E402

__version__ = "0.2.0"
__all__ = [
    "reindex",
    "get_skill_metadata",
    "search_registry",
    "PrologSurface",
    "HySurface",
    "JanusSurface",
    "PythonSurface",
]
