"""Plugin discovery mechanisms for the PluginManager."""

import importlib.util
import threading
from pathlib import Path

import structlog

logger = structlog.get_logger()


def _entry_points_with_timeout(group: str, timeout: float = 5.0):
    """Run entry_points(group=...) in a daemon thread with a timeout.

    importlib.metadata.entry_points() can be extremely slow on Windows
    because it scans every installed distribution. We bound that cost.
    """
    result: list = []
    exc: list = []

    def target():
        try:
            try:
                from importlib.metadata import entry_points
            except ImportError:
                from importlib_metadata import entry_points  # type: ignore[assignment]
            eps = entry_points(group=group)
            result.extend(eps)
        except Exception as e:
            exc.append(e)

    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout)

    if t.is_alive():
        logger.debug("entry_points discovery timed out after %ss", timeout)
        return []
    if exc:
        raise exc[0]
    return result


_ENTRY_POINT_CACHE: dict[str, dict[str, type]] = {}


def get_cached_entry_points(group: str) -> dict[str, type]:
    """Get cached entry points for a group, computing them once per process."""
    from .plugin import SurfacePlugin

    if group not in _ENTRY_POINT_CACHE:
        plugins: dict[str, type] = {}
        discovered_eps = _entry_points_with_timeout(group)
        for ep in discovered_eps:
            try:
                plugin_class = ep.load()
                if issubclass(plugin_class, SurfacePlugin):
                    plugins[ep.name] = plugin_class
            except Exception as e:
                logger.debug("Failed to load surface plugin entry point", ep_name=getattr(ep, "name", "unknown"), error=str(e))
        _ENTRY_POINT_CACHE[group] = plugins
    return _ENTRY_POINT_CACHE[group]


class PluginDiscovery:
    """Handles discovery of plugins from various sources."""

    # Surfaces that should be loaded lazily (expensive imports)
    LAZY_SURFACES: frozenset = frozenset({"z3", "datalog"})

    def __init__(self):
        self.discovered_plugins: dict[str, type] = {}
        self.lazy_classes: dict[str, type] = {}
        self._entry_point_cache: dict[str, type] | None = None

    def discover_builtin_surfaces(self) -> tuple[dict[str, type], dict[str, type]]:
        """
        Discover built-in surfaces.

        Returns:
            Tuple of (eager_surfaces, lazy_surfaces) dictionaries mapping names to classes
        """
        eager_surfaces = {}
        lazy_surfaces = {}

        try:
            from . import surfaces
            from .plugin import SurfacePlugin

            # Core surfaces to load eagerly
            core_surface_mapping = [
                ("python", surfaces.PythonSurface),
                ("prolog", surfaces.PrologSurface),
                ("hy", surfaces.HySurface),
                ("sqlite", surfaces.SQLiteSurface),  # stdlib, always available
            ]

            # Register core surfaces eagerly
            for name, surface_class in core_surface_mapping:
                if surface_class is not None and issubclass(surface_class, SurfacePlugin):
                    eager_surfaces[name] = surface_class

            # Store heavy surfaces for lazy loading
            heavy_surface_mapping = [
                ("llm", surfaces.LLMSurface),  # heavy dependencies (litellm, openai)
                ("z3", surfaces.Z3Surface),
                ("datalog", surfaces.DatalogSurface),
                ("quickjs", surfaces.QuickJSSurface),  # optional dependency
                ("kanren", surfaces.KanrenSurface),  # optional dependency
                ("clingo", surfaces.ClingoSurface),  # optional dependency
                ("duckdb", surfaces.DuckDBSurface),  # optional dependency
                ("julia", surfaces.JuliaSurface),  # optional dependency
                ("tensor", surfaces.TensorSurface),  # optional dependency
            ]

            for name, surface_class in heavy_surface_mapping:
                if surface_class is not None and issubclass(surface_class, SurfacePlugin):
                    lazy_surfaces[name] = surface_class

        except ImportError as e:
            logger.warning("Failed to import built-in surfaces: %s", str(e))

        return eager_surfaces, lazy_surfaces

    def discover_entry_point_plugins(self) -> dict[str, type]:
        """
        Discover plugins via setuptools entry points.

        Returns:
            Dictionary mapping plugin names to classes
        """
        if self._entry_point_cache is not None:
            return self._entry_point_cache

        try:
            entry_point_group = "em_cubed.surfaces"
            plugins = get_cached_entry_points(entry_point_group)

            if plugins:
                logger.info("Entry point plugins discovered", count=len(plugins))

        except ImportError:
            logger.debug("importlib.metadata not available, skipping entry point discovery")
            plugins = {}
        except Exception as e:
            logger.warning("Failed to discover entry point plugins", error=str(e))
            plugins = {}

        self._entry_point_cache = plugins
        return plugins

    def discover_directory_plugins(self, plugin_dir: Path | None = None) -> dict[str, type]:
        """
        Discover plugins by scanning a directory.

        Args:
            plugin_dir: Directory to scan for plugins (defaults to "plugins")

        Returns:
            Dictionary mapping plugin names to classes
        """
        plugin_dir = plugin_dir or Path("plugins")
        plugins: dict[str, type] = {}

        if not plugin_dir.exists():
            logger.debug("Plugin directory does not exist", directory=str(plugin_dir))
            return plugins

        try:
            from .plugin import SurfacePlugin

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
                            if isinstance(attr, type) and issubclass(attr, SurfacePlugin) and attr != SurfacePlugin:
                                try:
                                    # Validate by attempting instantiation
                                    plugin_instance = attr()
                                    plugins[plugin_instance.name] = attr
                                    logger.debug(
                                        "Directory plugin discovered", plugin=plugin_instance.name, file=str(py_file)
                                    )
                                except Exception as e:
                                    logger.warning(
                                        "Failed to validate plugin class",
                                        class_name=attr_name,
                                        file=str(py_file),
                                        error=str(e),
                                    )
                except Exception as e:
                    logger.warning("Failed to load plugin file", file=str(py_file), error=str(e))

            if plugins:
                logger.info("Directory plugins discovered", count=len(plugins), directory=str(plugin_dir))

        except Exception as e:
            logger.warning("Failed to discover directory plugins", directory=str(plugin_dir), error=str(e))

        return plugins

    def discover_all_plugins(
        self, plugin_dir: Path | None = None
    ) -> tuple[
        dict[str, type],  # eager surfaces
        dict[str, type],  # lazy surfaces
        dict[str, type],  # entry point surfaces
        dict[str, type],  # directory surfaces
    ]:
        """
        Discover plugins from all sources.

        Args:
            plugin_dir: Directory to scan for directory-based plugins

        Returns:
            Tuple of (eager_builtin, lazy_builtin, entry_point, directory) plugin dictionaries
        """
        eager_builtin, lazy_builtin = self.discover_builtin_surfaces()
        entry_point = self.discover_entry_point_plugins()
        directory = self.discover_directory_plugins(plugin_dir)

        return eager_builtin, lazy_builtin, entry_point, directory
