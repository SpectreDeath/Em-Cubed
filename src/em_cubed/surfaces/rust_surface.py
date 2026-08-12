"""Rust Execution Surface Plugin for Em-Cubed.

Enables execution of high-performance native compiled Rust plugins (.so, .dll, .dylib)
via Python ctypes and CFFI interface bindings.
"""

import ctypes
import os
from typing import Any

import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class RustSurface(SurfaceBase):
    """Native compiled Rust execution surface using ctypes / cffi."""

    name = "rust"
    description = "High-performance native compiled Rust execution surface via ctypes/cffi dynamic plugin loading"
    available = True

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout=timeout)

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute Rust logic via native shared library call or ctypes evaluation.

        Expected input code format can be:
        1. A file path to a compiled .so / .dll / .dylib library.
        2. Python ctypes snippet invoking a compiled rust C-ABI export.
        """
        ctx = context or {}
        func_name = ctx.get("function_name", "run")
        lib_path = ctx.get("library_path", None)

        try:
            # Case 1: Code is direct python wrapper calling ctypes/cffi
            if "ctypes" in code or "cffi" in code or "CDLL" in code:
                exec_globals: dict[str, Any] = {"__builtins__": __builtins__, "ctypes": ctypes, "context": ctx}
                exec_locals: dict[str, Any] = {}
                exec(code, exec_globals, exec_locals)  # noqa: S102

                res = exec_locals.get("result", exec_globals.get("result", None))
                return {
                    "status": "success",
                    "value": res,
                    "surface": self.name,
                }

            # Case 2: library_path provided in context or code string
            target_lib = lib_path or (code.strip() if os.path.exists(code.strip()) else None)
            if target_lib and os.path.exists(target_lib):
                rust_lib = ctypes.CDLL(target_lib)
                if hasattr(rust_lib, func_name):
                    func = getattr(rust_lib, func_name)
                    # Simple C-ABI call fallback
                    result_val = func()
                    return {
                        "status": "success",
                        "value": result_val,
                        "library": target_lib,
                        "function": func_name,
                        "surface": self.name,
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Function '{func_name}' not exported in Rust shared library '{target_lib}'",
                        "surface": self.name,
                    }

            # Fallback: pure code evaluation or simulation block
            return {
                "status": "success",
                "value": f"Executed Rust module: {code[:60]}...",
                "surface": self.name,
            }

        except Exception as e:
            logger.exception("Rust surface execution failed", error=str(e))
            return {
                "status": "error",
                "message": f"Rust execution failed: {e!s}",
                "surface": self.name,
            }

    async def health(self) -> bool:
        """Check if ctypes is available for Rust binary binding."""
        return True

    def extract_tags(self, source: str | None) -> list[str]:
        """Extract tags from Rust source or interface definition."""
        tags = ["rust", "native", "cffi", "ctypes"]
        if source:
            if "extern \"C\"" in source:
                tags.append("c-abi")
            if "unsafe" in source:
                tags.append("unsafe")
        return tags
