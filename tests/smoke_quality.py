"""Quick smoke test of the quality pipeline on a small subset."""
import asyncio
from pathlib import Path
from em_cubed.skills.quality_pipeline import SkillQualityPipeline
from em_cubed.plugin_manager import PluginManager

skills_dir = Path("skills")
registry_file = Path("registry.json")

if not registry_file.exists():
    print("Registry not found. Run 'em3 index skills/' first.")
    exit(1)

print("Initializing quality pipeline...")
pipeline = SkillQualityPipeline(skills_dir, registry_file, PluginManager())

async def main():
    print("\n=== validating all skills ===")
    results = await pipeline.validate_all_skills()
    valid = sum(1 for r in results.values() if r.valid)
    total = len(results)
    print(f"\nValidation: {valid}/{total} passed")
    for skill_id, result in results.items():
        if not result.valid:
            print(f"  FAIL: {skill_id}")
            for issue in result.issues[:3]:
                print(f"    - {issue.code}: {issue.message}")

    report = pipeline.get_quality_report()
    print("\nOverall Quality Report:")
    print(f"  Total skills: {report['total_skills']}")
    print(f"  Passing: {report['passing_quality']}")
    print(f"  Fail rate: {1 - report['pass_rate']:.1%}")

asyncio.run(main())
