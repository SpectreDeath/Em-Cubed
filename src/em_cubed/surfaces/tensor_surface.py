"""Tensor surface integration for PyTorch GPU/CUDA tensor acceleration and isolated ML operations."""

import gc
from typing import Any
import structlog
from asteval import Interpreter

from .base import SurfaceBase

logger = structlog.get_logger()

try:
    import torch

    _TORCH_AVAILABLE = True
except ImportError:
    torch = None  # type: ignore[assignment]
    _TORCH_AVAILABLE = False


class TensorSurface(SurfaceBase):
    """Handle hardware-accelerated tensor computations via PyTorch with VRAM isolation."""

    @property
    def name(self) -> str:
        return "tensor"

    @property
    def description(self) -> str:
        return "PyTorch GPU/CUDA hardware-accelerated tensor computing surface"

    @property
    def available(self) -> bool:
        return _TORCH_AVAILABLE

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        self.device = "cuda" if (_TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu"
        logger.info("TensorSurface initialized", available=self.available, device=self.device)

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute PyTorch code with AST isolation and automatic VRAM memory cleanup."""
        if not self.available:
            return {
                "status": "error",
                "message": "PyTorch is not available. Install with `pip install torch`.",
            }

        logger.info("Executing Tensor PyTorch code", code_length=len(code), device=self.device)

        try:
            # Build AST interpreter populated with PyTorch module symbols
            syms: dict[str, Any] = {
                "torch": torch,
                "device": self.device,
                "float32": torch.float32 if _TORCH_AVAILABLE else None,
                "float64": torch.float64 if _TORCH_AVAILABLE else None,
                "int64": torch.int64 if _TORCH_AVAILABLE else None,
            }

            if context:
                for k, v in context.items():
                    if k.isidentifier():
                        syms[k] = v

            interpreter = Interpreter(symtable=syms, use_numpy=True)
            interpreter.eval(code)

            if interpreter.errors:
                err_msg = "\n".join(str(e.get_error()) for e in interpreter.errors)
                return {"status": "error", "message": f"Tensor AST execution error: {err_msg}"}

            # Retrieve result variable if specified or return symbol table modifications
            result_val = interpreter.symtable.get("result", None)

            # Convert tensor to serializable list or numpy array
            if _TORCH_AVAILABLE and isinstance(result_val, torch.Tensor):
                if result_val.is_cuda:
                    result_val = result_val.cpu()
                result_val = result_val.detach().numpy().tolist()

            return {
                "status": "ok",
                "value": result_val,
                "device": self.device,
            }

        except Exception as e:
            logger.exception("Tensor execution failed", error=str(e))
            return {"status": "error", "message": str(e)}

        finally:
            # Clean up GPU VRAM cache if CUDA was used
            if _TORCH_AVAILABLE and torch.cuda.is_available():
                try:
                    torch.cuda.empty_cache()
                except Exception:
                    pass
            gc.collect()

    async def health(self) -> bool:
        """Check if PyTorch tensor surface is operational."""
        if not self.available:
            return False
        try:
            t = torch.tensor([1.0, 2.0])
            res = (t + 1.0).tolist()
            return res == [2.0, 3.0]
        except Exception:
            return False

    def extract_tags(self, source: str | None) -> list[str]:
        """Extract PyTorch operations and neural network layers from code."""
        if not source:
            return []
        import re

        tags = re.findall(r"torch\.([a-zA-Z0-9_]+)", source)
        tags.extend(re.findall(r"nn\.([a-zA-Z0-9_]+)", source))
        return list(dict.fromkeys(tags))
