import asyncio
from pathlib import Path
from em_cubed.skills.quality_pipeline import SkillQualityPipeline
from em_cubed.plugin_manager import PluginManager

skills_dir = Path("skills")
registry_file = Path("registry.json")
pipeline = SkillQualityPipeline(skills_dir, registry_file, PluginManager())

async def main():
    results = await pipeline.validate_all_skills()
    failing = [(sid, r) for sid, r in results.items() if not r.valid]
    print(f"Failing ({len(failing)}):")
    for sid, r in failing:
        print(f"\n{sid}: score={r.quality_score:.2f}")
        for issue in r.issues:
            print(f"  [{issue.severity.value}] {issue.code}: {issue.message}")

asyncio.run(main())
