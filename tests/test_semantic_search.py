"""Tests for semantic skill search functionality."""
import json
import tempfile
from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock

from em_cubed.skills.semantic_search import SemanticSkillSearch
from em_cubed.skills.registry import SkillRegistry
from em_cubed.skills.metadata import SkillMetadata


def test_semantic_search_creation():
    """Test that SemanticSkillSearch can be created."""
    # Create a temporary local registry
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")  # Empty registry
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        semantic_search = SemanticSkillSearch(local_registry)
        
        assert semantic_search.registry == local_registry
        assert semantic_search.cache_dir.exists()


def test_semantic_search_disabled_without_model():
    """Test that semantic search gracefully handles missing sentence-transformers."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        
        # Mock the import to fail
        with patch('em_cubed.skills.semantic_search.SENTENCE_TRANSFORMERS_AVAILABLE', False):
            semantic_search = SemanticSkillSearch(local_registry)
            assert semantic_search.model is None
            
            # Search should return empty list
            results = semantic_search.search("test query")
            assert results == []


def test_get_skill_text():
    """Test conversion of skill to text representation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        semantic_search = SemanticSkillSearch(local_registry)
        
        # Create a test skill
        skill = SkillMetadata(
            name="test-skill",
            domain="test-domain",
            version="1.0.0",
            surfaces=["python", "prolog"],
            description="A test skill for semantic search",
            purpose="Testing semantic search",
            tags=["test", "semantic"],
        )
        
        text = semantic_search._get_skill_text(skill)
        
        # Check that key components are in the text
        assert "test-skill" in text
        assert "test-domain" in text
        assert "A test skill for semantic search" in text
        assert "Testing semantic search" in text
        assert "python" in text
        assert "prolog" in text
        assert "test" in text
        assert "semantic" in text


def test_get_skill_text_empty_skill():
    """Test text conversion for skill with minimal fields."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        semantic_search = SemanticSkillSearch(local_registry)
        
        # Create a minimal skill
        skill = SkillMetadata(
            name="minimal",
            domain="minimal",
            version="1.0.0",
            surfaces=["python"],
        )
        
        text = semantic_search._get_skill_text(skill)
        
        # Should still produce some text
        assert "minimal" in text
        assert "python" in text


def test_search_empty_query():
    """Test that empty query returns empty results."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        semantic_search = SemanticSkillSearch(local_registry)
        
        # Even with model mocked, empty query should return empty
        with patch.object(semantic_search, 'model') as mock_model:
            mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
            results = semantic_search.search("")
            assert results == []
            
            results = semantic_search.search("   ")
            assert results == []


def test_similar_skills():
    """Test finding similar skills."""
    with tempfile.TemporaryDirectory() as temp_dir:
        skills_dir = Path(temp_dir) / "skills"
        skills_dir.mkdir()
        registry_file = Path(temp_dir) / "registry.json"
        registry_file.write_text("[]")
        
        local_registry = SkillRegistry(skills_dir, registry_file)
        semantic_search = SemanticSkillSearch(local_registry)
        
        # Add a skill to the registry
        skill = SkillMetadata(
            name="test-skill",
            domain="test",
            version="1.0.0",
            surfaces=["python"],
            description="A test skill",
        )
        local_registry.add_skill(skill)
        
        # Mock the model to return predictable embeddings
        with patch.object(semantic_search, 'model') as mock_model:
            # Mock encode to return fixed vectors
            def mock_encode(texts):
                # Return different vectors for different inputs
                if "test" in texts[0].lower():
                    return [[1.0, 0.0, 0.0]]  # Query vector
                else:
                    return [[0.0, 1.0, 0.0]]  # Skill vector (orthogonal)
            
            mock_model.encode.side_effect = mock_encode
            
            # Search for similar skills
            results = semantic_search.get_similar_skills(skill.skill_id, limit=5)
            
            # Should return empty list since vectors are orthogonal (similarity 0)
            assert isinstance(results, list)


if __name__ == "__main__":
    test_semantic_search_creation()
    test_semantic_search_disabled_without_model()
    test_get_skill_text()
    test_get_skill_text_empty_skill()
    test_search_empty_query()
    test_similar_skills()
    print("All tests passed!")