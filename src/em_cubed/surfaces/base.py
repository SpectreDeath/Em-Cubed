"""Backward compatibility for surface base class.

This module provides deprecated aliases for backward compatibility.
Use em_cubed.plugin_manager.SurfacePlugin for new code.
"""

from ..plugin_manager import SurfacePlugin as SurfaceBase, SurfaceTimeoutError

__all__ = ["SurfaceBase", "SurfaceTimeoutError"]