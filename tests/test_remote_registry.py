"""Tests for remote registry discovery functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from src.em_cubed.skills.remote_registry import RemoteSkillRegistry
from src.em_cubed.skills.registry import SkillRegistry


def test_remote_registry_discovery_with_mock():
    """Test remote registry discovery with mocked HTTP response."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir)
        registry_file = Path(tmpdir) / "registry.json"
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote = RemoteSkillRegistry(local_registry)
        
        # Mock registry data
        mock_skills = [
            {
                "name": "Central Force Optimizer",
                "domain": "optimization",
                "version": "1.0.0",
                "surfaces": ["python"],
                "purpose": "Gravitational optimization",
                "description": "Uses gravitational forces to find optima",
            },
        ]
        
        remote.add_registry("test-registry", "https://test.example.com")
        
        with patch.object(remote, '_fetch_remote_registry', return_value=mock_skills):
            skills = remote.discover_skills("central", limit=10)
            
            assert len(skills) == 1
            assert skills[0].name == "Central Force Optimizer"
            assert skills[0].domain == "optimization"


def test_remote_registry_multiple_registries():
    """Test discovery across multiple registries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir)
        registry_file = Path(tmpdir) / "registry.json"
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote = RemoteSkillRegistry(local_registry)
        
        # Mock skills from different registries
        registry_a_skills = [{"name": "Skill A", "domain": "test", "surfaces": ["python"]}]
        registry_b_skills = [{"name": "Skill B", "domain": "test", "surfaces": ["prolog"]}]
        
        remote.add_registry("registry-a", "https://a.example.com")
        remote.add_registry("registry-b", "https://b.example.com")
        
        fetch_mock = patch.object(remote, '_fetch_remote_registry')
        with fetch_mock as mock_fetch:
            mock_fetch.side_effect = [registry_a_skills, registry_b_skills]
            skills = remote.discover_skills("skill", limit=10)
            
            assert len(skills) == 2


def test_remote_registry_caching():
    """Test that registry data is cached properly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir)
        registry_file = Path(tmpdir) / "registry.json"
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote = RemoteSkillRegistry(local_registry)
        
        mock_skills = [{"name": "Cached Skill", "domain": "test", "surfaces": ["python"]}]
        
        remote.add_registry("cache-test", "https://cache.example.com")
        
        # First call - fetch and save
        with patch.object(remote, '_fetch_remote_registry', return_value=mock_skills):
            skills = remote.discover_skills("cached", limit=10)
            assert len(skills) == 1
        
        # Second call - should use cache, not call fetch
        with patch.object(remote, '_fetch_remote_registry', return_value=mock_skills) as fetch_mock2:
            skills2 = remote.discover_skills("cached", limit=10)
            # Cache should be hit, so fetch shouldn't be called
            assert fetch_mock2.call_count == 0
            assert len(skills2) == 1


def test_remote_registry_empty_result():
    """Test discovery returns empty when no skills match."""
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir)
        registry_file = Path(tmpdir) / "registry.json"
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        remote = RemoteSkillRegistry(local_registry)
        
        mock_skills = [{"name": "Unrelated Skill", "domain": "test", "surfaces": ["python"]}]
        
        remote.add_registry("empty-test", "https://empty.example.com")
        
        with patch.object(remote, '_fetch_remote_registry', return_value=mock_skills):
            skills = remote.discover_skills("nonexistent", limit=10)
            assert skills == []


if __name__ == "__main__":
    pytest.main(["-v", __file__])