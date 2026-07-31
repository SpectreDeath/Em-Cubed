"""Containerized execution for surface plugins."""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any, cast

import structlog

from .plugin import SurfacePlugin

logger = structlog.get_logger()


class ContainerizedSurfacePlugin(SurfacePlugin):
    """Surface plugin that executes code in isolated containers."""

    def __init__(self, surface_name: str, timeout: float | None = None):
        """Initialize containerized surface plugin.

        Args:
            surface_name: Name of the surface (e.g., 'python', 'prolog')
            timeout: Optional timeout in seconds for container execution
        """
        super().__init__(timeout)
        self._surface_name = surface_name
        self._container_image = f"em-cubed-{surface_name}:latest"
        self._docker_available = self._check_docker_availability()

    def _check_docker_availability(self) -> bool:
        """Check if Docker/Podman is available."""
        try:
            # Try docker first, then podman
            for cmd in ["docker", "podman"]:
                result = os.system(f"{cmd} version >nul 2>&1")  # nosec B605
                if result == 0:
                    self._container_runtime = cmd
                    logger.info("Container runtime available", runtime=cmd)
                    return True
            return False
        except Exception:
            return False

    @property
    def name(self) -> str:
        """Surface name (e.g., 'python', 'prolog')."""
        return self._surface_name

    @property
    def available(self) -> bool:
        """Check if surface dependencies are available."""
        return self._docker_available

    async def execute(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute code in isolated container.

        Args:
            code: Source code to execute
            context: Optional execution context

        Returns:
            Dict with status, value/error message
        """
        if not self.available:
            return {"status": "error", "message": f"Container runtime ({self._container_runtime}) not available"}

        # Create temporary directory for volume mounts
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write code to file
            code_file = temp_path / "skill_code.txt"
            code_file.write_text(code, encoding="utf-8")

            # Write context to file if provided
            if context:
                context_file = temp_path / "context.json"
                context_file.write_text(json.dumps(context), encoding="utf-8")

            # Prepare container command
            container_cmd = [
                self._container_runtime,
                "run",
                "--rm",
                "--memory=512m",  # Limit memory
                "--cpus=0.5",  # Limit CPU
                "--network=none",  # Disable network
                "--read-only",  # Read-only root filesystem
                f"--volume={temp_path}:/execution:ro",
                f"--volume={temp_path}:/output:rw",
                self._container_image,
                "python",
                "-m",
                "em_cubed.container_executor",
                str(code_file.relative_to(temp_path)),
                str(context_file.relative_to(temp_path)) if context else "null",
                str(self.timeout or 30),
            ]

            try:
                # Execute container with timeout.
                # nosec B603,B601 — create_subprocess_exec uses a fixed arg list (no shell=True).
                # `container_cmd` is built from hardcoded constants; the container is the security boundary.
                process = await asyncio.create_subprocess_exec(  # nosec B603
                    *container_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=self.timeout or 35,  # Slight buffer for container startup
                    )

                    if process.returncode == 0:
                        # Parse result from output
                        result_str = stdout.decode("utf-8").strip()
                        try:
                            result = json.loads(result_str)
                            return cast(dict[str, Any], result)
                        except json.JSONDecodeError:
                            return {"status": "error", "message": f"Invalid JSON output from container: {result_str}"}
                    else:
                        error_msg = stderr.decode("utf-8").strip()
                        return {"status": "error", "message": f"Container execution failed: {error_msg}"}

                except TimeoutError:
                    process.kill()
                    await process.wait()
                    return {"status": "error", "message": f"Container execution timed out after {self.timeout or 30}s"}

            except Exception as e:
                logger.error("Container execution error", error=str(e))
                return {"status": "error", "message": f"Container execution error: {e!s}"}

    async def health(self) -> bool:
        """Check if containerized surface is operational."""
        if not self._docker_available:
            return False

        try:
            # nosec B603 — fixed arg list, no shell=True; inspects a known image name only.
            process = await asyncio.create_subprocess_exec(  # nosec B603
                self._container_runtime,
                "image",
                "inspect",
                self._container_image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _stdout, _stderr = await process.communicate()
            return process.returncode == 0
        except Exception:
            return False

    def extract_tags(self, source: str | None) -> list[str]:
        """Extract relevant tags from source code.

        Delegates to the base surface implementation since tags are
        based on code content, not execution environment.
        """
        # Import the actual surface to reuse its tag extraction
        from .surfaces import (
            datalog_surface,
            hy_surface,
            prolog_surface,
            python_surface,
            z3_surface,
        )

        surface_map = {
            "python": python_surface.PythonSurface,
            "prolog": prolog_surface.PrologSurface,
            "hy": hy_surface.HySurface,
            "z3": z3_surface.Z3Surface,
            "datalog": datalog_surface.DatalogSurface,
        }

        surface_class: Any = surface_map.get(self._surface_name)
        if surface_class:
            surface_instance = surface_class()
            return cast(list[str], surface_instance.extract_tags(source))
        return []


# Factory function to create containerized surfaces
def create_containerized_surface(surface_name: str, timeout: float | None = None) -> SurfacePlugin:
    """Factory function to create containerized surface plugins.

    Args:
        surface_name: Name of the surface to containerize
        timeout: Optional timeout in seconds

    Returns:
        ContainerizedSurfacePlugin instance
    """
    return ContainerizedSurfacePlugin(surface_name, timeout)
