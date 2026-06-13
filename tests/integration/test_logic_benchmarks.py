"""Benchmark Kanren Logic Surface with StatLib-style numeric data."""

import time

import pytest

from em_cubed.surfaces import KanrenSurface


STATLIB_STYLE_DATASET = {
    "observations": [
        {"id": 1, "x": 1.2, "y": 2.3, "class": "A"},
        {"id": 2, "x": 1.8, "y": 2.1, "class": "A"},
        {"id": 3, "x": 5.4, "y": 1.1, "class": "B"},
        {"id": 4, "x": 4.9, "y": 0.8, "class": "B"},
        {"id": 5, "x": 2.5, "y": 3.0, "class": "A"},
    ],
}


@pytest.fixture
def kanren_surface():
    surface = KanrenSurface()
    if not surface.available:
        pytest.skip("kanren package is not installed")
    return surface


@pytest.mark.asyncio
async def test_kanren_statlib_numeric_benchmark(kanren_surface):
    """Benchmark Kanren reasoning over StatLib-style numeric observations."""
    code = """
from kanren import var, Relation, fact, run, eq

x = var('x')
y = var('y')
cls = var('cls')

point = Relation('point')

for row in context.get('observations', []):
    fact(point, row['x'], row['y'], row['class'])

q = (point(x, y, cls),)
res = run(0, (x, y, cls), q)

result = {
    'queries': len(context.get('observations', [])),
    'available': True,
    'results': len(res),
}
"""
    start = time.time()
    response = await kanren_surface.execute(
        code,
        {"observations": STATLIB_STYLE_DATASET["observations"]},
    )
    elapsed = time.time() - start
    assert response.get("status") == "ok"
    assert elapsed < 5.0, f"Kanren benchmark took too long: {elapsed:.2f}s"
    value = response.get("value") or {}
    assert value.get("available") is True
    assert value.get("results") == len(STATLIB_STYLE_DATASET["observations"])
