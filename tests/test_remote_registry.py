"""Tests for remote skill registry functionality."""
import json
import tempfile
from pathlib import Path
import pytest
from unittest.mock import Mock, patch

from em_cubed.skills.remote_registry import RemoteSkillRegistry
from em_cubed.skills.registry import SkillRegistry
from em_cubed.skills.metadata import SkillMetadata


def test_remote_registry_creation():
    """Test that RemoteSkillRegistry can be created."""
    # Create a temporary local registry
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")  # Empty registry
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote_registry = RemoteSkillRegistry(local_registry)
        
        assert remote_registry.local_registry == local_registry
        assert remote_registry.cache_dir.exists()


def test_add_remove_registry():
    """Test adding and removing remote registries."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote_registry = RemoteSkillRegistry(local_registry)
        
        # Add a registry
        remote_registry.add_registry(
            "test-registry", 
            "https://example.com/api", 
            token="test-token",
            sync_interval=60
        )
        
        assert "test-registry" in remote_registry._registries
        config = remote_registry._registries["test-registry"]
        assert config["url"] == "https://example.com/api"
        assert config["token"] == "test-token"
        assert config["sync_interval"] == 60
        
        # Remove the registry
        result = remote_registry.remove_registry("test-registry")
        assert result is True
        assert "test-registry" not in remote_registry._registries
        
        # Try to remove non-existent registry
        result = remote_registry.remove_registry("non-existent")
        assert result is False


def test_sync_registry_not_due():
    """Test that sync is skipped when not due."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote_registry = RemoteSkillRegistry(local_registry)
        
        # Add a registry with short sync interval
        remote_registry.add_registry("test", "https://example.com", sync_interval=10)
        
        # Manually set last sync to recent time
        import time
        remote_registry._last_sync["test"] = time.time()
        
        # Try to sync - should return False (not done)
        result = remote_registry.sync_registry("test", force=False)
        assert result is False


def test_sync_registry_force():
    """Test that sync can be forced."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote_registry = RemoteSkillRegistry(local_registry)
        
        # Add a registry
        remote_registry.add_registry("test", "https://example.com", sync_interval=10)
        
        # Even if not due, force should work
        with patch.object(remote_registry, '_fetch_remote_registry', return_value=[]):
            with patch.object(remote_registry, '_load_cached_registry', return_value=None):
                result = remote_registry.sync_registry("test", force=True)
                # Should return True (attempted sync)
                assert result is True


def test_load_cached_registry():
    """Test loading cached registry data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote_registry = RemoteSkillRegistry(local_registry)
        
        # Add a registry
        remote_registry.add_registry("test", "https://example.com")
        
        # Create cache file with test data
        cache_path = remote_registry._get_cache_path("test")
        test_data = [{"name": "test-skill", "domain": "test", "version": "1.0.0", "surfaces": ["python"]}]
        with open(cache_path, "w") as f:
            json.dump(test_data, f)
        
        # Load cached data
        cached = remote_registry._load_cached_registry("test")
        assert cached == test_data


def test_convert_remote_skill():
    """Test converting remote skill data to SkillMetadata."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote_registry = RemoteSkillRegistry(local_registry)
        
        # Test valid skill data
        skill_data = {
            "name": "test-skill",
            "domain": "test",
            "version": "1.0.0",
            "surfaces": ["python"],
            "description": "A test skill",
            "purpose": "Testing"
        }
        
        skill_metadata = remote_registry._convert_remote_skill(skill_data)
        assert skill_metadata is not None
        assert skill_metadata.name == "test-skill"
        assert skill_metadata.domain == "test"
        assert skill_metadata.version == "1.0.0"
        assert skill_metadata.surfaces == ["python"]
        assert skill_metadata.description == "A test skill"
        assert skill_metadata.purpose == "Testing"


def test_convert_remote_skill_missing_fields():
    """Test converting remote skill data with missing fields."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote_registry = RemoteSkillRegistry(local_registry)
        
        # Test missing required field
        skill_data = {
            "name": "test-skill",
            # Missing domain
            "version": "1.0.0",
            "surfaces": ["python"]
        }
        
        skill_metadata = remote_registry._convert_remote_skill(skill_data)
        assert skill_metadata is None


if __name__ == "__main__":
    test_remote_registry_creation()
    test_add_remove_registry()
    test_sync_registry_not_due()
    test_sync_registry_force()
    test_load_cached_registry()
    test_convert_remote_skill()
    test_convert_remote_skill_missing_fields()
    print("All tests passed!")