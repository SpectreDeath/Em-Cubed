"""Tests for the skill executor module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import time

from src.em_cubed.skills.executor import (
    SkillExecutor,
    SkillExecutionRequest,
    SkillExecutionResult,
    TelemetryProxy,
    get_skill_executor,
    initialize_executor
)
from src.em_cubed.skills.registry import SkillRegistry
from src.em_cubed.skills.metadata import SkillMetadata
from src.em_cubed.skills.metadata import SkillMetadata
from src.em_cubed.skills.telemetry import SkillTelemetry, TraceContext


class TestSkillExecutor:
    """Test cases for SkillExecutor class."""
    
    @pytest.fixture
    def mock_plugin_manager(self):
        """Create a mock plugin manager."""
        manager = Mock()
        manager.get.return_value = Mock()
        manager.get.return_value.available = True
        return manager
    
    @pytest.fixture
    def mock_registry(self):
        """Create a mock skill registry."""
        registry = Mock(spec=SkillRegistry)
        return registry
    
    @pytest.fixture
    def temp_skills_dir(self):
        """Create a temporary skills directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def skill_executor(self, mock_plugin_manager, mock_registry, temp_skills_dir):
        """Create a SkillExecutor instance for testing."""
        return SkillExecutor(mock_plugin_manager, mock_registry, temp_skills_dir)
    
    @pytest.fixture
    def sample_skill(self):
        """Create a sample skill for testing."""
        skill = SkillMetadata(
            name="Test Skill",
            domain="test",
            version="0.1.0",
            surfaces=["python"],
            purpose="Test skill",
            description="A test skill",
            dependencies=[],
            input_schema={},
            output_schema={},
            capabilities={},
            compatibility={},
            quality_thresholds={},
            metrics={},
            skill_id="test/skill",
            path=str(Path(__file__).parent.parent / "skills" / "test_skill"),
            schema_version=1,
            tags=[],
            created_at=None,
            updated_at=None
        )
        return skill
    
    def test_initialization(self, mock_plugin_manager, mock_registry, temp_skills_dir):
        """Test SkillExecutor initialization."""
        executor = SkillExecutor(mock_plugin_manager, mock_registry, temp_skills_dir)
        
        assert executor.plugin_manager == mock_plugin_manager
        assert executor.registry == mock_registry
        assert executor.skills_dir == temp_skills_dir
        assert executor._skill_cache == {}
        assert executor.logger is not None
    
    def test_load_skill_code_cached(self, skill_executor, mock_registry):
        """Test that skill code loading is cached."""
        # Setup
        skill_id = "test/skill"
        mock_skill = Mock()
        mock_skill.path = "/fake/path/skill.md"
        mock_registry.get_skill.return_value = mock_skill
        
        # Mock file reading
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value="```python\nprint('hello')\n```"):
                # First call
                result1 = skill_executor._load_skill_code(skill_id)
                
                # Second call should use cache
                result2 = skill_executor._load_skill_code(skill_id)
                
                # Both should return the same result
                assert result1 == result2
                assert "python" in result1
                assert result1["python"] == "print('hello')"
    
    def test_load_skill_code_not_found(self, skill_executor, mock_registry):
        """Test loading skill code when file not found."""
        # Setup
        skill_id = "nonexistent/skill"
        mock_skill = Mock()
        mock_skill.path = "/fake/path/nonexistent/skill.md"
        mock_registry.get_skill.return_value = mock_skill
        
        # Mock file not found
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Skill file not found"):
                skill_executor._load_skill_code(skill_id)
    
    def test_load_skill_code_multiple_blocks(self, skill_executor, mock_registry):
        """Test loading skill code with multiple language blocks."""
        # Setup
        skill_id = "multi/skill"
        mock_skill = Mock()
        mock_skill.path = "/fake/path/skill.md"
        mock_registry.get_skill.return_value = mock_skill
        
        content = """```python
def hello():
    return "world"
```

```prolog
hello(world).
```

```javascript
console.log("hello");
```
"""
        
        # Mock file reading
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=content):
                result = skill_executor._load_skill_code(skill_id)
                
                assert "python" in result
                assert "prolog" in result
                assert "javascript" in result
                assert result["python"] == "def hello():\n    return \"world\""
                assert result["prolog"] == "hello(world)."
                assert result["javascript"] == "console.log(\"hello\");"
    
    def test_execute_skill_not_found(self, skill_executor, mock_registry):
        """Test execution when skill is not found in registry."""
        # Setup
        request = SkillExecutionRequest(
            skill_id="nonexistent/skill",
            input_data={"param": "value"}
        )
        mock_registry.get_skill.return_value = None
        
        # Execute
        import asyncio
        result = asyncio.run(skill_executor.execute(request))
        
        # Verify
        assert not result.success
        assert "not found in registry" in result.error
        assert result.skill_id == "nonexistent/skill"
    
    def test_execute_surface_not_available(self, skill_executor, mock_plugin_manager, mock_registry, sample_skill):
        """Test execution when requested surface is not available."""
        # Setup
        mock_registry.get_skill.return_value = sample_skill
        mock_plugin_manager.get.return_value = Mock()
        mock_plugin_manager.get.return_value.available = False  # Surface not available
        
        request = SkillExecutionRequest(
            skill_id="test/skill",
            input_data={"param": "value"},
            surface="python"  # Requesting python surface
        )
        
        # Execute
        import asyncio
        result = asyncio.run(skill_executor.execute(request))
        
        # Verify
        assert not result.success
        assert "not available" in result.error
        assert result.surface_used == "python"
        assert result.skill_id == "test/skill"
    
    def test_execute_no_surface_implementation(self, skill_executor, mock_plugin_manager, mock_registry, sample_skill):
        """Test execution when skill has no implementation for requested surface."""
        # Setup
        mock_registry.get_skill.return_value = sample_skill
        mock_plugin = Mock()
        mock_plugin.available = True
        mock_plugin_manager.get.return_value = mock_plugin
        
        # Mock skill code loading to return no python implementation
        with patch.object(skill_executor, '_load_skill_code', return_value={"prolog": "hello(world)."}):
            request = SkillExecutionRequest(
                skill_id="test/skill",
                input_data={"param": "value"},
                surface="python"  # Requesting python but only prolog available
            )
            
            # Execute
            import asyncio
            result = asyncio.run(skill_executor.execute(request))
            
            # Verify
            assert not result.success
            assert "No python implementation found in skill" in result.error
            assert result.surface_used == "python"
    
    def test_telemetry_proxy_sync(self):
        """Test TelemetryProxy with synchronous execution."""
        # Setup
        mock_surface = Mock()
        mock_surface.execute_sync.return_value = {"status": "ok", "value": "result"}
        mock_trace_ctx = Mock()
        mock_span = Mock()
        mock_trace_ctx.start_span.return_value = mock_span
        
        proxy = TelemetryProxy(mock_surface, mock_trace_ctx)
        
        # Execute
        result = proxy.execute_sync("test code", input_data={})
        
        # Verify
        assert result == {"status": "ok", "value": "result"}
        mock_surface.execute_sync.assert_called_once_with("test code", input_data={})
        mock_trace_ctx.start_span.assert_called_once()
        mock_trace_ctx.end_span.assert_called_once()
    
    def test_telemetry_proxy_async(self):
        """Test TelemetryProxy with asynchronous execution."""
        import asyncio
        
        # Setup
        mock_surface = Mock()
        mock_trace_ctx = Mock()
        mock_span = Mock()
        mock_trace_ctx.start_span.return_value = mock_span
        
        # Mock async execution
        async def mock_execute(*args, **kwargs):
            return {"status": "ok", "value": "async_result"}
        
        mock_surface.execute = mock_execute
        
        proxy = TelemetryProxy(mock_surface, mock_trace_ctx)
        
        # Execute
        async def test_async():
            return await proxy.execute("test code", input_data={})
        
        result = asyncio.run(test_async())
        
        # Verify
        assert result == {"status": "ok", "value": "async_result"}
        mock_trace_ctx.start_span.assert_called_once()
        mock_trace_ctx.end_span.assert_called_once()
    
    def test_initialize_executor(self):
        """Test global executor initialization."""
        # Setup
        mock_plugin_manager = Mock()
        mock_registry = Mock()
        skills_dir = Path("/tmp/skills")
        
        # Execute
        executor = initialize_executor(mock_plugin_manager, mock_registry, skills_dir)
        
        # Verify
        assert isinstance(executor, SkillExecutor)
        assert executor.plugin_manager == mock_plugin_manager
        assert executor.registry == mock_registry
        assert executor.skills_dir == skills_dir
        
        # Verify global executor is set
        from src.em_cubed.skills.executor import _global_executor
        assert _global_executor == executor
    
    def test_get_skill_executor(self):
        """Test getting global skill executor."""
        # Initially should be None
        assert get_skill_executor() is None
        
        # Set up global executor
        mock_plugin_manager = Mock()
        mock_registry = Mock()
        skills_dir = Path("/tmp/skills")
        executor = initialize_executor(mock_plugin_manager, mock_registry, skills_dir)
        
        # Now should return the executor
        assert get_skill_executor() == executor


