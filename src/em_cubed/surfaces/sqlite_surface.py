"""SQLite surface integration for declarative data querying."""

import sqlite3
from typing import Dict, Any, Optional, List
import structlog

from .base import SurfaceBase

logger = structlog.get_logger()


class SQLiteSurface(SurfaceBase):
    """Handle SQL execution on an in-memory SQLite database."""

    @property
    def name(self) -> str:
        return "sqlite"

    @property
    def description(self) -> str:
        return "In-memory SQLite execution"

    @property
    def available(self) -> bool:
        return True  # sqlite3 is part of Python stdlib

    def __init__(self, timeout: Optional[float] = None):
        super().__init__(timeout)
        self._sessions: Dict[str, sqlite3.Connection] = {}
        logger.info("SQLiteSurface initialized")

    def _get_connection(self, context: Optional[Dict[str, Any]] = None):
        """Get or create a database connection based on session_id in context."""
        session_id = (context or {}).get("session_id")
        if session_id:
            if session_id not in self._sessions:
                conn = sqlite3.connect(":memory:")
                conn.row_factory = sqlite3.Row
                self._sessions[session_id] = conn
            return self._sessions[session_id], False  # don't close after use
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        return conn, True  # close after use

    def close_session(self, session_id: str) -> None:
        """Explicitly close a session's connection and remove it."""
        if session_id in self._sessions:
            try:
                self._sessions[session_id].close()
            except Exception:
                pass
            del self._sessions[session_id]

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute SQL code and return results."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute SQL code on an in-memory database, with optional session persistence."""
        logger.info("Executing SQL code", code_length=len(code))

        try:
            conn, should_close = self._get_connection(context)
            cursor = conn.cursor()

            # Split code into statements
            statements = [s.strip() for s in code.split(";") if s.strip()]

            results: list = []
            last_result: object = None

            for stmt in statements:
                cursor.execute(stmt)
                if cursor.description:
                    rows = cursor.fetchall()
                    last_result = [dict(row) for row in rows]
                    results.append(last_result)
                else:
                    conn.commit()
                    last_result = {"rows_affected": cursor.rowcount}
                    results.append(last_result)

            if should_close:
                conn.close()
            logger.info("SQL execution successful")
            return {
                "status": "ok",
                "value": last_result,
                "all_results": results
            }

        except Exception as e:
            logger.exception("SQL execution failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if the surface is available."""
        return True

    def extract_tags(self, source: Optional[str]) -> List[str]:
        """Extract table names from SQL source."""
        if not source:
            return []
        import re
        tables = re.findall(r"CREATE\s+TABLE\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE)
        tables.extend(re.findall(r"FROM\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE))
        tables.extend(re.findall(r"JOIN\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE))
        return list(dict.fromkeys(tables))
