"""QuickJS surface integration for executing JavaScript code."""

import asyncio
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional, List
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class QuickJSSurface(SurfaceBase):
    """Handle JavaScript code execution using pyquickjs."""

    @property
    def name(self) -> str:
        return "quickjs"

    @property
    def description(self) -> str:
        return "JavaScript execution via QuickJS"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        self._executor = ThreadPoolExecutor(max_workers=1)
        logger.info("QuickJSSurface initialized", available=self.available)

    def _check_availability(self) -> bool:
        """Check if pyquickjs is available."""
        available = importlib.util.find_spec("quickjs") is not None
        if not available:
            logger.warning("pyquickjs not available for QuickJS surface")
        return available

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute JavaScript code and return results."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute JavaScript code in the executor thread."""
        logger.info("Executing JavaScript code", code_length=len(code))

        if not self.available:
            return {"status": "error", "message": "pyquickjs not available"}

        try:
            import quickjs
            
            # Use a fresh context for each execution
            ctx = quickjs.Context()
            
            # Inject context variables if provided (primitive types only)
            if context:
                for key, value in context.items():
                    if isinstance(value, (int, float, str, bool, list, dict)) or value is None:
                        try:
                            # Use JSON as bridge for complex types
                            import json
                            ctx.set(key, ctx.parse_json(json.dumps(value)))
                        except Exception:
                            pass # Skip if serialization fails

            # Execute the code
            result = ctx.eval(code)
            
            # Convert result back to Python if it's a QuickJS object
            # Note: result might be a simple type or a QuickJS object
            
            logger.info("JavaScript execution successful")
            return {"status": "ok", "value": result}

        except Exception as e:
            logger.exception("JavaScript execution failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return self.available

    def extract_tags(self, source: Optional[str]) -> List[str]:
        """Extract function names from JavaScript source."""
        if not source:
            return []
        import re
        # Match function declarations or assignments
        fns = re.findall(r"function\s+([a-zA-Z0-9_]+)\s*\(", source)
        fns.extend(re.findall(r"const\s+([a-zA-Z0-9_]+)\s*=\s*(?:function|\()", source))
        return list(dict.fromkeys(fns))
