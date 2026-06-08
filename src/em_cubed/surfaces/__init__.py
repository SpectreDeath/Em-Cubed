"""Surface plugin implementations.

This package contains the various execution surfaces (Python, Prolog, Hy, Z3, Datalog, Janus)
with graceful handling of missing optional dependencies.
"""

from .base import SurfaceBase
from typing import Optional as _Optional  # noqa: F401

# Surface classes with graceful handling of missing dependencies
PrologSurface = None  # type: _Optional[type]
HySurface = None  # type: _Optional[type]
PythonSurface = None  # type: _Optional[type]
Z3Surface = None  # type: _Optional[type]
DatalogSurface = None  # type: _Optional[type]
JanusSurface = None  # type: _Optional[type]
LLMSurface = None  # type: _Optional[type]
SQLiteSurface = None  # type: _Optional[type]
QuickJSSurface = None  # type: _Optional[type]
WASMSurface = None  # type: _Optional[type]
KanrenSurface = None  # type: _Optional[type]
ClingoSurface = None  # type: _Optional[type]

try:
    from .prolog_surface import PrologSurface as _PrologSurface
    PrologSurface = _PrologSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .hy_surface import HySurface as _HySurface
    HySurface = _HySurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .python_surface import PythonSurface as _PythonSurface
    PythonSurface = _PythonSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .z3_surface import Z3Surface as _Z3Surface
    Z3Surface = _Z3Surface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .datalog_surface import DatalogSurface as _DatalogSurface
    DatalogSurface = _DatalogSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .janus_surface import JanusSurface as _JanusSurface
    JanusSurface = _JanusSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .llm_surface import LLMSurface as _LLMSurface
    LLMSurface = _LLMSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .sqlite_surface import SQLiteSurface as _SQLiteSurface
    SQLiteSurface = _SQLiteSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .quickjs_surface import QuickJSSurface as _QuickJSSurface
    QuickJSSurface = _QuickJSSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .kanren_surface import KanrenSurface as _KanrenSurface
    KanrenSurface = _KanrenSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .clingo_surface import ClingoSurface as _ClingoSurface
    ClingoSurface = _ClingoSurface  # type: ignore[assignment]
except ImportError:
    pass

try:
    from .wasm_surface import WASMSurface as _WASMSurface
    WASMSurface = _WASMSurface  # type: ignore[assignment]
except ImportError:
    pass

__all__ = ["SurfaceBase", "PrologSurface", "HySurface", "PythonSurface", "Z3Surface", "DatalogSurface", "JanusSurface", "LLMSurface", "SQLiteSurface", "QuickJSSurface", "WASMSurface", "KanrenSurface", "ClingoSurface"]
