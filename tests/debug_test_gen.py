from pathlib import Path
from em_cubed.skills import SkillRegistry
from em_cubed.skills.testing import SkillTestGenerator
from em_cubed.plugin_manager import PluginManager

registry = SkillRegistry(Path("skills"), Path("registry.json"))
plugin_manager = PluginManager()
generator = SkillTestGenerator(plugin_manager)

# Check a specific skill
skill_id = "AUTOMATION/workflow-synthesiser"
skill = registry.get_skill(skill_id)
print(f"Skill: {skill_id}")
print(f"  name: {skill.name}")
print(f"  path: {skill.path!r}")
print(f"  path exists: {Path(skill.path).exists() if skill.path else False}")

# Try generating tests
if skill.path:
    try:
        tests = generator.generate_tests_for_skill(Path(skill.path), skill)
        print(f"  Generated {len(tests)} tests")
        for t in tests[:3]:
            print(f"    - {t.name} ({t.surface})")
    except Exception as e:
        print(f"  ERROR: {e}")
else:
    print("  NO PATH - skipping")
