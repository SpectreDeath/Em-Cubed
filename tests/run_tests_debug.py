import asyncio
from pathlib import Path
from em_cubed.skills.quality_pipeline import SkillQualityPipeline
from em_cubed.plugin_manager import PluginManager

skills_dir = Path("skills")
registry_file = Path("registry.json")
pipeline = SkillQualityPipeline(skills_dir, registry_file, PluginManager())

async def main():
    print("Running quality pipeline...")
    report = await pipeline.test_all_skills(generate_tests=True)
    print("Done. Results:", report)

asyncio.run(main())
