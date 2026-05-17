"""Plugin system for extensible surface architecture."""
import importlib.util
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, cast
import structlog

from .plugin_discovery import PluginDiscovery
from .plugin_registry import PluginRegistry

logger = structlog.get_logger()


class PluginManager:
    """Manage surface plugins with separated discovery, registry, and lifecycle concerns.
    
    This class now follows the Single Responsibility Principle by delegating:
    - Discovery: PluginDiscovery class
    - Registry: PluginRegistry class  
    - Lifecycle: Handled by PluginRegistry with PluginManager coordination
    """
    
    def __init__(self):
        self.discovery = PluginDiscovery()
        self.registry = PluginRegistry()
        self._lazy_classes: Dict[str, type] = {}
        
        self._load_plugins()
        
        logger.info(
            "PluginManager initialized", 
            loaded=list(self.registry.get_plugin_names()),
            lazy=list(self._lazy_classes.keys())
        )
    
    def __del__(self):
        """Clean up plugins on deletion."""
        self.shutdown_all()
    
    def _load_plugins(self):
        """Load plugins from all discovery mechanisms."""
        # Import SurfacePlugin locally to avoid circular imports
        from .plugin import SurfacePlugin
        
        # Discover built-in surfaces
        eager_builtin, lazy_builtin, entry_point, directory = \
            self.discovery.discover_all_plugins()
        
        # Register eager built-in surfaces
        for name, surface_class in eager_builtin.items():
            if surface_class is not None:
                try:
                    # Verify it's a SurfacePlugin subclass
                    if issubclass(surface_class, SurfacePlugin):
                        instance = surface_class()
                        self.registry.register(name, instance)
                    else:
                        logger.warning("Discovered class is not a SurfacePlugin", 
                                     surface=name, class_name=surface_class.__name__)
                except Exception as e:
                    logger.warning("Failed to instantiate surface", surface=name, error=str(e))
        
        # Store lazy built-in surfaces for later loading
        for name, surface_class in lazy_builtin.items():
            if surface_class is not None:
                # Verify it's a SurfacePlugin subclass
                if issubclass(surface_class, SurfacePlugin):
                    self._lazy_classes[name] = surface_class
                else:
                    logger.warning("Discovered lazy class is not a SurfacePlugin", 
                                 surface=name, class_name=surface_class.__name__)
        
        # Register entry point plugins
        for name, surface_class in entry_point.items():
            try:
                # Verify it's a SurfacePlugin subclass
                if issubclass(surface_class, SurfacePlugin):
                    instance = surface_class()
                    self.registry.register(name, instance)
                else:
                    logger.warning("Entry point class is not a SurfacePlugin", 
                                 entry_point=name, class_name=surface_class.__name__)
            except Exception as e:
                logger.warning("Failed to load entry point plugin", 
                             entry_point=name, error=str(e))
        
        # Register directory plugins
        for name, surface_class in directory.items():
            try:
                # Verify it's a SurfacePlugin subclass
                if issubclass(surface_class, SurfacePlugin):
                    instance = surface_class()
                    self.registry.register(name, instance)
                else:
                    logger.warning("Directory class is not a SurfacePlugin", 
                                 plugin_name=name, class_name=surface_class.__name__)
            except Exception as e:
                logger.warning("Failed to load directory plugin", 
                             plugin_name=name, error=str(e))
    
    def get(self, name: str):
        """Get plugin by name, lazily loading heavy surfaces on first use."""
        # Import SurfacePlugin locally to avoid circular imports
        from .plugin import SurfacePlugin
        
        # Try to get from registry first
        plugin = self.registry.get(name)
        if plugin is not None:
            return plugin
        
        # If not found, check if it's a lazy surface
        if name in self._lazy_classes:
            try:
                surface_class = self._lazy_classes.pop(name)
                # Verify it's a SurfacePlugin subclass
                if issubclass(surface_class, SurfacePlugin):
                    instance = surface_class()
                    self.registry.register(name, instance)
                    logger.info("Lazily loaded surface", surface=name)
                    return instance
                else:
                    logger.warning("Lazily loaded class is not a SurfacePlugin", 
                                 surface=name, class_name=surface_class.__name__)
                    return None
            except Exception as e:
                logger.warning("Failed to lazily load surface", surface=name, error=str(e))
                return None
        
        return None
    
    def register(self, name: str, plugin):
        """Register a plugin instance."""
        self.registry.register(name, plugin)
    
    def list_plugins(self) -> Dict[str, bool]:
        """List all plugins and their availability."""
        return self.registry.list_plugins()
    
    def get_available_surfaces(self) -> List[str]:
        """Get list of available surface names."""
        available = [name for name, plugin in self.registry.get_plugins().items() if getattr(plugin, 'available', True)]
        available.extend(list(self._lazy_classes.keys()))
        return available
    
    def get_surface_info(self) -> List[Dict[str, Any]]:
        """Get detailed information about all surfaces."""
        info = []
        for name, plugin in self.registry.get_plugins().items():
            info.append({
                "name": name,
                "available": getattr(plugin, 'available', True),
                "description": getattr(plugin, "description", f"{name.title()} surface"),
            })
        for name in self._lazy_classes:
            info.append({
                "name": name,
                "available": True,
                "description": f"{name.title()} surface (lazy-loaded)",
            })
        return info
    
    def initialize_all(self) -> Dict[str, bool]:
        """Initialize all registered plugins."""
        return self.registry.initialize_all()
    
    def shutdown_all(self) -> Dict[str, bool]:
        """Shutdown all registered plugins."""
        return self.registry.shutdown_all()
    
    def get_plugin_count(self) -> int:
        """Get the number of registered plugins."""
        return self.registry.get_plugin_count()

    def get_plugin_names(self) -> set:
        """Get the set of registered plugin names."""
        return self.registry.get_plugin_names()