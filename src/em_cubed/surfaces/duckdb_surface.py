"""DuckDB surface integration for analytical SQL execution and zero-copy memory querying."""

from typing import Any
import structlog
from .base import SurfaceBase

logger = structlog.get_logger()

try:
    import duckdb

    _DUCKDB_AVAILABLE = True
except ImportError:
    duckdb = None  # type: ignore[assignment]
    _DUCKDB_AVAILABLE = False


class DuckDBSurface(SurfaceBase):
    """Handle analytical SQL execution on an in-memory DuckDB engine."""

    @property
    def name(self) -> str:
        return "duckdb"

    @property
    def description(self) -> str:
        return "In-memory DuckDB analytical engine"

    @property
    def available(self) -> bool:
        return _DUCKDB_AVAILABLE

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        self._sessions: dict[str, Any] = {}
        logger.info("DuckDBSurface initialized", available=self.available)

    def _get_connection(self, context: dict[str, Any] | None = None):
        """Get or create a DuckDB connection based on session_id in context."""
        if not _DUCKDB_AVAILABLE:
            raise RuntimeError("duckdb is not installed in the environment. Install via `pip install duckdb`.")

        session_id = (context or {}).get("session_id")
        if session_id:
            if session_id not in self._sessions:
                conn = duckdb.connect(database=":memory:")
                self._sessions[session_id] = conn
            return self._sessions[session_id], False

        conn = duckdb.connect(database=":memory:")
        return conn, True

    def close_session(self, session_id: str) -> None:
        """Explicitly close a session's connection."""
        if session_id in self._sessions:
            try:
                self._sessions[session_id].close()
            except Exception:
                pass  # nosec B110 - intentional cleanup fallback
            del self._sessions[session_id]

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute SQL code on DuckDB with optional context tables or session persistence."""
        if not self.available:
            return {
                "status": "error",
                "message": "DuckDB is not available. Install with `pip install duckdb`.",
            }

        logger.info("Executing DuckDB SQL code", code_length=len(code))

        try:
            conn, should_close = self._get_connection(context)

            # Register contextual DataFrames or dict tables if provided in context
            ctx_tables = (context or {}).get("tables", {})
            for name, data in ctx_tables.items():
                try:
                    conn.register(name, data)
                except Exception as reg_err:
                    logger.warning("Failed to register context table", table=name, error=str(reg_err))

            statements = [s.strip() for s in code.split(";") if s.strip()]
            results: list[Any] = []
            last_result: Any = None

            for stmt in statements:
                res = conn.execute(stmt)
                if res.description:
                    df_res = res.fetchdf()
                    last_result = df_res.to_dict(orient="records")
                    results.append(last_result)
                else:
                    last_result = {"rows_affected": getattr(res, "rowcount", 0)}
                    results.append(last_result)

            if should_close:
                conn.close()

            return {"status": "ok", "value": last_result, "all_results": results}

        except Exception as e:
            logger.exception("DuckDB execution failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if DuckDB surface is operational."""
        if not self.available:
            return False
        try:
            conn = duckdb.connect(":memory:")
            res = conn.execute("SELECT 1").fetchone()
            conn.close()
            return bool(res and res[0] == 1)
        except Exception:
            return False

    def extract_tags(self, source: str | None) -> list[str]:
        """Extract table names from DuckDB SQL source."""
        if not source:
            return []
        import re

        tables = re.findall(r"CREATE\s+TABLE\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE)
        tables.extend(re.findall(r"FROM\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE))
        tables.extend(re.findall(r"JOIN\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE))
        return list(dict.fromkeys(tables))
