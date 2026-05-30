"""Tests for WASM surface functionality."""

import pytest
from em_cubed.surfaces.wasm_surface import WASMSurface


def test_wasm_surface_creation():
    """Test that WASM surface can be created."""
    surface = WASMSurface()
    assert surface.name == "wasm"
    assert surface.description == "WebAssembly execution with sandboxed runtime"


def test_wasm_surface_available():
    """Test that WASM surface reports availability."""
    surface = WASMSurface()
    assert hasattr(surface, '_wasm_available')


def test_wasm_surface_extract_tags():
    """Test extracting tags from WASM source."""
    surface = WASMSurface()
    
    # Test with empty source
    tags = surface.extract_tags(None)
    assert tags == []
    
    tags = surface.extract_tags("")
    assert tags == []
    
    # Test with simple function in WAT format
    wasm_code = "(module (func $add (param i32 i32) (result i32)) (export \"add\" (func $add)))"
    tags = surface.extract_tags(wasm_code)
    assert isinstance(tags, list)
    if surface.available:
        assert "add" in tags


@pytest.mark.asyncio
async def test_wasm_surface_execution():
    """Test actual execution of a WebAssembly module in WAT format."""
    surface = WASMSurface()
    if not surface.available:
        pytest.skip("WASM runtime not available")

    # Simple WAT module exporting 'add'
    wat_code = """
    (module
      (func $add (param $lhs i32) (param $rhs i32) (result i32)
        local.get $lhs
        local.get $rhs
        i32.add)
      (export "add" (func $add))
    )
    """
    
    # Run the module
    context = {
        "skill_input": {
            "a": 15,
            "b": 27
        }
    }
    result = await surface.execute(wat_code, context)
    assert result["status"] == "ok"
    assert result["value"] == 42


if __name__ == "__main__":
    pytest.main(["-v", __file__])