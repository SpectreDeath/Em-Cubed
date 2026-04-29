import pytest
import json

from unittest.mock import patch
from em_cubed.cli import main


class TestCLI:
    def test_index_command(self, tmp_path, capsys):
        """Test the index command."""
        # Create a test skill
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "test_skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: Test Skill
Domain: Test
Version: 1.0.0
surfaces:
  - python
---

## Purpose
Test skill

## Description
A test skill for CLI testing

```python
def test():
    return "hello"
```
""")

        registry_file = tmp_path / "registry.json"

        with patch('sys.argv', ['em3', 'index', str(skills_dir), '--output', str(registry_file)]):
            main()

        assert registry_file.exists()
        with open(registry_file) as f:
            registry = json.load(f)
        assert len(registry) == 1
        assert registry[0]["name"] == "Test Skill"

    def test_search_command(self, tmp_path, capsys):
        """Test the search command."""
        # Create a test registry
        registry_data = [
            {
                "name": "Test Skill",
                "domain": "Test",
                "purpose": "Test purpose",
                "description": "Test description",
                "surfaces": ["python"],
                "logic_tags": [],
                "heuristic_tags": ["test"],
                "path": "test",
            }
        ]
        registry_file = tmp_path / "registry.json"
        with open(registry_file, "w") as f:
            json.dump(registry_data, f)

        from em_cubed.search import WhooshSearchIndex
        with patch('sys.argv', ['em3', 'search', 'test', '--registry', str(registry_file)]):
            with patch('em_cubed.search.get_search_index', return_value=WhooshSearchIndex(tmp_path / "whoosh_index")):
                with patch('em_cubed.search._search_index', None):
                    main()

        captured = capsys.readouterr()
        results = json.loads(captured.out.strip())
        assert len(results) == 1
        assert results[0]["name"] == "Test Skill"

    @patch('uvicorn.run')
    def test_serve_command(self, mock_uvicorn, capsys):
        """Test the serve command."""
        with patch('sys.argv', ['em3', 'serve', '--host', '0.0.0.0', '--port', '8080']):
            main()

        mock_uvicorn.assert_called_once()
        # Check that it was called with the correct arguments
        call_args = mock_uvicorn.call_args
        assert call_args[1]['host'] == '0.0.0.0'
        assert call_args[1]['port'] == 8080

    def test_run_command_python(self, capsys):
        """Test the run command with Python."""
        with patch('sys.argv', ['em3', 'run', '--surface', 'python', '--code', '1 + 1']):
            main()

        captured = capsys.readouterr()
        result = json.loads(captured.out.strip())
        assert result["status"] == "ok"
        assert result["value"] == 2

    def test_run_command_unknown_surface(self, capsys):
        """Test the run command with unknown surface."""
        with patch('sys.argv', ['em3', 'run', '--surface', 'unknown', '--code', 'test']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "Surface 'unknown' not found" in captured.err

    def test_no_command(self, capsys):
        """Test running without command."""
        with patch('sys.argv', ['em3']):
            main()

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_invalid_command(self):
        """Test invalid command."""
        with patch('sys.argv', ['em3', 'invalid']):
            try:
                main()
                assert False, "Should have exited"
            except SystemExit:
                pass  # Expected