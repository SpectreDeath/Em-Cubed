"""SQLite surface integration for declarative data querying."""

import sqlite3
import json
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
        logger.info("SQLiteSurface initialized")

    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute SQL code and return results."""
        return await self.execute_with_timeout(code, context)

    async def _execute_impl(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute SQL code on a per-execution in-memory database."""
        logger.info("Executing SQL code", code_length=len(code))

        try:
            # Create a new in-memory database for this execution
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # If substrate is provided, we can pre-load data from it
            # For now, we just execute the code
            
            # Split code into statements
            statements = [s.strip() for s in code.split(";") if s.strip()]
            
            results = []
            last_result = None
            
            for stmt in statements:
                cursor.execute(stmt)
                if cursor.description:
                    # It was a SELECT query
                    rows = cursor.fetchall()
                    last_result = [dict(row) for row in rows]
                    results.append(last_result)
                else:
                    # It was a DDL/DML statement
                    conn.commit()
                    last_result = {"rows_affected": cursor.rowcount}
                    results.append(last_result)

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
        # Basic regex to find table names in CREATE TABLE or FROM/JOIN
        tables = re.findall(r"CREATE\s+TABLE\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE)
        tables.extend(re.findall(r"FROM\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE))
        tables.extend(re.findall(r"JOIN\s+([a-zA-Z0-9_]+)", source, re.IGNORECASE))
        return list(dict.fromkeys(tables))
