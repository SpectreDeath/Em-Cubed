"""WASM surface integration for executing WebAssembly code using wasmtime."""

import asyncio
import base64
from typing import Dict, Any, Optional, List, cast
import structlog
import wasmtime

from .base import SurfaceBase

logger = structlog.get_logger()


class WASMSurface(SurfaceBase):
    """Handle WebAssembly code compilation and execution using wasmtime."""

    def __init__(self, timeout: Optional[float] = None):
        """Initialize WASM surface.
        
        Args:
            timeout: Optional timeout in seconds for WASM execution
        """
        super().__init__(timeout)
        self._wasm_available = self._check_wasm_availability()
        self._engine: Optional[wasmtime.Engine] = None
        logger.info("WASMSurface initialized", available=self._wasm_available, timeout=self.timeout)

    def initialize(self) -> None:
        """Initialize the WASM surface."""
        if self._wasm_available:
            self._engine = wasmtime.Engine()
            logger.debug("WASM engine initialized")

    def shutdown(self) -> None:
        """Shutdown the WASM surface."""
        self._engine = None
        logger.debug("WASM engine shut down")
        super().shutdown()

    def _check_wasm_availability(self) -> bool:
        """Check if wasmtime library is installed."""
        try:
            import wasmtime  # noqa: F401
            return True
        except ImportError:
            logger.warning("wasmtime not installed for WASM surface")
            return False

    @property
    def name(self) -> str:
        return "wasm"

    @property
    def description(self) -> str:
        return "WebAssembly execution with sandboxed runtime"

    @property
    def available(self) -> bool:
        return self._wasm_available

    def extract_tags(self, wasm_source: Optional[str]) -> List[str]:
        """Extract exported function names from WASM source as heuristic_tags."""
        if not wasm_source:
            return []
        
        try:
            import wasmtime
            engine = wasmtime.Engine()
            
            # Identify if it is .wat text format or raw/base64 binary wasm
            source_stripped = wasm_source.strip()
            if source_stripped.startswith("(module"):
                module = wasmtime.Module(engine, wasm_source)
            else:
                try:
                    binary_data = base64.b64decode(source_stripped)
                    module = wasmtime.Module(engine, binary_data)
                except Exception:
                    module = wasmtime.Module(engine, wasm_source)
            
            # Extract exported functions
            funcs = []
            for exp in module.exports:
                try:
                    if hasattr(exp.type, 'func') and exp.type.func() is not None:
                        funcs.append(exp.name)
                except Exception:
                    pass
            return funcs
            
        except Exception as e:
            logger.warning("Failed to extract WASM exports using wasmtime, falling back to regex", error=str(e))
            import re
            funcs = re.findall(r'\(func\s+(?:\$?(\w+))', wasm_source)
            return list(dict.fromkeys(funcs))

    def _run_wasm(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synchronous WASM compilation and execution to run inside the thread pool executor."""
        # Import wasmtime here to handle case where it's not available
        try:
            import wasmtime
        except ImportError:
            return {"status": "error", "message": "WASM runtime (wasmtime) not available"}
        
        # Use initialized engine if available, otherwise create a temporary one
        engine = self._engine if self._engine is not None else wasmtime.Engine()
        store = wasmtime.Store(engine)
        
        # 1. Compile WASM source
        code_stripped = code.strip()
        if code_stripped.startswith("(module"):
            module = wasmtime.Module(engine, code_stripped)
        else:
            try:
                binary_data = base64.b64decode(code_stripped)
                module = wasmtime.Module(engine, binary_data)
            except Exception:
                module = wasmtime.Module(engine, code_stripped)
        
        # 2. Setup linker and WASI config
        linker = wasmtime.Linker(engine)
        linker.define_wasi()
        
        wasi_config = wasmtime.WasiConfig()
        wasi_config.inherit_stdout()
        wasi_config.inherit_stderr()
        store.set_wasi(wasi_config)
        
        # 3. Instantiate the module
        instance = linker.instantiate(store, module)
        exports = instance.exports(store)
        
        # 4. Locate entry function
        entry_point = (context or {}).get("entry_point")
        func = None
        if entry_point and entry_point in exports:
            func = exports[entry_point]
        else:
            # Fallback to look for common entry points
            for name in ["main", "run", "execute", "solve", "add"]:
                if name in exports and isinstance(exports[name], wasmtime.Func):
                    func = exports[name]
                    break
            if not func:
                # Fallback to the first exported function in the module
                for name, item in exports.items():
                    if isinstance(item, wasmtime.Func):
                        func = item
                        break
                        
        if not func:
            return {"status": "error", "message": "No exported function found in WASM module"}
            
        # 5. Extract input values and map them to arguments
        import wasmtime
        func_val = cast(wasmtime.Func, func)
        func_typed = cast("Any", func_val.type(store))
        params: List[Any] = []
        if hasattr(func_typed, 'params'):
            params_val = getattr(func_typed, 'params')
            if hasattr(params_val, 'vals'):
                params = list(getattr(params_val, 'vals'))
            else:
                params = list(params_val)
        
        args: List[Any] = []
        
        input_data = (context or {}).get("skill_input", {})
        ctx = context or {}
        if "args" in ctx:
            raw_args = ctx["args"]
        elif isinstance(input_data, dict):
            raw_args = [input_data[k] for k in sorted(input_data.keys())]
        elif isinstance(input_data, list):
            raw_args = input_data
        else:
            raw_args = []
            
        for i, param_type in enumerate(params):
            val = raw_args[i] if i < len(raw_args) else 0
            
            try:
                type_str = str(param_type)
                if "i32" in type_str:
                    args.append(int(val))
                elif "i64" in type_str:
                    args.append(int(val))
                elif "f32" in type_str or "f64" in type_str:
                    args.append(int(val))
                else:
                    args.append(val)
            except Exception:
                args.append(val)
                
        # 6. Execute exported function
        result_val = func_val(store, *args)  # type: ignore[no-untyped-def,misc]
        
        # In case of multiple return values, return the list or first item
        if isinstance(result_val, list) and len(result_val) == 1:
            result_val = result_val[0]
            
        return {
            "status": "ok",
            "value": result_val
        }

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute WebAssembly code and return results."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compile and execute WebAssembly code safely on the thread executor."""
        logger.info("Executing WebAssembly code", code_length=len(code))

        if not self.available:
            return {"status": "error", "message": "WASM runtime (wasmtime) not available"}

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                self._executor,
                self._run_wasm,
                code,
                context
            )
            logger.info("WASM execution successful")
            return result
        except Exception as e:
            logger.exception("WASM execution failed", error=str(e))
            return {
                "status": "error",
                "message": f"WASM execution failed: {str(e)}"
            }

    async def health(self) -> bool:
        """Check if the WASM surface is available."""
        return self._wasm_available