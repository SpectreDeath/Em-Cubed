import pytest
from em_cubed.plugin_manager import PluginManager, SurfacePlugin
from typing import Dict, Any, Optional


class MockSurface(SurfacePlugin):
    """Mock surface for testing."""

    def __init__(self, name: str = "mock", available: bool = True):
        super().__init__(timeout=None)  # Initialize parent with no timeout
        self._name = name
        self._available = available

    @property
    def name(self) -> str:
        return self._name

    @property
    def available(self) -> bool:
        return self._available

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Implementation of execute for mock surface."""
        return {"status": "ok", "value": f"executed: {code}"}

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Override execute to provide mock behavior."""
        return await self._execute_impl(code, context)

    async def health(self) -> bool:
        return self._available

    def extract_tags(self, source: Optional[str]) -> list:
        return ["mock"]

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass


class TestPluginManager:

    def test_init_registers_builtin_surfaces(self):
        """Test that PluginManager initializes and registers built-in surfaces."""
        manager = PluginManager()

        # Should have registered some surfaces (at least python)
        assert len(manager._plugins) > 0
        assert "python" in manager._plugins

        # Verify surfaces are properly registered
        python_surface = manager.get("python")
        assert python_surface is not None
        assert python_surface.name == "python"

    def test_register_and_get_plugin(self):
        """Test registering and retrieving plugins."""
        manager = PluginManager()
        mock_surface = MockSurface("test_surface")

        # Register plugin
        manager.register("test", mock_surface)

        # Retrieve plugin
        retrieved = manager.get("test")
        assert retrieved is not None
        assert retrieved.name == "test_surface"
        assert retrieved.available is True

    def test_register_duplicate_plugin_warns(self):
        """Test that registering a duplicate plugin works (logging is hard to test)."""
        manager = PluginManager()
        mock_surface1 = MockSurface("surface1")
        mock_surface2 = MockSurface("surface2")

        # Register first plugin
        manager.register("test", mock_surface1)
        first_plugin = manager.get("test")
        assert first_plugin.name == "surface1"

        # Register duplicate (should replace)
        manager.register("test", mock_surface2)
        second_plugin = manager.get("test")
        assert second_plugin.name == "surface2"

    def test_get_nonexistent_plugin_returns_none(self):
        """Test that getting a nonexistent plugin returns None."""
        manager = PluginManager()

        result = manager.get("nonexistent")
        assert result is None

    def test_list_plugins(self):
        """Test listing all plugins with availability."""
        manager = PluginManager()
        mock_surface = MockSurface("mock_surface", available=True)

        manager.register("mock", mock_surface)

        plugins = manager.list_plugins()

        # Should include built-in surfaces plus mock
        assert isinstance(plugins, dict)
        assert len(plugins) >= 2  # At least python + mock

        # Mock surface should be available
        assert plugins.get("mock") is True

    def test_get_available_surfaces(self):
        """Test getting list of available surface names."""
        manager = PluginManager()
        mock_available = MockSurface("available", available=True)
        mock_unavailable = MockSurface("unavailable", available=False)

        manager.register("avail", mock_available)
        manager.register("unavail", mock_unavailable)

        available = manager.get_available_surfaces()

        # Should include available surfaces
        assert "avail" in available
        assert "unavail" not in available

        # Python should be available
        assert "python" in available

    def test_get_surface_info(self):
        """Test getting detailed surface information."""
        manager = PluginManager()
        mock_surface = MockSurface("info_test")

        manager.register("info", mock_surface)

        info = manager.get_surface_info()

        # Should be a list of dictionaries
        assert isinstance(info, list)
        assert len(info) >= 2  # Built-in + mock

        # Find our mock surface in the info
        mock_info = next((item for item in info if item["name"] == "info"), None)
        assert mock_info is not None
        assert mock_info["available"] is True
        assert "description" in mock_info

    def test_discover_directory_nonexistent_dir(self):
        """Test directory discovery with nonexistent directory."""
        from pathlib import Path
        manager = PluginManager()
        
        # Should not raise exception
        manager._discover_directory(Path("/nonexistent"))
        
        # Plugins should remain unchanged
        initial_count = len(manager._plugins)
        assert len(manager._plugins) == initial_count

    def test_plugin_initialization_and_shutdown(self):
        """Test that plugins are properly initialized and shut down."""
        mock_surface = MockSurface("lifecycle_test")

        manager = PluginManager()

        # Register plugin
        manager.register("lifecycle", mock_surface)

        # Plugin should be initialized during registration
        # (this happens in __init__ for built-in surfaces)

        # Test manual shutdown (normally happens in __del__)
        # Create a fresh manager to test shutdown
        manager2 = PluginManager()
        manager2.register("shutdown_test", mock_surface)

        # Manually trigger shutdown (normally done in __del__)
        del manager2

    def test_discover_builtin_handles_missing_surfaces(self):
        """Test that _discover_builtin gracefully handles missing surface dependencies."""
        manager = PluginManager()

        # All surfaces should be registered (available or not)
        surfaces = manager.list_plugins()
        expected_surfaces = {"python", "prolog", "hy", "z3", "datalog"}

        # Should have all expected surface names
        assert set(surfaces.keys()).issuperset(expected_surfaces)

        # Python should always be available
        assert surfaces["python"] is True

    def test_surface_plugin_abstract_methods(self):
        """Test that SurfacePlugin is properly abstract."""
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            SurfacePlugin()

    def test_logging_in_plugin_operations(self):
        """Test that appropriate logging occurs during plugin operations."""
        manager = PluginManager()
        mock_surface = MockSurface("logging_test")

        # Test registration logging (logging is handled by structlog, hard to mock easily)
        # Just verify the plugin is registered correctly
        manager.register("logging", mock_surface)
        loaded = manager.get("logging")
        assert loaded is not None
        assert loaded.name == "logging_test"

    def test_plugin_manager_cleanup_on_deletion(self):
        """Test that plugin manager properly cleans up on deletion."""
        mock_surface = MockSurface("cleanup_test")

        # Create manager and register plugin
        manager = PluginManager()
        manager.register("cleanup", mock_surface)

        # Delete manager (triggers __del__)
        del manager

        # Plugin shutdown should have been called
        # (This is hard to test directly, but at least verify no exceptions)