class TestSkillExecutionRequest:
    """Test cases for SkillExecutionRequest dataclass."""
    
    def test_default_creation(self):
        """Test creating request with default values."""
        request = SkillExecutionRequest(
            skill_id="test/skill",
            input_data={"key": "value"}
        )
        
        assert request.skill_id == "test/skill"
        assert request.input_data == {"key": "value"}
        assert request.surface is None
        assert request.timeout is None
        assert request.context is None
    
    def test_explicit_creation(self):
        """Test creating request with explicit values."""
        request = SkillExecutionRequest(
            skill_id="test/skill",
            input_data={"key": "value"},
            surface="python",
            timeout=30.0,
            context={"extra": "data"}
        )
        
        assert request.skill_id == "test/skill"
        assert request.input_data == {"key": "value"}
        assert request.surface == "python"
        assert request.timeout == 30.0
        assert request.context == {"extra": "data"}


class TestSkillExecutionResult:
    """Test cases for SkillExecutionResult dataclass."""
    
    def test_successful_result(self):
        """Test creating successful execution result."""
        result = SkillExecutionResult(
            skill_id="test/skill",
            success=True,
            output={"result": "value"},
            execution_time_ms=150.5,
            surface_used="python",
            token_usage=42
        )
        
        assert result.skill_id == "test/skill"
        assert result.success is True
        assert result.output == {"result": "value"}
        assert result.error is None
        assert result.execution_time_ms == 150.5
        assert result.surface_used == "python"
        assert result.token_usage == 42
    
    def test_failed_result(self):
        """Test creating failed execution result."""
        result = SkillExecutionResult(
            skill_id="test/skill",
            success=False,
            output=None,
            error="Something went wrong",
            execution_time_ms=50.0,
            surface_used="prolog"
        )
        
        assert result.skill_id == "test/skill"
        assert result.success is False
        assert result.output is None
        assert result.error == "Something went wrong"
        assert result.execution_time_ms == 50.0
        assert result.surface_used == "prolog"
        assert result.token_usage == 0  # Default value


if __name__ == "__main__":
    pytest.main([__file__])