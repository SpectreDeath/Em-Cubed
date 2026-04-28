import pytest
import json
from em_cubed.indexer import reindex, get_skill_metadata, extract_fenced_block, extract_prolog_tags, extract_hy_tags


class TestIndexerFunctions:
    @pytest.fixture
    def temp_skills_dir(self, tmp_path):
        """Create a temporary skills directory structure."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create test skill directories
        skill1_dir = skills_dir / "math_calculator"
        skill1_dir.mkdir()

        skill2_dir = skills_dir / "logic_solver"
        skill2_dir.mkdir()

        return skills_dir

    def test_extract_fenced_block_python(self):
        """Test extracting Python code blocks."""
        content = """
        Some text here.

        ```python
        def hello():
            return "world"
        ```

        More text.
        """
        result = extract_fenced_block(content, "python")
        assert result is not None
        assert "def hello():" in result
        assert 'return "world"' in result

    def test_extract_fenced_block_prolog(self):
        """Test extracting Prolog code blocks."""
        content = """
        ## Logic
        ```prolog
        parent(john, mary).
        parent(mary, ann).
        ```
        """
        result = extract_fenced_block(content, "prolog")
        assert result is not None
        assert "parent(john, mary)." in result

    def test_extract_fenced_block_hy(self):
        """Test extracting Hy code blocks."""
        content = """
        ```hy
        (defn greet [name]
          (+ "Hello " name))
        ```
        """
        result = extract_fenced_block(content, "hy")
        assert result is not None
        assert "(defn greet" in result

    def test_extract_fenced_block_no_match(self):
        """Test extracting non-existent language block."""
        content = "```python\ncode\n```"
        result = extract_fenced_block(content, "javascript")
        assert result is None

    def test_extract_prolog_tags(self):
        """Test extracting Prolog predicate names."""
        prolog_code = """
        parent(john, mary).
        grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
        ancestor(X, Y) :- parent(X, Y).
        ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
        """
        tags = extract_prolog_tags(prolog_code)
        assert "parent" in tags
        assert "grandparent" in tags
        assert "ancestor" in tags

    def test_extract_prolog_tags_exclude_builtins(self):
        """Test that Prolog builtins are excluded."""
        prolog_code = """
        not(X).
        is(X, Y).
        true.
        fail.
        custom_predicate(fact).
        """
        tags = extract_prolog_tags(prolog_code)
        assert "not" not in tags
        assert "is" not in tags
        assert "true" not in tags
        assert "fail" not in tags
        assert "custom_predicate" in tags  # This is not a builtin

    def test_extract_hy_tags(self):
        """Test extracting Hy function names."""
        hy_code = """
        (defn calculate [x y]
          (+ x y))

        (defn process-data [data]
          (map calculate data))
        """
        tags = extract_hy_tags(hy_code)
        assert "calculate" in tags
        assert "process-data" in tags

    def test_extract_hy_tags_complex(self):
        """Test extracting Hy functions with complex patterns."""
        hy_code = "(defn my-function? [x] (if (even? x) true false))"
        tags = extract_hy_tags(hy_code)
        assert "my-function?" in tags

    def test_get_skill_metadata_complete(self, temp_skills_dir):
        """Test extracting metadata from a complete SKILL.md file."""
        skill_file = temp_skills_dir / "math_calculator" / "SKILL.md"

        content = """---
name: Math Calculator
Domain: Mathematics
Version: 1.0.0
surfaces:
  - python
---

## Purpose
Perform mathematical calculations

## Description
A simple calculator that can add, subtract, multiply, and divide numbers.

```python
def add(x, y):
    return x + y

def multiply(a, b):
    return a * b
```

```prolog
add_prolog(X, Y, Result) :- Result is X + Y.
```
"""

        skill_file.write_text(content)

        metadata = get_skill_metadata(skill_file, temp_skills_dir)
        assert metadata is not None
        assert metadata["name"] == "Math Calculator"
        assert metadata["domain"] == "Mathematics"
        assert metadata["version"] == "1.0.0"
        assert metadata["purpose"] == "Perform mathematical calculations"
        assert metadata["surfaces"] == ["python", "prolog"]
        assert "add_prolog" in metadata["logic_tags"]  # from prolog
        assert "add" in metadata["heuristic_tags"]  # from python

    def test_get_skill_metadata_minimal(self, temp_skills_dir):
        """Test extracting metadata from minimal SKILL.md."""
        skill_file = temp_skills_dir / "logic_solver" / "SKILL.md"

        content = """---
