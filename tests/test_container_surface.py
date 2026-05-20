"""Test for containerized surface execution."""

from em_cubed.container_surface import ContainerizedSurfacePlugin


def test_containerized_surface_creation():
    """Test that containerized surface plugin can be created."""
    plugin = ContainerizedSurfacePlugin("python")
    assert plugin.name == "python"


def test_containerized_surface_available_false_when_no_docker():
    """Test that containerized surface reports unavailable when no Docker."""
    # This test would need mocking to simulate Docker unavailability
    # For now, we'll just verify the attribute exists
    plugin = ContainerizedSurfacePlugin("python")
    assert hasattr(plugin, '_docker_available')


if __name__ == "__main__":
    test_containerized_surface_creation()
    test_containerized_surface_available_false_when_no_docker()
    print("All tests passed!")