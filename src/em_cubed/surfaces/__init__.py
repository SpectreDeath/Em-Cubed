from .base import SurfaceBase
from typing import Optional as _Optional  # noqa: F401

# Surface classes with graceful handling of missing dependencies
PrologSurface = None  # type: _Optional[type]
HySurface = None  # type: _Optional[type]
PythonSurface = None  # type: _Optional[type]
Z3Surface = None  # type: _Optional[type]
DatalogSurface = None  # type: _Optional[type]

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

__all__ = ["SurfaceBase", "PrologSurface", "HySurface", "PythonSurface", "Z3Surface", "DatalogSurface"]
