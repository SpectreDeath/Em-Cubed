# Hy adapter
import asyncio
from typing import Dict, Any
from .base import Surface, SurfaceResult

class HyAdapter(Surface):
    name = 'hy'

    async def execute(self, code: str, context: Dict[str, Any]) -> SurfaceResult:
        try:
            import hy
            result = hy.eval(hy.read_str(code), context)
            return SurfaceResult('ok', value=result, logs=[])
        except ImportError:
            return SurfaceResult('error', value='Hy not installed', logs=['Install hy>=1.0.0a4'])
        except Exception as e:
            return SurfaceResult('error', value=str(e), logs=[str(e)])

    async def health(self) -> bool:
        try:
            import hy
            return True
        except ImportError:
            return False
