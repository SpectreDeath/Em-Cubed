"""Tests for Polars surface integration."""

import pytest
from em_cubed.surfaces.polars_surface import PolarsSurface, _POLARS_AVAILABLE


@pytest.mark.asyncio
async def test_polars_surface_basic_execution():
    surface = PolarsSurface()
    if not surface.available:
        pytest.skip("Polars library not installed")

    code = """
import polars as pl
df = pl.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
result = df.select(pl.col("a").sum())
"""
    res = await surface.execute(code)
    assert res["status"] == "ok"
    assert res["value"] == [{"a": 6}]


@pytest.mark.asyncio
async def test_polars_surface_context_tables():
    surface = PolarsSurface()
    if not surface.available:
        pytest.skip("Polars library not installed")

    code = """
result = sales.filter(pl.col("amount") > 50)
"""
    context = {
        "tables": {
            "sales": [
                {"item": "A", "amount": 20},
                {"item": "B", "amount": 100},
                {"item": "C", "amount": 75},
            ]
        }
    }
    res = await surface.execute(code, context=context)
    assert res["status"] == "ok"
    assert len(res["value"]) == 2
    assert res["value"][0]["item"] == "B"


@pytest.mark.asyncio
async def test_polars_surface_health():
    surface = PolarsSurface()
    if not surface.available:
        assert await surface.health() is False
    else:
        assert await surface.health() is True
