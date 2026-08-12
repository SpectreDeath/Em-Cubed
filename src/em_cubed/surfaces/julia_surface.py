"""Julia surface integration for mathematical, automatic differentiation, and scientific computing skills."""

import asyncio
import shutil
import subprocess
from typing import Any

import structlog

from .base import SurfaceBase

logger = structlog.get_logger()

# Check for juliacall package or system julia binary
try:
    import juliacall  # type: ignore[import-untyped]

    _JULIACALL_AVAILABLE = True
except ImportError:
    juliacall = None
    _JULIACALL_AVAILABLE = False

_JULIA_EXE_AVAILABLE = shutil.which("julia") is not None


class JuliaSurface(SurfaceBase):
    """Handle execution of Julia code for scientific computing, differential equations, and AD."""

    @property
    def name(self) -> str:
        return "julia"

    @property
    def description(self) -> str:
        return "Julia high-performance scientific and mathematical computing surface"

    @property
    def available(self) -> bool:
        return _JULIACALL_AVAILABLE or _JULIA_EXE_AVAILABLE

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        self._jl_main = None
        if _JULIACALL_AVAILABLE:
            try:
                self._jl_main = juliacall.Main
            except Exception as e:
                logger.warning("juliacall initialization failed", error=str(e))

        logger.info(
            "JuliaSurface initialized",
            juliacall=_JULIACALL_AVAILABLE,
            julia_exe=_JULIA_EXE_AVAILABLE,
        )

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute Julia code via juliacall or subprocess fallback."""
        if not self.available:
            return {
                "status": "error",
                "message": "Julia is not available. Install juliacall via `pip install juliacall` or install Julia runtime.",
            }

        logger.info("Executing Julia code", code_length=len(code))

        if self._jl_main is not None:
            try:
                # Inject context into Julia Main module
                if context:
                    for k, v in context.items():
                        if k.isidentifier():
                            setattr(self._jl_main, k, v)

                # Evaluate julia code
                res = self._jl_main.seval(code)
                # Convert result to python primitive if possible
                val = str(res) if res is not None else None
                try:
                    if hasattr(res, "_jl_raw"):
                        val = str(res)
                except Exception:
                    pass

                return {"status": "ok", "value": val}
            except Exception as e:
                logger.exception("Julia execution via juliacall failed", error=str(e))
                return {"status": "error", "message": str(e)}

        # Subprocess fallback
        try:
            loop = asyncio.get_running_loop()

            def run_julia_subprocess() -> dict[str, Any]:
                process = subprocess.run(
                    ["julia", "-e", code],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False,
                )
                if process.returncode != 0:
                    return {"status": "error", "message": process.stderr.strip() or "Julia subprocess exited with error"}
                return {"status": "ok", "value": process.stdout.strip()}

            return await loop.run_in_executor(self._executor, run_julia_subprocess)

        except subprocess.TimeoutExpired:
            return {"status": "error", "message": f"Julia execution timed out after {self.timeout}s"}
        except Exception as e:
            logger.exception("Julia subprocess execution failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check operational status of Julia surface."""
        if not self.available:
            return False
        res = await self._execute_impl("1 + 1")
        return res.get("status") == "ok"

    def extract_tags(self, source: str | None) -> list[str]:
        """Extract function names and package imports from Julia code."""
        if not source:
            return []
        import re

        tags = re.findall(r"function\s+([a-zA-Z0-9_!]+)", source)
        tags.extend(re.findall(r"using\s+([a-zA-Z0-9_]+)", source))
        tags.extend(re.findall(r"import\s+([a-zA-Z0-9_]+)", source))
        return list(dict.fromkeys(tags))
