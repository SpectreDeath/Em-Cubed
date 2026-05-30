"""Cangjie surface integration for high-performance logic orchestration."""

import asyncio
import concurrent.futures as _cf
import json
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


@lru_cache(maxsize=1)
def _find_cjc(timeout: float = 2.0) -> Optional[str]:
    """Return the path to `cjc` or None.

    Runs `shutil.which` in a worker thread so that a stalled network PATH
    entry on Windows cannot block the event loop indefinitely.
    """
    with _cf.ThreadPoolExecutor(max_workers=1, thread_name_prefix="cjc_which") as pool:
        fut = pool.submit(shutil.which, "cjc")
        try:
            return fut.result(timeout=timeout)
        except (_cf.TimeoutError, Exception):
            return None


class CangjieSurface(SurfaceBase):
    """Handle Cangjie code compilation and execution using cjc."""

    @property
    def name(self) -> str:
        return "cangjie"

    @property
    def description(self) -> str:
        return "High-Performance Logic Orchestrator (Cangjie/LLVM)"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        # Use the cached, timeout-guarded lookup so we never block indefinitely.
        self.cjc_path = _find_cjc()
        logger.info("CangjieSurface initialized", available=self.available, cjc_path=self.cjc_path)

    def _check_availability(self) -> bool:
        """Check if cjc (Cangjie Compiler) is available in the system path."""
        return _find_cjc() is not None

    @staticmethod
    def extract_tags(source: Optional[str]) -> list:
        """Extract function names and effect handlers from Cangjie source."""
        if not source:
            return []
        import re

        tags = set()
        
        # Extract function names: func name(...)
        fn_matches = re.findall(r"func\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(", source)
        tags.update(fn_matches)
        
        # Extract effect names: effect Name
        eff_matches = re.findall(r"effect\s+([a-zA-Z][a-zA-Z0-9_]*)", source)
        tags.update(eff_matches)
        
        return list(tags)

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Cangjie code with timeout protection."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compile and run Cangjie code.
        
        This follows a Compiler-in-the-Loop strategy:
        1. Write source to temp file.
        2. Compile with cjc.
        3. Execute binary.
        4. Clean up.
        """
        if not self.available:
            return {"status": "error", "message": "Cangjie compiler (cjc) not found"}

        with tempfile.TemporaryDirectory(prefix="cj_surface_") as tmpdir:
            tmpdir_path = Path(tmpdir)
            source_file = tmpdir_path / "main.cj"
            bin_file = tmpdir_path / "main"
            
            # 1. Write source
            # For execution, we might need to wrap the snippet in a main func if not present
            if "main" not in code:
                full_code = f"main() {{\n{code}\n}}"
            else:
                full_code = code
                
            source_file.write_text(full_code, encoding="utf-8")
            
            # 2. Compile
            logger.info("Compiling Cangjie code", path=str(source_file))
            compile_proc = await asyncio.create_subprocess_exec(
                "cjc", "-o", str(bin_file), str(source_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await compile_proc.communicate()
            
            if compile_proc.returncode != 0:
                error_msg = stderr.decode().strip() or stdout.decode().strip()
                logger.error("Cangjie compilation failed", error=error_msg)
                return {"status": "error", "message": f"Compilation failed: {error_msg}"}
            
            # 3. Execute via stdin-based context passing
            logger.info("Executing Cangjie binary", path=str(bin_file))

            exec_proc = await asyncio.create_subprocess_exec(
                str(bin_file),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdin_data = json.dumps(context).encode() if context else b""
            stdout, stderr = await exec_proc.communicate(input=stdin_data)
            
            if exec_proc.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error("Cangjie execution failed", error=error_msg)
                return {"status": "error", "message": f"Execution failed: {error_msg}"}
                
            result = stdout.decode().strip()
            logger.info("Cangjie execution successful")
            return {"status": "ok", "value": result}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return self._check_availability()
