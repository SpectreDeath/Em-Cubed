"""Prolog surface integration using pyswip."""

import asyncio
import importlib.util
import os
import re
import tempfile
import threading
from decimal import Decimal
from fractions import Fraction
from numbers import Real
from typing import Any

import structlog

from .base import SurfaceBase, _make_daemon_executor

logger = structlog.get_logger()

# Global lock & shared single-worker executor for PySWIP C FFI calls.
# SWI-Prolog C engine is not thread-safe for concurrent FFI access across multiple threads.
_prolog_lock = threading.RLock()
_prolog_shared_executor = _make_daemon_executor(max_workers=1)
_prolog_instance = None


def _attach_prolog_thread():
    """Attach the current worker thread as a SWI-Prolog engine thread if needed."""
    try:
        from pyswip.core import PL_thread_attach_engine, PL_thread_self
        if PL_thread_self() < 0:
            PL_thread_attach_engine(None)
    except Exception:
        pass  # nosec B110


def _get_shared_prolog():
    global _prolog_instance
    with _prolog_lock:
        _attach_prolog_thread()
        if _prolog_instance is None:
            from pyswip import Prolog

            _prolog_instance = Prolog()
        return _prolog_instance


class PrologSurface(SurfaceBase):
    """Handle Prolog code execution and predicate extraction."""

    _consulted_hashes: set[str] = set()

    @property
    def name(self) -> str:
        return "prolog"

    @property
    def description(self) -> str:
        return "Prolog execution via PySWIP"

    @property
    def available(self) -> bool:
        return self._check_availability()

    def __init__(self, timeout: float | None = None) -> None:
        super().__init__(timeout)
        self._prolog = None  # Lazy initialization of Prolog interpreter
        logger.info("PrologSurface initialized", available=self.available, timeout=self.timeout)

    def _check_availability(self) -> bool:
        """Check if PySWIP is available and importable."""
        if importlib.util.find_spec("pyswip") is None:
            return False
        try:
            import pyswip  # noqa: F401
            return True
        except Exception as e:
            logger.warning("PySWIP import failed", error=str(e))
            return False

    def extract_tags(self, prolog_source: str | None) -> list[str]:
        """Extract predicate names from Prolog source as logic_tags."""
        if not prolog_source:
            return []
        import re

        # Match predicate heads: name( or name :-
        heads = re.findall(r"^([a-z][a-zA-Z0-9_]*)\s*[:(]", prolog_source, re.MULTILINE)
        # Deduplicate, exclude Prolog builtins
        builtins = {"not", "is", "true", "fail", "assert", "retract"}
        return list(dict.fromkeys(h for h in heads if h not in builtins))

    def _get_prolog(self):
        """Get or create the Prolog interpreter instance."""
        if self._prolog is not None:
            return self._prolog
        return _get_shared_prolog()

    def shutdown(self) -> None:
        """Shutdown Prolog engine."""
        if self._prolog is not None:
            logger.info("Shutting down Prolog surface")
            self._prolog = None

    def _prolog_safe_value(self, value: Any) -> str:
        """Convert a value to a safe Prolog representation."""
        if isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "true" if value else "fail"
        elif isinstance(value, str):
            # Escape single quotes and wrap in single quotes
            escaped = value.replace("\\", "\\\\").replace("'", "\\'")
            return "'" + escaped + "'"
        elif isinstance(value, (list, tuple)):
            # Convert to Prolog list
            elements = [self._prolog_safe_value(item) for item in value]
            return f"[{','.join(elements)}]"
        else:
            # Convert to string and quote
            escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
            return "'" + escaped + "'"

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute Prolog code - implementation with timeout protection."""
        logger.info("Executing Prolog code", code_length=len(code), has_context=context is not None)

        if not self.available:
            logger.error("Attempted Prolog execution but PySWIP not available")
            return {"status": "error", "message": "PySWIP not available"}

        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(_prolog_shared_executor, self._run_prolog_code, code, context)
        except (TimeoutError, asyncio.CancelledError):
            logger.warning("Prolog query timed out", query=code, timeout=self.timeout)
            return {"status": "error", "message": f"Query execution timed out after {self.timeout}s"}

    def _run_prolog_code(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        with _prolog_lock:
            _attach_prolog_thread()
            try:
                prolog = self._get_prolog()
                # Load context as facts if provided
                if context:
                    for key, value in context.items():
                        safe_value = self._prolog_safe_value(value)
                        prolog.assertz(f"{key}({safe_value})")

                stripped_code = code.strip()

                # Built-ins that modify the dynamic database and should be
                # executed as goals, NOT asserted as facts/rules.
                _IMPURE_BUILTINS = {
                    "retractall",
                    "retract",
                    "asserta",
                    "assertz",
                    "abolish",
                    "flush_output",
                    "flush",
                    "close",
                    "op",
                    "set_prolog_flag",
                    "setof",
                    "bagof",
                    "findall",
                    "maplist",
                    "call",
                    "once",
                }

                # Improved mode detection:
                # - Explicit queries start with ?-
                # - Impure built-ins that modify the DB are always executed as goals
                # - Code containing rule definitions (:-) followed by ?- is split into assert + query
                # - Otherwise, trailing . indicates assertion (fact/rule)
                is_query = False
                processed_code = stripped_code

                if stripped_code.startswith("?-"):
                    is_query = True
                    processed_code = stripped_code[2:].strip().rstrip(".").strip()
                elif "?-" in stripped_code:
                    parts = stripped_code.split("?-")
                    rule_part = parts[0].strip()
                    query_part = parts[1].strip().rstrip(".").strip()
                    if rule_part:
                        try:
                            rule_flat = " ".join(rule_part.split())
                            rule_clean = rule_flat.rstrip(".")
                            prolog.assertz(rule_clean)
                        except Exception as assert_err:
                            logger.warning("Prolog rule assertion warning", error=str(assert_err))
                    processed_code = query_part
                    is_query = True
                elif "\n" in stripped_code:
                    lines = [
                        line for line in stripped_code.split("\n") if line.strip() and not line.strip().startswith("%")
                    ]
                    program = "\n".join(lines)
                    if not program.strip():
                        return {"status": "ok", "message": "No Prolog code to execute"}

                    import hashlib

                    code_hash = hashlib.sha256(program.encode("utf-8")).hexdigest()
                    if code_hash in self._consulted_hashes:
                        logger.info("Prolog rules already consulted (cache hit)", hash=code_hash)
                        return {"status": "ok", "message": "Multi-line Prolog code consulted successfully"}

                    try:
                        fd, path = tempfile.mkstemp(suffix=".pl", prefix="em3_prolog_")
                        try:
                            file_obj = os.fdopen(fd, "w", encoding="utf-8")
                            try:
                                file_obj.write(program)
                                file_obj.flush()
                                os.fsync(file_obj.fileno())
                            finally:
                                file_obj.close()
                            module_match = re.search(r":-\s*module\(\s*([A-Za-z_][A-Za-z0-9_]*)", program)
                            if module_match:
                                module_name = module_match.group(1)
                                try:
                                    if list(prolog.query(f"current_module({module_name})")):
                                        logger.info("Prolog module already loaded, skipping consult", module=module_name)
                                        return {"status": "ok", "message": f"Module {module_name} already loaded"}
                                except Exception as module_check_err:
                                    logger.info(
                                        "Prolog module check failed, proceeding with consult",
                                        module=module_name,
                                        error=str(module_check_err),
                                    )
                            try:
                                prolog.consult(path)
                                self._consulted_hashes.add(code_hash)
                            except Exception as consult_err:
                                if "redefine module" in str(consult_err) or "Already loaded" in str(consult_err):
                                    logger.info("Prolog module already loaded, skipping re-consult", error=str(consult_err))
                                    self._consulted_hashes.add(code_hash)
                                else:
                                    raise
                            return {"status": "ok", "message": "Multi-line Prolog code consulted successfully"}
                        finally:
                            try:
                                os.unlink(path)
                            except OSError:
                                pass  # nosec B110 - intentional fallback; caller handles None/False return
                    except Exception as consult_err:
                        logger.warning("Prolog file consultation failed, falling back to assertz", error=str(consult_err))
                        i = 0
                        while i < len(lines):
                            item = lines[i].strip()
                            j = i + 1
                            while j < len(lines) and not item.endswith("."):
                                item = item + " " + lines[j].strip()
                                j += 1
                            i = j
                            if not item:
                                continue
                            if item.startswith(":-") and re.search(r":-\s*module\s*\(", item):
                                continue
                            directive = item.startswith(":-")
                            query_prefix = item.startswith("?-")
                            clean = item.rstrip(".").strip()
                            if directive or query_prefix:
                                try:
                                    list(prolog.query(clean[2:].strip()))
                                except Exception:
                                    pass  # nosec B110 - intentional fallback; caller handles None/False return
                            elif clean:
                                try:
                                    prolog.assertz(clean)
                                except Exception as assert_err:
                                    logger.warning("Prolog assert warning", error=str(assert_err))
                        self._consulted_hashes.add(code_hash)
                        return {"status": "ok", "message": "Multi-line Prolog code processed via fallback"}
                elif stripped_code.endswith("."):
                    head_word = stripped_code.split("(")[0].split(" ")[0].strip().rstrip(".")
                    if head_word in _IMPURE_BUILTINS or re.search(r"\bis\b", stripped_code):
                        is_query = True
                        processed_code = stripped_code.rstrip(".").strip()
                    else:
                        processed_code = stripped_code.rstrip(".").strip()
                else:
                    is_query = True
                    processed_code = stripped_code

                if is_query:
                    # Query mode: starts with ?- or determined to be query
                    logger.info("Prolog query mode detected", query=processed_code)
                    result = list(prolog.query(processed_code))

                    if len(result) > 1000:
                        result = result[:1000]  # Truncate for safety

                    logger.info("Prolog query raw result", query=processed_code, raw_result_repr=repr(result))

                    # Normalize all Prolog query result bindings to standard Python types
                    if result:
                        is_arithmetic = bool(re.search(r"\bis\b", stripped_code) or " is " in processed_code)

                        def _normalize_val(v: Any) -> Any:
                            if isinstance(v, bool):
                                return v
                            if is_arithmetic:
                                if isinstance(v, Real) and not isinstance(v, bool):
                                    return float(v)
                                if isinstance(v, (Decimal, Fraction)):
                                    return float(v)
                                if (
                                    hasattr(v, "__module__")
                                    and getattr(v, "__module__", "").startswith("numpy.")
                                    and hasattr(v, "item")
                                ):
                                    try:
                                        return float(v.item())
                                    except (ValueError, TypeError):
                                        return v
                            if isinstance(v, (bytes, bytearray)):
                                s = v.decode("utf-8", errors="ignore")
                                if is_arithmetic:
                                    try:
                                        return float(s)
                                    except (ValueError, TypeError):
                                        pass
                                return s
                            if isinstance(v, str):
                                if is_arithmetic:
                                    try:
                                        return float(v)
                                    except (ValueError, TypeError):
                                        pass
                                return v
                            if isinstance(v, (list, tuple)):
                                return [_normalize_val(x) for x in v]
                            if isinstance(v, dict):
                                return {k: _normalize_val(val) for k, val in v.items()}
                            # Fallback for PySWIP Atom, Variable, Functor or custom terms
                            s = str(v)
                            if is_arithmetic:
                                try:
                                    return float(s)
                                except (ValueError, TypeError):
                                    pass
                            return s

                        normalized_results: list[dict[str, Any]] = []
                        for row in result:
                            if isinstance(row, dict):
                                new_row: dict[str, Any] = {k: _normalize_val(v) for k, v in row.items()}
                                normalized_results.append(new_row)
                            else:
                                normalized_results.append(row)
                        result = normalized_results

                    logger.info("Prolog query successful", result_count=len(result))
                    return {"status": "ok", "message": "Query executed successfully", "result": result}
                else:
                    # Assertion mode: fact or rule
                    logger.info("Prolog assert mode detected")
                    # Attempt assertz; if SWI-Prolog raises permission_error(modify,
                    # static_procedure) (happens when the predicate exists as a
                    # statically-compiled clause, e.g. from a previous consult in
                    # the same global Prolog singleton), declare it dynamic and retry.
                    try:
                        prolog.assertz(processed_code)
                    except Exception as first_err:
                        err_str = str(first_err)
                        if "permission_error" in err_str and "static_procedure" in err_str:
                            import re as _re

                            head = processed_code.split(":-")[0].strip()
                            m = _re.match(r"([a-z][a-zA-Z0-9_]*)\s*\(", head)
                            if m:
                                functor = m.group(1)
                                inner = head[head.index("(") + 1 :]
                                depth, arity = 1, 1
                                for ch in inner:
                                    if ch in "([":
                                        depth += 1
                                    elif ch in ")]":
                                        depth -= 1
                                        if depth == 0:
                                            break
                                    elif ch == "," and depth == 1:
                                        arity += 1
                            else:
                                functor = head.strip()
                                arity = 0

                            try:
                                try:
                                    list(prolog.query(f"abolish({functor}/{arity})"))
                                except Exception:  # nosec B110
                                    pass
                                list(prolog.query(f"dynamic({functor}/{arity})"))
                                prolog.assertz(processed_code)
                            except Exception as retry_err:
                                logger.warning(
                                    "Prolog dynamic declaration + assertz failed",
                                    error=str(retry_err),
                                )
                                return {"status": "error", "message": str(retry_err)}
                        else:
                            raise
                    logger.info("Prolog assertion successful")
                    return {"status": "ok", "message": "Code asserted successfully"}

            except Exception as e:
                logger.exception("Prolog execution failed", error=str(e), code=code)
                return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return self.available
