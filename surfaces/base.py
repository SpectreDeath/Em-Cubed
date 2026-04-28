from typing import Dict, Any

class SurfaceResult:
    def __init__(self, status: str, value: Any = None, logs: list = None):
        self.status = status
        self.value = value
        self.logs = logs or []

class Surface:
    name: str = 'base'

    async def execute(self, code: str, context: Dict[str, Any]) -> SurfaceResult:
        raise NotImplementedError

    async def health(self) -> bool:
        return True
