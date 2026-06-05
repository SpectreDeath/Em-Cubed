"""Additional tests for the CLI to improve coverage."""

import pytest
import json
from unittest.mock import patch, MagicMock

from em_cubed.cli import main


def test_main_no_args(capsys):
    """Test main with no arguments shows usage."""
    with patch('sys.argv', ['em3']):
        # When no command is provided, it prints help and exits normally
        main()
    
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower()
    assert "em-cubed: multi-surface skill framework" in captured.out.lower()


def test_handle_index_creates_directory_if_missing(tmp_path):
    """Test that index command handles missing skills directory."""
    skills_dir = tmp_path / "nonexistent"
    registry_file = tmp_path / "registry.json"
    
    with patch('sys.argv', ['em3', 'index', str(skills_dir), '--output', str(registry_file)]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Should exit with code 1 due to error handling in main()
        assert exc_info.value.code == 1


def test_handle_index_incremental(tmp_path):
    """Test incremental indexing."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    registry_file = tmp_path / "registry.json"
    
    # Create a simple skill
    skill_dir = skills_dir / "test"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("""---
name: Test Skill
Domain: Test
Version: 1.0.0
surfaces:
  - python
---
## Purpose
Test

```python
def test():
    return 1
```
""")
    
    with patch('sys.argv', ['em3', 'index', str(skills_dir), '--output', str(registry_file), '--incremental']):
        main()
    
    assert registry_file.exists()
    with open(registry_file) as f:
        registry = json.load(f)
    assert len(registry) == 1


def test_handle_search_with_error_result(tmp_path, capsys):
    """Test search command when results contain error."""
    # Mock search_registry to return error data
    with patch('em_cubed.cli.search_registry', return_value=[{"error": "Test error"}]):
        with patch('sys.argv', ['em3', 'search', 'test']):
            main()  # Should not raise exception, just print error and return
    
    captured = capsys.readouterr()
    assert "Error: Test error" in captured.err


def test_handle_serve_import_error(capsys):
    """Test serve command when uvicorn is not available."""
    with patch('sys.argv', ['em3', 'serve']):
        # Mock the specific import that's causing issues
        with patch.dict('sys.modules', {'uvicorn': None}):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    captured = capsys.readouterr()
    # The error is caught and handled in main() function
    assert "uvicorn is required" in captured.err


def test_handle_run_unknown_surface_exits_cleanly(capsys):
    """Test run command with unknown surface exits with SystemExit."""
    with patch('sys.argv', ['em3', 'run', '--surface', 'unknown', '--code', 'test']):
        with pytest.raises(SystemExit):
            main()
    
    captured = capsys.readouterr()
    assert "Surface 'unknown' not found" in captured.err


def test_handle_run_unavailable_surface(capsys):
    """Test run command with unavailable surface."""
    with patch('sys.argv', ['em3', 'run', '--surface', 'unavailable_surface', '--code', 'test']):
        with patch('em_cubed.cli.PluginManager') as mock_pm:
            mock_instance = MagicMock()
            mock_instance.get.return_value = MagicMock(available=False)
            mock_pm.return_value = mock_instance
    
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


def test_handle_run_async_path(tmp_path, capsys):
    """Test the async path of run command with tracing."""
    with patch('sys.argv', ['em3', 'run', '--surface', 'python', '--code', '1+1', '--trace']):
        with patch('em_cubed.cli.PluginManager') as mock_pm:
            mock_surface = MagicMock()
            mock_surface.available = True
            mock_surface.name = "python"
            # Mock the execute method to be an async method
            async def mock_execute(code, context):
                return {"status": "ok", "value": 2}
            mock_surface.execute = mock_execute
            
            mock_pm_instance = MagicMock()
            mock_pm_instance.get.return_value = mock_surface
            mock_pm_instance.get_available_surfaces.return_value = ["python"]
            mock_pm.return_value = mock_pm_instance
            
            main()  # Should not raise exception
            
    # Should have executed successfully and printed output
    captured = capsys.readouterr()
    assert '"status": "ok"' in captured.out
    assert '"value": 2' in captured.out
    assert "Execution Trace:" in captured.out


def test_handle_validate_calls_handler(tmp_path):
    """Test that validate command calls the handler."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    registry_file = tmp_path / "registry.json"
    
    with patch('sys.argv', ['em3', 'validate', '--skills-dir', str(skills_dir), '--registry', str(registry_file)]):
        with patch('em_cubed.cli._handle_validate') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()


def test_handle_quality_calls_handler(tmp_path):
    """Test that quality command calls the handler."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    registry_file = tmp_path / "registry.json"
    
    with patch('sys.argv', ['em3', 'quality', '--skills-dir', str(skills_dir), '--registry', str(registry_file)]):
        with patch('em_cubed.cli._handle_quality') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()


def test_handle_test_calls_handler_all(tmp_path):
    """Test that test command calls handler for all skills."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    with patch('sys.argv', ['em3', 'test', '--skills-dir', str(skills_dir)]):
        with patch('em_cubed.cli._handle_test') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()


def test_handle_test_calls_handler_specific(tmp_path):
    """Test that test command calls handler for specific skill."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    skill_dir = skills_dir / "test"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: Test\n---")
    
    with patch('sys.argv', ['em3', 'test', str(skill_dir)]):
        with patch('em_cubed.cli._handle_test') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()


def test_handle_recommend_calls_handler():
    """Test that recommend command calls the handler."""
    with patch('sys.argv', ['em3', 'recommend', 'test query', '--limit', '3']):
        with patch('em_cubed.cli._handle_recommend') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()


def test_handle_compose_calls_handler_simple():
    """Test that compose command calls handler for simple case."""
    with patch('sys.argv', ['em3', 'compose', '--source', 'skill1', '--target', 'skill2']):
        with patch('em_cubed.cli._handle_compose') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()


def test_handle_compose_calls_handler_goal():
    """Test that compose command calls handler for goal-based case."""
    with patch('sys.argv', ['em3', 'compose', '--source', 'skill1', '--goal', 'test goal']):
        with patch('em_cubed.cli._handle_compose') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()


def test_handle_trace_view_no_file(capsys):
    """Test trace-view with non-existent file."""
    with patch('sys.argv', ['em3', 'trace-view', '--file', '/nonexistent/traces.jsonl']):
        main()
    
    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()


def test_handle_trace_view_empty_file(tmp_path, capsys):
    """Test trace-view with empty file."""
    trace_file = tmp_path / "traces.jsonl"
    trace_file.write_text("")
    
    with patch('sys.argv', ['em3', 'trace-view', '--file', str(trace_file)]):
        main()
    
    captured = capsys.readouterr()
    assert "no traces" in captured.out.lower()


def test_handle_trace_view_skill_filter(tmp_path, capsys):
    """Test trace-view with skill filter."""
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


def test_handle_trace_view_verbose(tmp_path, capsys):
    """Test trace-view with verbose flag."""
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


def test_handle_surfaces_lists_surfaces(capsys):
    """Test surfaces command lists available surfaces."""
    with patch('sys.argv', ['em3', 'surfaces']):
        main()
    
    captured = capsys.readouterr()
    output = captured.out.strip()
    # Should list at least some surfaces
    assert "python" in output.lower()
    assert "AVAILABLE" in output
    assert "LOADED" in output


def test_handle_skill_info(tmp_path, capsys):
    """Test skill-info command."""
    registry_file = tmp_path / "registry.json"
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    # Create a skill directory and SKILL.md file
    skill_dir = skills_dir / "test"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("""---
name: Test Skill
domain: test
version: 1.0.0
surfaces:
  - python
---
## Purpose
Test skill for CLI testing

## Description
This is a test skill

```python
def test_func():
    return "success"
```
""")
    
    # Create registry by indexing
    with patch('sys.argv', ['em3', 'index', str(skills_dir), '--output', str(registry_file)]):
        main()
    
    # Now test skill-info with the correct skill ID (domain/name slugified)
    with patch('sys.argv', ['em3', 'skill-info', 'test/test-skill', '--registry', str(registry_file)]):
        with patch('em_cubed.cli.get_skill_metadata') as mock_get:
            mock_get.return_value = {
                "name": "Test Skill",
                "domain": "test",
                "version": "1.0.0",
                "description": "A test skill",
                "surfaces": ["python"],
                "purpose": "Test skill for CLI testing",
                "path": str(skill_file)
            }
            main()
    
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert "Test Skill" in output
    assert "test" in output


def test_handle_workflow_calls_handler(tmp_path):
    """Test that workflow command calls the handler."""
    workflow_file = tmp_path / "workflow.json"
    workflow_file.write_text('{"id": "test", "steps": []}')
    
    with patch('sys.argv', ['em3', 'workflow', str(workflow_file)]):
        with patch('em_cubed.cli._handle_workflow') as mock_handler:
            mock_handler.return_value = None
            main()
    
    mock_handler.assert_called_once()