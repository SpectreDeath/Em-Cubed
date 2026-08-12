"""Polars surface integration for high-performance sub-millisecond DataFrame transformations."""

from typing import Any

import structlog

from .base import SurfaceBase

logger = structlog.get_logger()

try:
    import polars as pl
    _POLARS_AVAILABLE = True
except ImportError:
    pl = None  # type: ignore[assignment]
    _POLARS_AVAILABLE = False


class PolarsSurface(SurfaceBase):
    """Handle high-performance, in-memory Polars DataFrame transformations."""

    @property
    def name(self) -> str:
        return "polars"

    @property
    def description(self) -> str:
        return "High-performance Polars DataFrame surface"

    @property
    def available(self) -> bool:
        return _POLARS_AVAILABLE

    def __init__(self, timeout: float | None = None):
        super().__init__(timeout)
        logger.info("PolarsSurface initialized", available=self.available)

    async def _execute_impl(self, code: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute Polars Python code or expression with contextual data.

        The code can define a `result` variable or return a DataFrame / Series / dict.
        Contextual tables provided in `context['tables']` are exposed as Polars DataFrames `df` or dict keys.
        """
        if not self.available:
            return {
                "status": "error",
                "message": "Polars is not available. Install with `pip install polars`.",
            }

        logger.info("Executing Polars code", code_length=len(code))

        try:
            loc: dict[str, Any] = {"pl": pl}
            ctx_tables = (context or {}).get("tables", {})
            for tbl_name, tbl_data in ctx_tables.items():
                if isinstance(tbl_data, pl.DataFrame):
                    loc[tbl_name] = tbl_data
                elif isinstance(tbl_data, (list, dict)):
                    loc[tbl_name] = pl.DataFrame(tbl_data)

            if context and "df" in context and "df" not in loc:
                ctx_df = context["df"]
                if isinstance(ctx_df, pl.DataFrame):
                    loc["df"] = ctx_df
                else:
                    loc["df"] = pl.DataFrame(ctx_df)

            # Execute code within restricted globals namespace
            exec_globals = {"pl": pl, "__builtins__": __builtins__}
            exec(code, exec_globals, loc)  # noqa: S102


            raw_val = loc.get("result")
            if raw_val is None:
                # Fallback to checking any newly modified/created DataFrame in locals
                for k, v in loc.items():
                    if k not in ("pl", "df") and isinstance(v, (pl.DataFrame, pl.Series)):
                        raw_val = v
                        break

            if isinstance(raw_val, pl.DataFrame):
                res_val: Any = raw_val.to_dicts()
            elif isinstance(raw_val, pl.Series):
                res_val = raw_val.to_list()
            else:
                res_val = raw_val

            return {"status": "ok", "value": res_val}

        except Exception as e:
            logger.exception("Polars execution failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def health(self) -> bool:
        """Check if Polars surface is operational."""
        if not self.available:
            return False
        try:
            df = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
            res = df.select(pl.col("a").sum()).item()
            return res == 3
        except Exception:
            return False

    def extract_tags(self, source: str | None) -> list[str]:
        """Extract Polars column or expression tags from source code."""
        if not source:
            return []
        import re
        cols = re.findall(r'pl\.col\(["\']([a-zA-Z0-9_]+)["\']\)', source)
        return list(dict.fromkeys(cols))
