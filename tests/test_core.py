from pathlib import Path
import tempfile
from em_cubed.indexer import reindex, get_skill_metadata


class TestIndexer:
    def test_get_skill_metadata_basic(self):
        """Test extracting metadata from a valid SKILL.md."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_p = Path(tmpdir)
            skills_dir = tmpdir_p / "skills"
            skills_dir.mkdir()
            skill_dir = skills_dir / "test_skill"
            skill_dir.mkdir()

            skill_file = skill_dir / "SKILL.md"
            skill_content = """---
name: Test Skill
Domain: Testing
Version: 1.0.0
---
## Purpose
Test purpose here.

## Description
Test description here.

```python
def hello():
    return "world"
```
"""
            skill_file.write_text(skill_content, encoding="utf-8")

            metadata = get_skill_metadata(skill_file, skills_dir)
            assert metadata is not None
            assert metadata["name"] == "Test Skill"
            assert metadata["domain"] == "Testing"
            assert metadata["surfaces"] == ["python"]

    def test_reindex(self):
        """Test reindexing skills to registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_p = Path(tmpdir)
            skills_dir = tmpdir_p / "skills"
            skills_dir.mkdir()
            skill_dir = skills_dir / "test_skill"
            skill_dir.mkdir()

            skill_file = skill_dir / "SKILL.md"
            skill_content = """---
name: Test Skill
Domain: Testing
---
## Purpose
Test purpose.
"""
            skill_file.write_text(skill_content, encoding="utf-8")

            registry_file = tmpdir_p / "registry.json"
            reindex(skills_dir, registry_file)

            assert registry_file.exists()
            import json

            with open(registry_file, encoding="utf-8") as f:
                registry = json.load(f)
            assert len(registry) == 1
            assert registry[0]["name"] == "Test Skill"
