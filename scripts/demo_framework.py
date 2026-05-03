#!/usr/bin/env python3
"""
Comprehensive demonstration of the Skills Quality Framework.
This script demonstrates all major capabilities.
"""

import asyncio
from pathlib import Path
from em_cubed.skills import (
    SkillRegistry,
    SkillValidator,
    SkillComposer,
    SkillRecommender,
    SkillBenchmark,
    TelemetryCollector,
    initialize_telemetry,
)
from em_cubed.plugin_manager import PluginManager
from em_cubed.skills.composer import CompositionStep, CompositionPattern

async def main():
    print("\n" + "="*60)
    print("SKILLS QUALITY FRAMEWORK DEMONSTRATION")
    print("="*60)

    skills_dir = Path("skills")
    registry_file = Path("registry.json")

    # Initialize components
    print("\n[1] Initializing components...")
    plugin_manager = PluginManager()
    registry = SkillRegistry(skills_dir, registry_file)
    validator = SkillValidator()
    composer = SkillComposer(plugin_manager, registry)
    recommender = SkillRecommender(registry)
    telemetry = initialize_telemetry()

    print(f"   Loaded {len(registry._skills)} skills")
    print(f"   Available surfaces: {', '.join(plugin_manager.get_available_surfaces())}")

    # Demonstrate validation
    print("\n[2] Skill Validation Results:")
    sample_skills = list(registry._skills.keys())[:5]
    for skill_id in sample_skills:
        skill = registry.get_skill(skill_id)
        qm = registry.get_quality(skill_id)
        status = "✓ PASS" if qm and qm.validation_score >= 0.7 else "✗ FAIL"
        print(f"   {status} {skill_id[:40]:40} score={qm.validation_score:.2f}" if qm else f"   ? NO DATA {skill_id}")

    # Demonstrate recommendations
    print("\n[3] Skill Recommendations:")
    print("   Query: 'optimization and constraints'")
    from em_cubed.skills.recommender import TaskRequirement
    req = TaskRequirement(
        category="OPTIMIZATION",
        surfaces=["python"],
        capabilities=["constraint", "optimize"],
        complexity="medium"
    )
    suggestions = recommender.recommend(req, limit=3)
    for i, s in enumerate(suggestions, 1):
        print(f"   {i}. {s.name} ({s.skill_id}) - relevance: {s.relevance_score:.1%}")

    # Demonstrate skill composition
    print("\n[4] Skill Composition Example:")
    if len(registry._skills) >= 2:
        skill_ids = list(registry._skills.keys())[:2]
        source, target = skill_ids[0], skill_ids[1]

        compatible = registry.find_compatible_skills(source)
        print(f"   Source: {source}")
        print(f"   Compatible targets: {len(compatible)} skills")
        if target in compatible:
            print(f"   Example composition: {source} → {target}")
            print(f"   Compatibility score: {registry._check_compatibility(registry.get_skill(source).output_schema, registry.get_skill(target).input_schema):.2%}")

    # Demonstrate quality metrics
    print("\n[5] Quality Metrics:")
    stats = registry.get_statistics()
    print(f"   Total skills: {stats['total_skills']}")
    print(f"   Domain coverage: {len(stats['domains'])} domains")
    print(f"   Surface distribution: {stats['surfaces']}")
    print(f"   Composition edges: {stats['composition_edges']}")

    # Telemetry demo
    print("\n[6] Telemetry Demo:")
    from em_cubed.skills.telemetry import record_skill_execution
    record_skill_execution(
        skill_id="demo/skill",
        success=True,
        execution_time_ms=123.4,
        token_usage=50,
        surface="python"
    )
    collector = TelemetryCollector()
    metrics = collector.get_skill_metrics("demo/skill")
    print(f"   Recorded execution, current metrics: {metrics}")

    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
