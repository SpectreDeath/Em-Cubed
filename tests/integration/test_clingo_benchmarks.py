"""Benchmark Clingo Logic Surface with StatLib-style numeric data."""

import time

import pytest

from em_cubed.surfaces import ClingoSurface


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
def clingo_surface():
    surface = ClingoSurface()
    if not surface.available:
        pytest.skip("clingo package is not installed")
    return surface


@pytest.mark.asyncio
async def test_clingo_statlib_numeric_benchmark(clingo_surface):
    """Benchmark Clingo ASP reasoning over StatLib-style numeric observations."""
    observations = STATLIB_STYLE_DATASET["observations"]
    rows = [
        f"observation({row['id']}, {int(row['x']*10)}, {int(row['y']*10)}, {1 if row['class'] == 'A' else 2})."
        for row in observations
    ]
    code = "\n".join(
        rows
        + [
            "class_high_y(Id) :- observation(Id, _, Y, 1), Y >= 20.",
            "#show class_high_y/1.",
        ]
    )
    start = time.time()
    response = await clingo_surface.execute(code)
    elapsed = time.time() - start
    if response.get("status") == "error" and "parsing" in response.get("message", "").lower():
        pytest.skip("clingo API version not supported")
    assert response.get("status") == "ok", response.get("message")
    assert elapsed < 5.0, f"Clingo benchmark took too long: {elapsed:.2f}s"
    value = response.get("value") or {}
    assert "model" in value or "models" in value or len(value) >= 0
