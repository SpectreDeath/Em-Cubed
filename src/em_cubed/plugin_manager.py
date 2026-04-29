"""Plugin system for extensible surface architecture."""
import importlib.util
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()


class SurfacePlugin(ABC):
    """Base class for surface plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Surface name (e.g., 'python', 'prolog')."""
        pass

    @property
    @abstractmethod
    def available(self) -> bool:
        """Check if surface dependencies are available."""
        pass

    @abstractmethod
    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute code on this surface."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Health check for this surface."""
        pass

    @abstractmethod
    def extract_tags(self, source: Optional[str]) -> list:
        """Extract relevant tags from source code."""
        pass

    def initialize(self) -> None:
        """Optional initialization hook."""
        pass

    def shutdown(self) -> None:
        """Optional shutdown hook."""
        pass


class PluginManager:
    """Manage surface plugins with multiple discovery mechanisms."""

    def __init__(self):
        self._plugins: Dict[str, SurfacePlugin] = {}
        self._discover_builtin()
        self._discover_entry_points()
        self._discover_directory()

        # Initialize all plugins
        for plugin in self._plugins.values():
            try:
                plugin.initialize()
            except Exception as e:
                logger.warning("Failed to initialize plugin", plugin=plugin.name, error=str(e))

    def __del__(self):
        """Clean up plugins on deletion."""
        for plugin in self._plugins.values():
            try:
                plugin.shutdown()
            except Exception as e:
                logger.warning("Failed to shutdown plugin", plugin=plugin.name, error=str(e))

    def _discover_builtin(self):
        """Register built-in surfaces."""
        try:
            from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface, Z3Surface, DatalogSurface
            self.register("python", PythonSurface())
            self.register("prolog", PrologSurface())
            self.register("hy", HySurface())
            self.register("z3", Z3Surface())
            self.register("datalog", DatalogSurface())
            logger.info("Built-in plugins registered", count=5)
        except Exception as e:
            logger.error("Failed to register built-in plugins", error=str(e))

    def _discover_entry_points(self):
        """Discover plugins via setuptools entry points."""
        try:
            import entry_points
            discovered = 0
            for ep in entry_points.get_group_all("em_cubed.surfaces"):
                try:
                    plugin_class = ep.load()
                    plugin = plugin_class()
                    self.register(ep.name, plugin)
                    discovered += 1
                except Exception as e:
                    logger.warning("Failed to load plugin from entry point",
                                 entry_point=ep.name, error=str(e))
            if discovered > 0:
                logger.info("Entry point plugins registered", count=discovered)
        except ImportError:
            logger.debug("entry-points package not available, skipping entry point discovery")
        except Exception as e:
            logger.warning("Failed to discover entry point plugins", error=str(e))

    def _discover_directory(self, plugin_dir: Optional[Path] = None):
        """Discover plugins by scanning directory."""
        plugin_dir = plugin_dir or Path("plugins")
        if not plugin_dir.exists():
            return

        discovered = 0
        try:
            # Scan for Python files in plugin directory
            for py_file in plugin_dir.glob("**/*.py"):
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Look for plugin classes (inherit from SurfacePlugin)
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and
                                issubclass(attr, SurfacePlugin) and
                                attr != SurfacePlugin):
                                try:
                                    plugin = attr()
                                    plugin_name = plugin.name
                                    self.register(plugin_name, plugin)
                                    discovered += 1
                                    logger.debug("Directory plugin loaded", plugin=plugin_name, file=str(py_file))
                                except Exception as e:
                                    logger.warning("Failed to instantiate plugin class",
                                                 class_name=attr_name, file=str(py_file), error=str(e))
                except Exception as e:
                    logger.warning("Failed to load plugin file", file=str(py_file), error=str(e))

            if discovered > 0:
                logger.info("Directory plugins registered", count=discovered, directory=str(plugin_dir))
        except Exception as e:
            logger.warning("Failed to discover directory plugins", directory=str(plugin_dir), error=str(e))

    def register(self, name: str, plugin: SurfacePlugin):
        """Register a plugin."""
        if name in self._plugins:
            logger.warning("Plugin already registered, replacing", plugin=name)
        self._plugins[name] = plugin
        logger.debug("Plugin registered", plugin=name)

    def get(self, name: str) -> Optional[SurfacePlugin]:
        """Get plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> Dict[str, bool]:
        """List all plugins and their availability."""
        return {name: plugin.available for name, plugin in self._plugins.items()}

    def get_available_surfaces(self) -> List[str]:
        """Get list of available surface names."""
        return [name for name, plugin in self._plugins.items() if plugin.available]

    def get_surface_info(self) -> List[Dict[str, Any]]:
        """Get detailed information about all surfaces."""
        info = []
        for name, plugin in self._plugins.items():
            info.append({
                "name": name,
                "available": plugin.available,
                "description": getattr(plugin, "description", f"{name.title()} surface"),
            })
        return info