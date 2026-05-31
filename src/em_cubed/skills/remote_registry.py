"""Remote skill registry discovery and federation."""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, cast
import structlog
import requests

from .registry import SkillRegistry
from .metadata import SkillMetadata

logger = structlog.get_logger()


class RemoteSkillRegistry:
    """Handles discovery and synchronization with remote skill registries."""
    
    def __init__(self, local_registry: SkillRegistry, cache_dir: Optional[Path] = None):
        """Initialize remote registry handler.
        
        Args:
            local_registry: The local SkillRegistry to sync with
            cache_dir: Directory to cache remote skill data (defaults to ~/.em-cubed/remote-cache)
        """
        self.local_registry = local_registry
        self.logger = logger.bind(component="remote_registry")
        
        # Setup cache directory
        if cache_dir is None:
            cache_dir = Path.home() / ".em-cubed" / "remote-cache"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Registry configuration
        self._registries: Dict[str, Dict[str, Any]] = {}
        self._last_sync: Dict[str, float] = {}
        self._sync_interval = 300  # 5 minutes default
        
        # Load default registries from environment or config
        self._load_default_registries()
    
    def _load_default_registries(self):
        """Load default registry configurations."""
        # Check for registry configuration in environment
        registry_config = os.getenv("EM_CUBED_REGISTRIES")
        if registry_config:
            try:
                configs = json.loads(registry_config)
                for name, config in configs.items():
                    self.add_registry(name, config["url"], config.get("token"), config.get("interval", 300))
            except Exception as e:
                self.logger.warning("Failed to parse EM_CUBED_REGISTRIES", error=str(e))
        
        # Add some default public registries (these would be examples)
        # In practice, these would be configured by the user/administrator
        pass
    
    def add_registry(self, name: str, url: str, token: Optional[str] = None, 
                    sync_interval: int = 300, verify_ssl: bool = True):
        """Add a remote registry to synchronize with.
        
        Args:
            name: Unique name for this registry
            url: Base URL of the remote registry API
            token: Optional authentication token
            sync_interval: How often to sync in seconds (default 5 minutes)
            verify_ssl: Whether to verify SSL certificates
        """
        self._registries[name] = {
            "url": url.rstrip("/"),
            "token": token,
            "sync_interval": sync_interval,
            "verify_ssl": verify_ssl,
            "headers": {
                "Authorization": f"Bearer {token}" if token else None,
                "User-Agent": "Em-Cubed/0.5.0"
            }
        }
        # Remove None values from headers
        self._registries[name]["headers"] = {
            k: v for k, v in self._registries[name]["headers"].items() if v is not None
        }
        
        self.logger.info("Added remote registry", name=name, url=url)
    
    def remove_registry(self, name: str) -> bool:
        """Remove a remote registry.
        
        Args:
            name: Name of the registry to remove
            
        Returns:
            True if registry was removed, False if not found
        """
        if name in self._registries:
            del self._registries[name]
            # Clear cached data for this registry
            cache_file = self.cache_dir / f"{name}.json"
            if cache_file.exists():
                cache_file.unlink()
            self._last_sync.pop(name, None)
            self.logger.info("Removed remote registry", name=name)
            return True
        return False
    
    def _get_cache_path(self, registry_name: str) -> Path:
        """Get cache file path for a registry."""
        # Hash the registry name to create a safe filename
        name_hash = hashlib.md5(registry_name.encode()).hexdigest()[:8]  # nosec B324
        return self.cache_dir / f"registry_{name_hash}.json"
    
    def _load_cached_registry(self, registry_name: str) -> Optional[List[Dict[str, Any]]]:
        """Load cached registry data if available and not expired."""
        cache_path = self._get_cache_path(registry_name)
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is still fresh
            registry_config = self._registries.get(registry_name, {})
            max_age = registry_config.get("sync_interval", 300) * 2  # Allow 2x interval
            
            cache_age = time.time() - cache_path.stat().st_mtime
            if cache_age > max_age:
                self.logger.debug("Registry cache expired", registry=registry_name, age=cache_age)
                return None
            
            with open(cache_path, encoding="utf-8") as f:
                data = json.load(f)
                self.logger.debug("Loaded cached registry data", 
                                registry=registry_name, count=len(data))
                return cast(List[Dict[str, Any]], data)
        except Exception as e:
            self.logger.warning("Failed to load cached registry", 
                              registry=registry_name, error=str(e))
            return None
    
    def _save_cached_registry(self, registry_name: str, data: List[Dict[str, Any]]):
        """Save registry data to cache."""
        cache_path = self._get_cache_path(registry_name)
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.logger.debug("Saved registry data to cache", 
                            registry=registry_name, count=len(data))
        except Exception as e:
            self.logger.warning("Failed to save registry cache", 
                              registry=registry_name, error=str(e))
    
    def _fetch_remote_registry(self, registry_name: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch skill data from a remote registry.
        
        Args:
            registry_name: Name of the registry to fetch from
            
        Returns:
            List of skill data dictionaries, or None if failed
        """
        if registry_name not in self._registries:
            self.logger.error("Unknown registry", name=registry_name)
            return None
        
        config = self._registries[registry_name]
        url = f"{config['url']}/api/skills"  # Assuming standard API endpoint
        
        try:
            self.logger.info("Fetching remote registry", name=registry_name, url=url)
            response = requests.get(
                url,
                headers=config["headers"],
                verify=config["verify_ssl"],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Expecting format: {"skills": [...]} or just [...]
                if isinstance(data, dict) and "skills" in data:
                    skills_data = data["skills"]
                elif isinstance(data, list):
                    skills_data = data
                else:
                    self.logger.error("Unexpected registry response format", 
                                    registry=registry_name, format=type(data).__name__)
                    return None
                
                self.logger.info("Fetched remote registry data", 
                                registry=registry_name, count=len(skills_data))
                return cast(List[Dict[str, Any]], skills_data)
            else:
                self.logger.error("Failed to fetch remote registry", 
                                registry=registry_name, 
                                status=response.status_code,
                                response=response.text[:200])
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error("Network error fetching remote registry", 
                            registry=registry_name, error=str(e))
            return None
        except Exception as e:
            self.logger.error("Unexpected error fetching remote registry", 
                            registry=registry_name, error=str(e))
            return None
    
    def _convert_remote_skill(self, skill_data: Dict[str, Any]) -> Optional[SkillMetadata]:
        """Convert remote skill data to SkillMetadata.
        
        Args:
            skill_data: Skill data from remote registry
            
        Returns:
            SkillMetadata object or None if conversion failed
        """
        try:
            # Handle different possible formats from remote registries
            # Standard format expected: similar to local skill registry format
            if "skill_id" not in skill_data:
                # Try to construct skill_id from domain/name
                domain = skill_data.get("domain", "remote")
                name = skill_data.get("name", "unknown")
                skill_data["skill_id"] = f"{domain}/{name}"
            
            # Ensure required fields are present
            required_fields = ["name", "domain", "version", "surfaces"]
            for field in required_fields:
                if field not in skill_data:
                    self.logger.warning("Missing required field in remote skill", 
                                      field=field, skill_id=skill_data.get("skill_id"))
                    return None
            
            # Deserialize using existing method (similar to local registry)
            # We'll reuse the deserialization logic from SkillRegistry
            # For now, create a basic SkillMetadata - in practice this would 
            # need more robust handling of different formats
            from .metadata import SkillMetadata
            return SkillMetadata.from_frontmatter(skill_data)
            
        except Exception as e:
            self.logger.warning("Failed to convert remote skill to metadata", 
                              skill_id=skill_data.get("skill_id"), error=str(e))
            return None
    
    def sync_registry(self, registry_name: str, force: bool = False) -> bool:
        """Synchronize with a remote registry.
        
        Args:
            registry_name: Name of the registry to sync with
            force: Whether to force sync even if not due
            
        Returns:
            True if sync was performed, False if skipped
        """
        if registry_name not in self._registries:
            self.logger.error("Unknown registry for sync", name=registry_name)
            return False
        
        # Check if sync is due
        config = self._registries[registry_name]
        last_sync = self._last_sync.get(registry_name, 0)
        sync_interval = config["sync_interval"]
        
        if not force and (time.time() - last_sync) < sync_interval:
            self.logger.debug("Registry sync not due yet", 
                            registry=registry_name, 
                            next_sync_in=sync_interval - (time.time() - last_sync))
            return False
        
        # Try to load cached data first
        skills_data = self._load_cached_registry(registry_name)
        
        # If no cache or forced, try to fetch fresh data
        if skills_data is None or force:
            skills_data = self._fetch_remote_registry(registry_name)
            if skills_data is None:
                # If fetch failed but we have cache, use cache
                skills_data = self._load_cached_registry(registry_name)
                if skills_data is None:
                    self.logger.error("Failed to fetch or load registry data", 
                                    registry=registry_name)
                    return False
            else:
                # Save fresh data to cache
                self._save_cached_registry(registry_name, skills_data)
        
        # Convert and import skills
        imported_count = 0
        updated_count = 0
        
        for skill_data in skills_data:
            try:
                skill_metadata = self._convert_remote_skill(skill_data)
                if skill_metadata is None:
                    continue
                
                skill_id = skill_metadata.skill_id
                if skill_id is None:
                    continue
                
                # Check if skill already exists locally
                existing_skill = self.local_registry.get_skill(skill_id)
                
                if existing_skill is None:
                    # New skill - add it
                    self.local_registry.add_skill(skill_metadata)
                    imported_count += 1
                    self.logger.info("Imported new skill from remote registry", 
                                   skill_id=skill_id, registry=registry_name)
                else:
                    # Existing skill - check if we should update
                    # For now, we'll update if the remote version is newer
                    # In a more sophisticated implementation, we might check
                    # timestamps, version numbers, or update policies
                    remote_version = skill_metadata.version
                    local_version = existing_skill.version
                    
                    # Simple version comparison (would want proper semver in practice)
                    if remote_version != local_version:
                        self.local_registry.add_skill(skill_metadata)  # This will replace
                        updated_count += 1
                        self.logger.info("Updated skill from remote registry", 
                                       skill_id=skill_id, 
                                       old_version=local_version,
                                       new_version=remote_version,
                                       registry=registry_name)
                
            except Exception as e:
                self.logger.warning("Failed to process skill from remote registry", 
                                  skill_id=skill_data.get("skill_id"), 
                                  error=str(e))
        
        # Update sync timestamp
        self._last_sync[registry_name] = time.time()
        
        self.logger.info("Completed registry sync", 
                        registry=registry_name,
                        imported=imported_count,
                        updated=updated_count,
                        total=len(skills_data))
        
        return True
    
    def sync_all_registries(self, force: bool = False) -> Dict[str, bool]:
        """Synchronize with all configured registries.
        
        Args:
            force: Whether to force sync even if not due
            
        Returns:
            Dictionary mapping registry names to sync success boolean
        """
        results = {}
        for registry_name in self._registries.keys():
            results[registry_name] = self.sync_registry(registry_name, force=force)
        return results
    
    def discover_skills(self, query: str, limit: int = 10) -> List[SkillMetadata]:
        """Discover skills from remote registries matching a query.
        
        Args:
            query: Search query (would be sent to remote registries)
            limit: Maximum number of results to return
            
        Returns:
            List of matching SkillMetadata objects
        """
        all_skills = []
        
        for name in self._registries:
            # Try cache first
            cache = self._load_cached_registry(name)
            if cache is None:
                cache = self._fetch_remote_registry(name)
                if cache is not None:
                    self._save_cached_registry(name, cache)
            
            if cache:
                # Filter by query (simple substring match on name/description)
                for skill_data in cache:
                    skill_name = skill_data.get("name", "").lower()
                    skill_desc = skill_data.get("description", "").lower()
                    if query.lower() in skill_name or query.lower() in skill_desc:
                        try:
                            skill = SkillMetadata(
                                name=skill_data.get("name", ""),
                                domain=skill_data.get("domain", "remote"),
                                version=skill_data.get("version", "0.0.0"),
                                surfaces=skill_data.get("surfaces", ["python"]),
                                purpose=skill_data.get("purpose", ""),
                                description=skill_data.get("description", ""),
                                dependencies=[],
                                input_schema={},
                                output_schema={},
                                capabilities={},
                                compatibility={},
                                quality_thresholds={},
                                metrics={},
                                skill_id=skill_data.get("skill_id", f"remote/{skill_data.get('name', '')}"),
                                path="",
                                schema_version=skill_data.get("schema_version", 1),
                                tags=skill_data.get("tags", []),
                            )
                            all_skills.append(skill)
                        except Exception as e:
                            self.logger.warning("Failed to parse remote skill", 
                                              registry=name, error=str(e))
        
        self._last_sync.update({name: time.time() for name in self._registries})
        
        return all_skills[:limit]
    
    def get_registry_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about configured registries.
        
        Returns:
            Dictionary with registry configuration and status
        """
        info = {}
        for name, config in self._registries.items():
            info[name] = {
                "url": config["url"],
                "sync_interval": config["sync_interval"],
                "last_sync": self._last_sync.get(name, 0),
                "next_sync": self._last_sync.get(name, 0) + config["sync_interval"],
                "has_cache": self._get_cache_path(name).exists()
            }
        return info


# Global remote registry manager (singleton pattern)
_remote_registry_manager: Optional[RemoteSkillRegistry] = None


def get_remote_registry_manager() -> Optional[RemoteSkillRegistry]:
    """Get the global remote registry manager instance."""
    global _remote_registry_manager
    return _remote_registry_manager


def initialize_remote_registry(local_registry: SkillRegistry, 
                              cache_dir: Optional[Path] = None) -> RemoteSkillRegistry:
    """Initialize the global remote registry manager.
    
    Args:
        local_registry: The local SkillRegistry to sync with
        cache_dir: Directory to cache remote skill data
        
    Returns:
        The initialized RemoteSkillRegistry instance
    """
    global _remote_registry_manager
    _remote_registry_manager = RemoteSkillRegistry(local_registry, cache_dir)
    logger.info("Remote registry manager initialized")
    return _remote_registry_manager