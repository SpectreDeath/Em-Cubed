"""Unit tests for Phase 1 surfaces: DuckDB, Julia, Tensor, and Arrow Shared Substrate."""

import pytest

from em_cubed.surfaces import (
    ArrowSharedSubstrate,
    DuckDBSurface,
    JuliaSurface,
    TensorSurface,
)


@pytest.mark.asyncio
async def test_duckdb_surface_execution():
    surface = DuckDBSurface()
    if not surface.available:
        pytest.skip("DuckDB is not installed in the environment")

    # Test basic SQL execution
    code = "CREATE TABLE test_tbl (id INT, val VARCHAR); INSERT INTO test_tbl VALUES (1, 'hello'); SELECT * FROM test_tbl;"
    res = await surface.execute(code)
    assert res["status"] == "ok"
    assert len(res["value"]) == 1
    assert res["value"][0]["id"] == 1
    assert res["value"][0]["val"] == "hello"


@pytest.mark.asyncio
async def test_duckdb_surface_health():
    surface = DuckDBSurface()
    if not surface.available:
        pytest.skip("DuckDB is not installed in the environment")

    health = await surface.health()
    assert health is True


@pytest.mark.asyncio
async def test_julia_surface_available():
    surface = JuliaSurface()
    assert hasattr(surface, "available")
    assert hasattr(surface, "name")
    assert surface.name == "julia"


@pytest.mark.asyncio
async def test_tensor_surface_execution():
    surface = TensorSurface()
    if not surface.available:
        pytest.skip("PyTorch is not installed in the environment")

    code = "a = torch.tensor([1.0, 2.0]); b = torch.tensor([3.0, 4.0]); result = a + b"
    res = await surface.execute(code)
    assert res["status"] == "ok"
    assert res["value"] == [4.0, 6.0]


@pytest.mark.asyncio
async def test_tensor_surface_health():
    surface = TensorSurface()
    if not surface.available:
        pytest.skip("PyTorch is not installed in the environment")

    health = await surface.health()
    assert health is True


def test_arrow_shared_substrate_dict_fallback():
    substrate = ArrowSharedSubstrate()
    data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}

    ok = substrate.register_table("dataset1", data)
    assert ok is True

    retrieved = substrate.to_pydict("dataset1")
    assert retrieved is not None
    assert "col1" in retrieved
    assert retrieved["col1"] == [1, 2, 3]


def test_arrow_shared_substrate_serialization():
    substrate = ArrowSharedSubstrate()
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    ok = substrate.register_table("users", data)
    assert ok is True

    serialized = substrate.serialize_ipc("users")
    assert serialized is not None

    # Test deserialization
    ok_deser = substrate.deserialize_ipc("users_copy", serialized)
    assert ok_deser is True

    pydict = substrate.to_pydict("users_copy")
    assert pydict is not None
