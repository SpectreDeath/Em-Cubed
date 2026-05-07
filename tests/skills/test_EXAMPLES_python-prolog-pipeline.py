"""Tests for the python-prolog-pipeline example skill.

Demonstrates the recommended pattern for testing multi-surface skills.
"""
import pytest
from pathlib import Path


class TestPythonPrologPipelineSkill:
    """Test the python-prolog-pipeline example skill."""

    def test_metadata_valid(self):
        """Test that skill metadata is valid."""
        from em_cubed.indexer import get_skill_metadata

        skill_file = Path("skills/EXAMPLES/python-prolog-pipeline/SKILL.md")
        if not skill_file.exists():
            pytest.skip("Example skill not installed")

        metadata = get_skill_metadata(skill_file, Path("skills"))
        assert metadata is not None
        assert metadata["name"] == "python-prolog-pipeline"
        assert metadata["domain"] == "EXAMPLES"
        assert "python" in metadata.get("surfaces", [])

    def test_skill_file_parses(self):
        """Test that the skill file can be parsed and indexed."""
        from em_cubed.indexer import reindex

        skill_file = Path("skills/EXAMPLES/python-prolog-pipeline/SKILL.md")
        if not skill_file.exists():
            pytest.skip("Example skill not installed")

        skills_dir = Path("skills")
        registry_file = Path("registry.json")
        reindex(skills_dir, registry_file)

        import json
        data = json.loads(registry_file.read_text())
        matching = [s for s in data if s["name"] == "python-prolog-pipeline"]
        assert len(matching) == 1
        assert "EXAMPLES" in matching[0].get("path", "")

    def test_skill_execution_via_executor(self):
        """Test skill execution through SkillExecutor (integration test)."""
        pytest.importorskip("pyswip", reason="PySWIP not installed")

        from em_cubed.indexer import reindex
        from em_cubed.plugin_manager import PluginManager
        from em_cubed.skills.registry import SkillRegistry
        from em_cubed.skills.executor import SkillExecutor, SkillExecutionRequest
        import asyncio

        skill_file = Path("skills/EXAMPLES/python-prolog-pipeline/SKILL.md")
        if not skill_file.exists():
            pytest.skip("Example skill not installed")

        skills_dir = Path("skills")
        registry_file = Path("registry.json")
        reindex(skills_dir, registry_file)

        registry = SkillRegistry(skills_dir, registry_file)
        plugin_manager = PluginManager()
        executor = SkillExecutor(plugin_manager, registry, skills_dir)

        request = SkillExecutionRequest(
            skill_id="EXAMPLES/python-prolog-pipeline",
            input_data={
                "edges": [["a", "b"], ["b", "c"]],
                "start": "a",
                "end": "c"
            }
        )

        result = asyncio.run(executor.execute(request))
        assert result.success, f"Execution failed: {result.error}"
        assert result.output is not None
        assert result.output["count"] == 3
        assert result.output["path"] == ["a", "b", "c"]
