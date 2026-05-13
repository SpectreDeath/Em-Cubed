import pytest
from pathlib import Path
from em_cubed.indexer import get_skill_metadata
from em_cubed.surfaces.cangjie_surface import CangjieSurface

def test_cangjie_skill_indexing():
    """Verify that a skill with Cangjie is correctly indexed."""
    skill_path = Path("skills/logic/CANGJIE_ORCHESTRATION.md")
    skills_dir = Path("skills")
    
    metadata = get_skill_metadata(skill_path, skills_dir)
    
    assert metadata is not None
    assert "cangjie" in metadata["surfaces"]
    assert "python" in metadata["surfaces"]
    assert "prolog" in metadata["surfaces"]
    
    # Verify tags extracted from CJ block
    assert "main" in metadata["tags"]

@pytest.mark.asyncio
async def test_cangjie_surface_integration():
    """Verify CangjieSurface can be instantiated and used in the framework."""
    from em_cubed.plugin_manager import PluginManager
    
    pm = PluginManager()
    # Mock cjc availability for the test
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("shutil.which", lambda x: "/usr/bin/cjc" if x == "cjc" else None)
        
        surface = pm.get("cangjie")
        assert surface is not None
        assert isinstance(surface, CangjieSurface)
        assert surface.name == "cangjie"
