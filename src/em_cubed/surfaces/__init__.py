from .base import SurfaceBase

# Import surfaces with graceful handling of missing dependencies
_prolog_available = False
_hy_available = False
_z3_available = False
_datalog_available = False

try:
    from .prolog_surface import PrologSurface
    _prolog_available = True
except ImportError:
    PrologSurface = None

try:
    from .hy_surface import HySurface
    _hy_available = True
except ImportError:
    HySurface = None

try:
    from .python_surface import PythonSurface
    _python_available = True
except ImportError:
    PythonSurface = None

try:
    from .z3_surface import Z3Surface
    _z3_available = True
except ImportError:
    Z3Surface = None

try:
    from .datalog_surface import DatalogSurface
    _datalog_available = True
except ImportError:
    DatalogSurface = None

__all__ = ["SurfaceBase", "PrologSurface", "HySurface", "PythonSurface", "Z3Surface", "DatalogSurface"]
