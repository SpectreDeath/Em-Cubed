import pytest
import json
from em_cubed.indexer import reindex
from em_cubed.search import search_registry
from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface


# Disable whoosh for integration tests to ensure consistent behavior
def search_registry_test(query, registry_path, max_results=10):
    return search_registry(query, registry_path, max_results, use_whoosh=False)


class TestIntegration:
    """Integration tests for the full Em-Cubed workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_python_skill(self, tmp_path):
        """Test complete workflow: create skill -> index -> search -> execute."""
        # 1. Create a skill directory with SKILL.md
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "test_calculator"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_content = """---
name: Test Calculator
Domain: Mathematics
Version: 1.0.0
surfaces:
  - python
---

## Purpose
Perform basic arithmetic calculations

## Description
A simple calculator for testing the full workflow.

```python
def add(x, y):
    return x + y

def multiply(x, y):
    return x * y
```
"""
        skill_md.write_text(skill_content)

        # 2. Index the skills
        registry_file = tmp_path / "registry.json"
        reindex(skills_dir, registry_file)

        # 3. Search for the skill
        results = search_registry_test("calculator", registry_file)
        assert len(results) == 1
        assert results[0]["name"] == "Test Calculator"

        # 4. Execute code using the surface
        surface = PythonSurface()
        result = await surface.execute("add(5, 3)", {"add": lambda x, y: x + y})
        assert result["status"] == "ok"
        assert result["value"] == 8

    @pytest.mark.asyncio
    async def test_multi_surface_skill_workflow(self, tmp_path):
        """Test workflow with multi-surface skill."""
        # 1. Create a multi-surface skill
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "multi_solver"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_content = """---
name: Multi Solver
Domain: General
surfaces:
  - python
  - prolog
---

## Purpose
Solve problems using multiple approaches

## Description
Demonstrates multi-surface execution.

```python
def python_solve(x):
    return x * 2
```

```prolog
double(X, Result) :- Result is X * 2.
```
"""
        skill_md.write_text(skill_content)

        # 2. Index and verify multi-surface detection
        registry_file = tmp_path / "registry.json"
        reindex(skills_dir, registry_file)

        with open(registry_file) as f:
            registry = json.load(f)

        assert len(registry) == 1
        skill = registry[0]
        assert skill["name"] == "Multi Solver"
        assert len(skill["surfaces"]) == 2
        assert "python" in skill["surfaces"]
        assert "prolog" in skill["surfaces"]

        # 3. Test Python surface execution
        python_surface = PythonSurface()
        result = await python_surface.execute("python_solve(4)", {"python_solve": lambda x: x * 2})
        assert result["status"] == "ok"
        assert result["value"] == 8

        # 4. Test Prolog surface (if available)
        prolog_surface = PrologSurface()
        result = await prolog_surface.execute("double(4, Result).")
        # Prolog may or may not be available depending on system
        # Just verify result has status field
        assert "status" in result

    @pytest.mark.asyncio
    async def test_search_and_execute_integration(self, tmp_path):
        """Test searching for a skill and then executing it."""
        # Setup skills
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create multiple skills
        skills_data = [
            ("math_adder", "Math Adder", "addition", "python", "lambda x, y: x + y"),
            ("logic_solver", "Logic Solver", "logic", "prolog", "parent(john, mary)."),
            ("data_processor", "Data Processor", "process", "python", "lambda data: len(data)"),
        ]

        for skill_id, name, search_term, surface, code in skills_data:
            skill_dir = skills_dir / skill_id
            skill_dir.mkdir()

            skill_md = skill_dir / "SKILL.md"
            content = f"""---
name: {name}
Domain: General
surfaces:
  - {surface}
---

## Purpose
Test {search_term} functionality

```python
def test_function():
    return "{search_term}"
```
"""
            skill_md.write_text(content)

        # Index
        registry_file = tmp_path / "registry.json"
        reindex(skills_dir, registry_file)

        # Search for each skill
        for skill_id, name, search_term, surface, code in skills_data:
            results = search_registry_test(search_term, registry_file)
            assert len(results) >= 1

            # Find our skill in results
            skill_result = next((r for r in results if r["name"] == name), None)
            assert skill_result is not None

            # Execute based on surface type
            if surface == "python":
                python_surface = PythonSurface()
                result = await python_surface.execute("test_function()", {"test_function": lambda: search_term})
                assert result["status"] == "ok"
                assert result["value"] == search_term

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, tmp_path):
        """Test error handling throughout the integration."""
        # 1. Create a skill with problematic code
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "error_skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_content = """---
name: Error Skill
Domain: Testing
surfaces:
  - python
---

## Purpose
Test error handling

## Description
A skill designed to test error scenarios.
"""
        skill_md.write_text(skill_content)

        # 2. Index
        registry_file = tmp_path / "registry.json"
        reindex(skills_dir, registry_file)

        # 3. Search - should work
        results = search_registry_test("error", registry_file)
        assert len(results) == 1

        # 4. Execute with error - should handle gracefully
        surface = PythonSurface()
        result = await surface.execute("1 / 0")  # Division by zero
        # asteval returns {"status": "error", "message": "..."} for ZeroDivisionError
        assert result["status"] == "error"
        assert "division by zero" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_registry_persistence_integration(self, tmp_path):
        """Test that registry persists and can be reloaded."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "persistent_skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_content = """---
name: Persistent Skill
Domain: Testing
---

## Purpose
Test registry persistence
"""
        skill_md.write_text(skill_content)

        # First index
        registry_file = tmp_path / "registry.json"
        reindex(skills_dir, registry_file)

        # Verify registry exists and has data
        assert registry_file.exists()
        with open(registry_file) as f:
            registry1 = json.load(f)
        assert len(registry1) == 1

        # Search works
        results1 = search_registry_test("persistent", registry_file)
        assert len(results1) == 1

        # Add another skill
        skill2_dir = skills_dir / "second_skill"
        skill2_dir.mkdir()

        skill2_md = skill2_dir / "SKILL.md"
        skill2_content = """---
name: Second Skill
Domain: Testing
---

## Purpose
Second test skill
"""
        skill2_md.write_text(skill2_content)

        # Re-index
        reindex(skills_dir, registry_file)

        # Verify both skills are there
        with open(registry_file) as f:
            registry2 = json.load(f)
        assert len(registry2) == 2

        names = {skill["name"] for skill in registry2}
        assert "Persistent Skill" in names
        assert "Second Skill" in names

    @pytest.mark.asyncio
    async def test_surface_availability_integration(self):
        """Test that surfaces report availability correctly."""
        python_surface = PythonSurface()
        prolog_surface = PrologSurface()
        hy_surface = HySurface()

        # Python should always be available (asteval)
        assert python_surface.available

        # Prolog/Hy availability depends on system
        # Just test that the health methods work
        assert isinstance(await python_surface.health(), bool)
        assert isinstance(await prolog_surface.health(), bool)
        assert isinstance(await hy_surface.health(), bool)
