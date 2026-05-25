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

    def test_run_command_sqlite(self, capsys):
        """Test the run command with SQLite."""
        # Simple SELECT query; column name will be '1' if not aliased
        with patch('sys.argv', ['em3', 'run', '--surface', 'sqlite', '--code', 'SELECT 1']):
            main()

        captured = capsys.readouterr()
        result = json.loads(captured.out.strip())
        assert result["status"] == "ok"
        # SQLite returns list of rows; each row is a dict. For SELECT 1, column name is "1".
        # Result format: {"value": [{"1": 1}]}
        assert "value" in result
        rows = result["value"]
        assert isinstance(rows, list)
        assert len(rows) >= 1
        # The first row should have key "1" with value 1
        assert rows[0].get("1") == 1 or rows[0].get("value") == 1  # Accept aliased or plain

    def test_run_command_unknown_surface(self, capsys):
        """Test the run command with unknown surface."""
        with patch('sys.argv', ['em3', 'run', '--surface', 'unknown', '--code', 'test']):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        assert "Surface 'unknown' not found" in captured.err

    def test_surfaces_command(self, capsys):
        """Test the surfaces command lists surfaces."""
        with patch('sys.argv', ['em3', 'surfaces']):
            main()

        captured = capsys.readouterr()
        output = captured.out.strip()
        # At minimum should list python, prolog, hy surfaces
        assert "python" in output
        assert "prolog" in output
        assert "hy" in output
        # Header line should contain AVAILABLE, LOADED, DESCRIPTION
        assert "AVAILABLE" in output
        assert "LOADED" in output

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

    @patch('em_cubed.cli._handle_validate')
    def test_validate_command(self, mock_handler, tmp_path, capsys):
        """Test the validate command."""
        mock_handler.return_value = None
        
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        registry_file = tmp_path / "registry.json"
        
        with patch('sys.argv', ['em3', 'validate', '--skills-dir', str(skills_dir), '--registry', str(registry_file)]):
            main()
        
        mock_handler.assert_called_once()

    @patch('em_cubed.cli._handle_quality')
    def test_quality_command(self, mock_handler, tmp_path, capsys):
        """Test the quality command."""
        mock_handler.return_value = None
        
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        registry_file = tmp_path / "registry.json"
        
        with patch('sys.argv', ['em3', 'quality', '--skills-dir', str(skills_dir), '--registry', str(registry_file)]):
            main()

        # Handler is mocked, so no output - just verify it was called
        mock_handler.assert_called_once()

    @patch('em_cubed.cli._handle_test')
    def test_test_command_all(self, mock_handler, tmp_path, capsys):
        """Test the test command (all skills)."""
        mock_handler.return_value = None
        
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        
        with patch('sys.argv', ['em3', 'test', '--skills-dir', str(skills_dir)]):
            main()
        
        mock_handler.assert_called_once()

    @patch('em_cubed.cli._handle_test')
    def test_test_command_specific(self, mock_handler, tmp_path, capsys):
        """Test the test command (specific skill)."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_dir = skills_dir / "test_skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: Test Skill
Domain: Test
---
## Purpose\nTest\n```python\ndef test():\n    return 1\n```""")
        
        mock_handler.return_value = None
        
        with patch('sys.argv', ['em3', 'test', str(skill_dir)]):
            main()
        
        mock_handler.assert_called_once()

    @patch('em_cubed.cli._handle_recommend')
    def test_recommend_command(self, mock_handler, tmp_path, capsys):
        """Test the recommend command."""
        mock_handler.return_value = None
        
        with patch('sys.argv', ['em3', 'recommend', 'test query', '--limit', '3']):
            main()
        
        mock_handler.assert_called_once()

    @patch('em_cubed.cli._handle_compose')
    def test_compose_command_simple(self, mock_handler, tmp_path, capsys):
        """Test the compose command (simple)."""
        mock_handler.return_value = None
        
        with patch('sys.argv', ['em3', 'compose', '--source', 'skill1', '--target', 'skill2']):
            main()
        
        mock_handler.assert_called_once()

    @patch('em_cubed.cli._handle_compose')
    def test_compose_command_goal(self, mock_handler, tmp_path, capsys):
        """Test the compose command (goal-based)."""
        mock_handler.return_value = None

        with patch('sys.argv', ['em3', 'compose', '--source', 'skill1', '--goal', 'test goal']):
            main()

        mock_handler.assert_called_once()
        patch.stopall()

    def test_trace_view_command_no_file(self, capsys):
        """Test trace-view with non-existent file."""
        with patch('sys.argv', ['em3', 'trace-view', '--file', '/nonexistent/traces.jsonl']):
            main()

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower()

    def test_trace_view_command_empty_file(self, tmp_path, capsys):
        """Test trace-view with empty file."""
        trace_file = tmp_path / "traces.jsonl"
        trace_file.write_text("")

        with patch('sys.argv', ['em3', 'trace-view', '--file', str(trace_file)]):
            main()

        captured = capsys.readouterr()
        assert "no traces" in captured.out.lower()

    def test_trace_view_command_json_output(self, tmp_path, capsys):
        """Test trace-view with --json flag."""
        trace_file = tmp_path / "traces.jsonl"
        trace_file.write_text(
            '{"trace_id": "abc123", "skill_id": "test/skill", "success": true, '
            '"execution_time_ms": 100.0, "surface": "python", "timestamp": "2026-01-01T00:00:00Z", '
            '"spans": [{"surface": "prolog", "duration_ms": 50.0, "success": true}]}\n'
        )

        with patch('sys.argv', ['em3', 'trace-view', '--file', str(trace_file), '--json']):
            main()

        captured = capsys.readouterr()
        import json
        output = json.loads(captured.out.strip())
        assert len(output) == 1
        assert output[0]["trace_id"] == "abc123"

    def test_trace_view_command_skill_filter(self, tmp_path, capsys):
        """Test trace-view with --skill filter."""
        trace_file = tmp_path / "traces.jsonl"
        trace_file.write_text(
            '{"trace_id": "1", "skill_id": "other/skill", "success": true, '
            '"execution_time_ms": 100.0, "surface": "python", "timestamp": "2026-01-01T00:00:00Z", "spans": []}\n'
            '{"trace_id": "2", "skill_id": "test/skill", "success": true, '
            '"execution_time_ms": 200.0, "surface": "python", "timestamp": "2026-01-01T00:00:00Z", "spans": []}\n'
        )

        with patch('sys.argv', ['em3', 'trace-view', '--file', str(trace_file), '--skill', 'test/skill']):
            main()

        captured = capsys.readouterr()
        # Should only show trace with skill_id "test/skill"
        assert "test/skill" in captured.out
        assert "other/skill" not in captured.out

    def test_trace_view_command_verbose(self, tmp_path, capsys):
        """Test trace-view with --verbose flag."""
        trace_file = tmp_path / "traces.jsonl"
        trace_file.write_text(
            '{"trace_id": "abc123", "skill_id": "test/skill", "success": true, '
            '"execution_time_ms": 100.0, "surface": "python", "timestamp": "2026-01-01T00:00:00Z", '
            '"spans": [{"surface": "prolog", "duration_ms": 50.0, "success": true, "error": null, '
            '"input_data": {"query": "fact(X)"}, "output_data": {"X": "test"}}]}\n'
        )

        with patch('sys.argv', ['em3', 'trace-view', '--file', str(trace_file), '--verbose']):
            main()

        captured = capsys.readouterr()
        assert "prolog" in captured.out
        assert "Input:" in captured.out or "Input" in captured.out