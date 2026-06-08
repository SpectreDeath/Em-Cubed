import pytest
from em_cubed.surfaces.kanren_surface import KanrenSurface


@pytest.mark.asyncio
async def test_kanren_surface_availability():
    surface = KanrenSurface()
    assert surface.available is True
    assert await surface.health() is True


@pytest.mark.asyncio
async def test_kanren_basic_relation():
    surface = KanrenSurface()

    code = '''
from kanren import Relation, fact, run, Var

parent = Relation()
fact(parent, "john", "mary")
fact(parent, "mary", "ann")

q = Var()
result = run(0, q, parent("john", q))
'''
    result = await surface.execute(code, {})
    assert result["status"] == "ok"
    assert "mary" in result["value"]


def test_kanren_tag_extraction():
    code = """
def helper_ancestor(x, y):
    pass

relational_fact(parent)
relational_fact(child)
var q
var another
"""
    tags = KanrenSurface.extract_tags(code)
    assert "helper_ancestor" in tags
    assert "parent" in tags
    assert "child" in tags


def test_kanren_extract_tags_empty():
    assert KanrenSurface.extract_tags("") == []
    assert KanrenSurface.extract_tags(None) == []
