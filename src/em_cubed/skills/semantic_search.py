"""Semantic skill search using local vector embeddings."""
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import structlog
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from .registry import SkillRegistry
from .metadata import SkillMetadata

logger = structlog.get_logger()


class SemanticSkillSearch:
    """Semantic skill search using local vector embeddings."""
    
    def __init__(self, registry: SkillRegistry, cache_dir: Optional[Path] = None,
                 model_name: str = "all-MiniLM-L6-v2"):
        """Initialize semantic search.
        
        Args:
            registry: The skill registry to search
            cache_dir: Directory to cache embeddings (defaults to ~/.em-cubed/semantic-cache)
            model_name: Name of the sentence transformer model to use
        """
        self.registry = registry
        self.logger = logger.bind(component="semantic_search")
        self.model_name = model_name
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path.home() / ".em-cubed" / "semantic-cache"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model if available
        self.model = None
        self._initialize_model()
        
        # Cache for skill embeddings and text representations
        self._skill_embeddings: Dict[str, np.ndarray] = {}
        self._skill_texts: Dict[str, str] = {}
        self._last_indexed: Dict[str, float] = {}  # skill_id -> timestamp
        
        # Index existing skills
        self._reindex_all_skills()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.warning("SentenceTransformers not available, semantic search disabled")
            return
        
        try:
            self.logger.info("Loading sentence transformer model", model=self.model_name)
            self.model = SentenceTransformer(self.model_name)
            self.logger.info("Sentence transformer model loaded successfully")
        except Exception as e:
            self.logger.error("Failed to load sentence transformer model", 
                            model=self.model_name, error=str(e))
            self.model = None
    
    def _get_skill_text(self, skill: SkillMetadata) -> str:
        """Convert skill to text representation for embedding.
        
        Args:
            skill: The skill to convert
            
        Returns:
            Text representation of the skill
        """
        # Combine multiple fields for rich semantic representation
        text_parts = [
            skill.name or "",
            skill.domain or "",
            skill.description or "",
            skill.purpose or "",
            " ".join(skill.surfaces or []),
            " ".join([dep.skill_id for dep in skill.dependencies or []]),
            " ".join(skill.tags or []),
        ]
        
        # Add schema information
        if skill.input_schema:
            text_parts.append(f"input: {skill.input_schema.type}")
            if skill.input_schema.properties:
                text_parts.append(" ".join(skill.input_schema.properties.keys()))
        
        if skill.output_schema:
            text_parts.append(f"output: {skill.output_schema.type}")
            if skill.output_schema.properties:
                text_parts.append(" ".join(skill.output_schema.properties.keys()))
        
        # Add capabilities
        if skill.capabilities:
            if skill.capabilities.surfaces:
                text_parts.append(" ".join(skill.capabilities.surfaces))
            if skill.capabilities.permissions:
                text_parts.append(" ".join(skill.capabilities.permissions))
        
        return " ".join(filter(None, text_parts)).strip()
    
    def _get_cache_path(self) -> Path:
        """Get cache file path for embeddings."""
        # Create a hash based on model name and registry state
        registry_hash = hashlib.md5(
            f"{self.model_name}:{len(self.registry._skills)}".encode()
        ).hexdigest()[:8]
        return self.cache_dir / f"embeddings_{registry_hash}.pkl"
    
    def _get_skill_timestamp(self, skill: SkillMetadata) -> float:
        """Get timestamp for skill to check if reindexing is needed.
        
        Args:
            skill: The skill to check
            
        Returns:
            Timestamp of the skill file or 0 if not available
        """
        if skill.path:
            skill_path = Path(skill.path)
            if skill_path.exists():
                return skill_path.stat().st_mtime
        return 0
    
    def _load_cached_embeddings(self) -> bool:
        """Load cached embeddings if available and fresh.
        
        Returns:
            True if embeddings were loaded from cache, False otherwise
        """
        cache_path = self._get_cache_path()
        if not cache_path.exists():
            return False
        
        try:
            # Check if any skill has been modified since cache was created
            for skill_id, skill in self.registry._skills.items():
                if skill_id not in self._last_indexed:
                    return False  # Missing from cache, need to reindex
                skill_time = self._get_skill_timestamp(skill)
                if skill_time > self._last_indexed.get(skill_id, 0):
                    return False  # Skill modified, cache stale
            
            # Load cached data
            with open(cache_path, "rb") as f:
                cached_data = pickle.load(f)
                
            self._skill_embeddings = cached_data.get("embeddings", {})
            self._skill_texts = cached_data.get("texts", {})
            self._last_indexed = cached_data.get("last_indexed", {})
            
            self.logger.info("Loaded skill embeddings from cache", 
                           count=len(self._skill_embeddings))
            return True
        except Exception as e:
            self.logger.warning("Failed to load cached embeddings", error=str(e))
            return False
    
    def _save_cached_embeddings(self):
        """Save embeddings to cache."""
        if not self._skill_embeddings:
            return
        
        cache_path = self._get_cache_path()
        try:
            cached_data = {
                "embeddings": self._skill_embeddings,
                "texts": self._skill_texts,
                "last_indexed": self._last_indexed,
            }
            with open(cache_path, "wb") as f:
                pickle.dump(cached_data, f)
            
            self.logger.info("Saved skill embeddings to cache", 
                           count=len(self._skill_embeddings))
        except Exception as e:
            self.logger.warning("Failed to save cached embeddings", error=str(e))
    
    def _reindex_all_skills(self):
        """Reindex all skills in the registry."""
        if not self.model:
            self.logger.warning("Semantic search model not available, skipping indexing")
            return
        
        # Try to load from cache first
        if self._load_cached_embeddings():
            # Check if we need to update any skills
            needs_update = False
            for skill_id, skill in self.registry._skills.items():
                if skill_id not in self._last_indexed:
                    needs_update = True
                    break
                # Check if skill file has been modified
                skill_time = self._get_skill_timestamp(skill)
                if skill_time > self._last_indexed.get(skill_id, 0):
                    needs_update = True
                    break
            
            if not needs_update:
                self.logger.info("Using cached embeddings, no updates needed")
                return
        
        self.logger.info("Reindexing all skills for semantic search")
        
        # Generate embeddings for all skills
        texts = []
        skill_ids = []
        
        for skill_id, skill in self.registry._skills.items():
            text = self._get_skill_text(skill)
            if text.strip():  # Only index skills with meaningful text
                texts.append(text)
                skill_ids.append(skill_id)
                self._skill_texts[skill_id] = text
        
        if not texts:
            self.logger.warning("No skills with text content found for indexing")
            return
        
        # Generate embeddings
        try:
            embeddings = self.model.encode(texts)
            
            # Store embeddings
            for i, skill_id in enumerate(skill_ids):
                self._skill_embeddings[skill_id] = embeddings[i]
                self._last_indexed[skill_id] = self._get_skill_timestamp(
                    self.registry._skills[skill_id])
            
            # Save to cache
            self._save_cached_embeddings()
            
            self.logger.info("Completed skill reindexing", 
                           count=len(self._skill_embeddings))
        except Exception as e:
            self.logger.error("Failed to generate skill embeddings", error=str(e))
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[SkillMetadata, float]]:
        """Search for skills semantically similar to the query.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of (skill, similarity_score) tuples, sorted by similarity descending
        """
        if not self.model:
            self.logger.warning("Semantic search model not available")
            return []
        
        if not query.strip():
            return []
        
        # Ensure we have up-to-date embeddings
        self._reindex_all_skills()
        
        if not self._skill_embeddings:
            return []
        
        try:
            # Encode the query
            query_embedding = self.model.encode([query])[0]
            
            # Calculate similarities
            similarities = []
            for skill_id, skill_embedding in self._skill_embeddings.items():
                # Cosine similarity
                similarity = np.dot(query_embedding, skill_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(skill_embedding)
                )
                skill = self.registry.get_skill(skill_id)
                if skill:
                    similarities.append((skill, float(similarity)))
            
            # Sort by similarity descending
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top results
            return similarities[:limit]
        except Exception as e:
            self.logger.error("Failed to perform semantic search", error=str(e))
            return []

    def get_similar_skills(self, skill_id: str, limit: int = 5) -> List[Tuple[SkillMetadata, float]]:
        """Find skills similar to a given skill.
        
        Args:
            skill_id: The skill ID to find similar skills for
            limit: Maximum number of results to return
            
        Returns:
            List of (skill, similarity_score) tuples, sorted by similarity descending
        """
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return []
        
        # Use the skill's text representation as the query
        skill_text = self._get_skill_text(skill)
        if not skill_text.strip():
            return []
        
        return self.search(skill_text, limit=limit + 1)[1:]  # Exclude the skill itself


# Global semantic search manager (singleton pattern)
_semantic_search_manager: Optional[SemanticSkillSearch] = None


def get_semantic_search_manager() -> Optional[SemanticSkillSearch]:
    """Get the global semantic search manager instance."""
    global _semantic_search_manager
    return _semantic_search_manager


def initialize_semantic_search(registry: SkillRegistry, 
                              cache_dir: Optional[Path] = None,
                              model_name: str = "all-MiniLM-L6-v2") -> SemanticSkillSearch:
    """Initialize the global semantic search manager.
    
    Args:
        registry: The skill registry to search
        cache_dir: Directory to cache embeddings
        model_name: Name of the sentence transformer model to use
        
    Returns:
        The initialized SemanticSkillSearch instance
    """
    global _semantic_search_manager
    _semantic_search_manager = SemanticSkillSearch(registry, cache_dir, model_name)
    logger.info("Semantic search manager initialized")
    return _semantic_search_manager