name: Logic Solver
---

## Purpose
Solve logic puzzles
"""

        skill_file.write_text(content)

        metadata = get_skill_metadata(skill_file, temp_skills_dir)
        assert metadata is not None
        assert metadata["name"] == "Logic Solver"
        assert metadata["domain"] == "General"  # default
        assert metadata["purpose"] == "Solve logic puzzles"
        assert metadata["surfaces"] == ["python"]  # default

    def test_get_skill_metadata_no_frontmatter(self, temp_skills_dir):
        """Test handling files without frontmatter."""
        skill_file = temp_skills_dir / "math_calculator" / "SKILL.md"

        content = """
        ## Just content, no frontmatter
        Some description here.
        """

        skill_file.write_text(content)

        metadata = get_skill_metadata(skill_file, temp_skills_dir)
        assert metadata is None

    def test_get_skill_metadata_malformed_yaml(self, temp_skills_dir):
        """Test handling malformed YAML frontmatter."""
        skill_file = temp_skills_dir / "math_calculator" / "SKILL.md"

        content = """---
name: Test Skill
invalid: yaml: content: [
---
## Purpose
Test purpose
"""

        skill_file.write_text(content)

        metadata = get_skill_metadata(skill_file, temp_skills_dir)
        # Should handle gracefully, possibly return None or partial data
        # The current implementation uses yaml.safe_load which returns None on error
        assert metadata is None

    def test_reindex_basic(self, temp_skills_dir):
        """Test basic reindexing functionality."""
        # Create a skill file
        skill_file = temp_skills_dir / "math_calculator" / "SKILL.md"
        skill_file.write_text("""---
name: Math Calculator
---
## Purpose
Calculate math
""")

        registry_file = temp_skills_dir.parent / "registry.json"
        reindex(temp_skills_dir, registry_file)

        assert registry_file.exists()

        with open(registry_file) as f:
            registry = json.load(f)

        assert len(registry) == 1
        assert registry[0]["name"] == "Math Calculator"

    def test_reindex_multiple_skills(self, temp_skills_dir):
        """Test reindexing multiple skills."""
        # Create multiple skill files
        skill1_file = temp_skills_dir / "math_calculator" / "SKILL.md"
        skill1_file.write_text("""---
name: Math Calculator
surfaces: [python]
---
## Purpose
Calculate math
""")

        skill2_file = temp_skills_dir / "logic_solver" / "SKILL.md"
        skill2_file.write_text("""---
name: Logic Solver
surfaces: [prolog, python]
---
## Purpose
Solve logic
""")

        registry_file = temp_skills_dir.parent / "registry.json"
        reindex(temp_skills_dir, registry_file)

        with open(registry_file) as f:
            registry = json.load(f)

        assert len(registry) == 2

        # Check multi-surface counting
        multi_surface = [s for s in registry if len(s.get("surfaces", [])) > 1]
        single_surface = [s for s in registry if len(s.get("surfaces", [])) <= 1]

        assert len(multi_surface) == 1  # Logic Solver
        assert len(single_surface) == 1  # Math Calculator

    def test_reindex_skill_variants(self, temp_skills_dir):
        """Test reindexing SKILL.md and SKILL_*.md variants."""
        # Create SKILL.md
        skill1_file = temp_skills_dir / "math_calculator" / "SKILL.md"
        skill1_file.write_text("""---
name: Main Calculator
---
## Purpose
Main calculator
""")

        # Create SKILL_add.md
        skill2_file = temp_skills_dir / "math_calculator" / "SKILL_add.md"
        skill2_file.write_text("""---
name: Addition Module
---
## Purpose
Addition operations
""")

        registry_file = temp_skills_dir.parent / "registry.json"
        reindex(temp_skills_dir, registry_file)

        with open(registry_file) as f:
            registry = json.load(f)

        assert len(registry) == 2
        names = {skill["name"] for skill in registry}
        assert "Main Calculator" in names
        assert "Addition Module" in names
