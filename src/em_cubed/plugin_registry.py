"""Plugin registry and lifecycle management for the PluginManager."""
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Manages plugin registration, lookup, and lifecycle."""
    
    def __init__(self):
        self._plugins: Dict[str, object] = {}  # Store as object to avoid circular import issues
        self._initialized: Set[str] = set()
    
    def register(self, name: str, plugin) -> None:
        """
        Register a plugin instance.
        
        Args:
            name: Unique name for the plugin
            plugin: Plugin instance to register
        """
        if name in self._plugins:
            logger.warning("Plugin already registered, replacing: %s", name)
        
        self._plugins[name] = plugin
        logger.debug("Plugin registered: %s", name)
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            name: Name of plugin to unregister
            
        Returns:
            True if plugin was found and removed, False otherwise
        """
        if name in self._plugins:
            plugin = self._plugins.pop(name)
            try:
                if hasattr(plugin, 'shutdown'):
                    plugin.shutdown()
            except Exception as e:
                logger.warning("Error shutting down plugin during unregister {}: {}".format(name, str(e)))
            self._initialized.discard(name)
            logger.debug("Plugin unregistered: %s", name)
            return True
        return False
    
    def get(self, name: str):
        """
        Get a plugin by name.
        
        Args:
            name: Name of plugin to retrieve
            
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(name)
    
    def initialize_plugin(self, name: str) -> bool:
        """
        Initialize a specific plugin.
        
        Args:
            name: Name of plugin to initialize
            
        Returns:
            True if plugin was initialized, False if not found
        """
        plugin = self._plugins.get(name)
        if plugin and name not in self._initialized:
            try:
                if hasattr(plugin, 'initialize'):
                    plugin.initialize()
                self._initialized.add(name)
                logger.debug("Plugin initialized: %s", name)
                return True
            except Exception as e:
                logger.error("Failed to initialize plugin %s: %s", name, str(e))
                return False
        return plugin is not None and name in self._initialized
    
    def shutdown_plugin(self, name: str) -> bool:
        """
        Shutdown a specific plugin.
        
        Args:
            name: Name of plugin to shutdown
            
        Returns:
            True if plugin was shutdown, False if not found
        """
        plugin = self._plugins.get(name)
        if plugin:
            try:
                if hasattr(plugin, 'shutdown'):
                    plugin.shutdown()
                self._initialized.discard(name)
                logger.debug("Plugin shutdown: %s", name)
                return True
            except Exception as e:
                logger.error("Error shutting down plugin %s: %s", name, str(e))
                return False
        return False
    
    def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all registered plugins.
        
        Returns:
            Dictionary mapping plugin names to initialization success
        """
        results = {}
        for name in self._plugins:
            results[name] = self.initialize_plugin(name)
        return results
    
    def shutdown_all(self) -> Dict[str, bool]:
        """
        Shutdown all registered plugins.
        
        Returns:
            Dictionary mapping plugin names to shutdown success
        """
        results = {}
        for name in list(self._plugins.keys()):  # Copy keys to avoid modification during iteration
            results[name] = self.shutdown_plugin(name)
        return results
    
    def list_plugins(self) -> Dict[str, bool]:
        """
        List all registered plugins and their availability.
        
        Returns:
            Dictionary mapping plugin names to availability status
        """
        result = {}
        for name, plugin in self._plugins.items():
            # Check if plugin has available attribute
            if hasattr(plugin, 'available'):
                result[name] = plugin.available
            else:
                # Default to True if no available attribute
                result[name] = True
        return result
    
    def get_plugins(self) -> Dict[str, object]:
        """Get all registered plugins.
        
        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        return self._plugins.copy()
    
    def get_plugin_count(self) -> int:
        """Get the number of registered plugins."""
        return len(self._plugins)
    
    def get_plugin_names(self) -> Set[str]:
        """Get the set of registered plugin names."""
        return set(self._plugins.keys())