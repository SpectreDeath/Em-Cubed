# Python runner surface
import ast
import asyncio
from typing import Dict, Any
from .base import Surface, SurfaceResult

class PythonRunner(Surface):
    name = 'python'

    async def execute(self, code: str, context: Dict[str, Any]) -> SurfaceResult:
        try:
            # Restricted execution context
            safe_globals = {'__builtins__': {}}
            safe_globals.update(context)
            result = eval(code, safe_globals, {})
            return SurfaceResult('ok', value=result, logs=[])
        except Exception as e:
            return SurfaceResult('error', value=str(e), logs=[str(e)])

    async def health(self) -> bool:
        return True
