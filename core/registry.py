# Core registry for surfaces and skills
from typing import Dict, Any

class Registry:
    def __init__(self):
        self.surfaces: Dict[str, Any] = {}
        self.skills: Dict[str, Any] = {}
        self.index = {}

    def register_surface(self, name: str, surface: Any) -> None:
        self.surfaces[name] = surface

    def register_skill(self, name: str, skill: Any) -> None:
        self.skills[name] = skill

    def get_surface(self, name: str) -> Any:
        return self.surfaces.get(name)
