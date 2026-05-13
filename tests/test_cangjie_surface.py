import pytest
from unittest.mock import patch, MagicMock
import asyncio
from em_cubed.surfaces.cangjie_surface import CangjieSurface

@pytest.mark.asyncio
async def test_cangjie_surface_availability():
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/cjc"
        surface = CangjieSurface()
        assert surface.available is True
        assert await surface.health() is True

@pytest.mark.asyncio
async def test_cangjie_surface_compilation_failure():
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/cjc"
        surface = CangjieSurface()
        
        # Mock subprocess to fail during compilation
        from unittest.mock import AsyncMock
        mock_proc = MagicMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b"Syntax error at line 1"))
        mock_proc.returncode = 1
        
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await surface.execute("invalid code")
            assert result["status"] == "error"
            assert "Compilation failed" in result["message"]

@pytest.mark.asyncio
async def test_cangjie_surface_success():
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/bin/cjc"
        surface = CangjieSurface()
        
        # Mock compilation (success)
        from unittest.mock import AsyncMock
        mock_compile = MagicMock()
        mock_compile.communicate = AsyncMock(return_value=(b"", b""))
        mock_compile.returncode = 0
        
        # Mock execution (success)
        mock_exec = MagicMock()
        mock_exec.communicate = AsyncMock(return_value=(b"Hello from CJ", b""))
        mock_exec.returncode = 0
        
        with patch("asyncio.create_subprocess_exec") as mock_exec_call:
            mock_exec_call.side_effect = [mock_compile, mock_exec]
            result = await surface.execute('print("Hello from CJ")')
            assert result["status"] == "ok"
            assert result["value"] == "Hello from CJ"

def test_cangjie_tag_extraction():
    code = """
    func calculate_logic(x: Int64) {
        return x * 2
    }
    
    effect RegistrySearch {
        fn search(q: String): String
    }
    """
    tags = CangjieSurface.extract_tags(code)
    assert "calculate_logic" in tags
    assert "RegistrySearch" in tags
