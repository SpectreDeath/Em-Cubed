"""Surface plugin implementations.

This package contains the various execution surfaces (Python, Prolog, Hy, Z3, Datalog, Janus)
with graceful handling of missing optional dependencies.
"""

from typing import Optional as _Optional  # noqa: F401

from .base import SurfaceBase

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
except (ImportError, Exception):
    pass

try:
    from .hy_surface import HySurface as _HySurface

    HySurface = _HySurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .python_surface import PythonSurface as _PythonSurface

    PythonSurface = _PythonSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .z3_surface import Z3Surface as _Z3Surface

    Z3Surface = _Z3Surface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .datalog_surface import DatalogSurface as _DatalogSurface

    DatalogSurface = _DatalogSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .janus_surface import JanusSurface as _JanusSurface

    JanusSurface = _JanusSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .llm_surface import LLMSurface as _LLMSurface

    LLMSurface = _LLMSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .sqlite_surface import SQLiteSurface as _SQLiteSurface

    SQLiteSurface = _SQLiteSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .quickjs_surface import QuickJSSurface as _QuickJSSurface

    QuickJSSurface = _QuickJSSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .kanren_surface import KanrenSurface as _KanrenSurface

    KanrenSurface = _KanrenSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .clingo_surface import ClingoSurface as _ClingoSurface

    ClingoSurface = _ClingoSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .wasm_surface import WASMSurface as _WASMSurface

    WASMSurface = _WASMSurface  # type: ignore[assignment]
except (ImportError, Exception):
    pass

try:
    from .duckdb_surface import DuckDBSurface as _DuckDBSurface

    DuckDBSurface = _DuckDBSurface  # type: ignore[assignment]
except (ImportError, Exception):
    DuckDBSurface = None  # type: ignore[assignment]

try:
    from .julia_surface import JuliaSurface as _JuliaSurface

    JuliaSurface = _JuliaSurface  # type: ignore[assignment]
except (ImportError, Exception):
    JuliaSurface = None  # type: ignore[assignment]

try:
    from .tensor_surface import TensorSurface as _TensorSurface

    TensorSurface = _TensorSurface  # type: ignore[assignment]
except (ImportError, Exception):
    TensorSurface = None  # type: ignore[assignment]

try:
    from .shared_substrate_arrow import ArrowSharedSubstrate as _ArrowSharedSubstrate

    ArrowSharedSubstrate = _ArrowSharedSubstrate  # type: ignore[assignment]
except (ImportError, Exception):
    ArrowSharedSubstrate = None  # type: ignore[assignment]

try:
    from .morphism import SurfaceMorphism as _SurfaceMorphism

    SurfaceMorphism = _SurfaceMorphism  # type: ignore[assignment,misc]
except (ImportError, Exception):
    SurfaceMorphism = None  # type: ignore[assignment,misc]

try:
    from .functor import OntologyMonad as _OntologyMonad
    from .functor import SurfaceFunctor as _SurfaceFunctor

    SurfaceFunctor = _SurfaceFunctor  # type: ignore[assignment,misc]
    OntologyMonad = _OntologyMonad  # type: ignore[assignment,misc]
except (ImportError, Exception):
    SurfaceFunctor = None  # type: ignore[assignment,misc]
    OntologyMonad = None  # type: ignore[assignment,misc]

try:
    from .polars_surface import PolarsSurface as _PolarsSurface

    PolarsSurface = _PolarsSurface  # type: ignore[assignment]
except (ImportError, Exception):
    PolarsSurface = None  # type: ignore[assignment]

try:
    from .rust_surface import RustSurface as _RustSurface

    RustSurface = _RustSurface  # type: ignore[assignment]
except (ImportError, Exception):
    RustSurface = None  # type: ignore[assignment]

__all__ = [
    "ArrowSharedSubstrate",
    "ClingoSurface",
    "DatalogSurface",
    "DuckDBSurface",
    "HySurface",
    "JanusSurface",
    "JuliaSurface",
    "KanrenSurface",
    "LLMSurface",
    "OntologyMonad",
    "PolarsSurface",
    "PrologSurface",
    "PythonSurface",
    "QuickJSSurface",
    "RustSurface",
    "SQLiteSurface",
    "SurfaceBase",
    "SurfaceFunctor",
    "SurfaceMorphism",
    "TensorSurface",
    "WASMSurface",
    "Z3Surface",
]



