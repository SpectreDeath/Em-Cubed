from em_cubed.skills.registry import SkillRegistry
from pathlib import Path

registry = SkillRegistry(Path("skills"), Path("registry.json"))
skill = registry.get_skill("TIME_SERIES/time-series-forecaster")
print("Skill:", skill.name if skill else "NOT FOUND")
if skill:
    print("Surfaces:", skill.surfaces)
    print("Surfaces type:", type(skill.surfaces))
    print("Length:", len(skill.surfaces) if skill.surfaces else 0)
    print("Quality thresholds:", skill.quality_thresholds)
    print("Required surfaces:", skill.quality_thresholds.required_surfaces)
    print("Version:", skill.version)
