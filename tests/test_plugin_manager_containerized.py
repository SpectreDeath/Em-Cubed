"""Test for containerized execution in plugin manager."""
from em_cubed.plugin_manager import PluginManager


def test_plugin_manager_containerized_execution():
    """Test that plugin manager can enable containerized execution."""
    pm = PluginManager()
    
    # Initially no containerized surfaces
    assert len(pm._containerized_surfaces) == 0
    
    # Enable containerized execution for python
    pm.enable_containerized_execution("python", timeout=10.0)
    
    # Check that it's enabled
    assert "python" in pm._containerized_surfaces
    assert pm._containerized_timeouts["python"] == 10.0
    
    # Get the plugin - should return containerized version
    plugin = pm.get("python")
    assert plugin is not None
    # Note: We can't easily test if it's actually containerized without Docker
    
    # Disable containerized execution
    pm.disable_containerized_execution("python")
    
    # Check that it's disabled
    assert "python" not in pm._containerized_surfaces
    assert "python" not in pm._containerized_timeouts


if __name__ == "__main__":
    test_plugin_manager_containerized_execution()
    print("All tests passed!")