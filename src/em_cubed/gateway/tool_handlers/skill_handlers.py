"""Skill tool handlers: search_skills, list_surfaces, execute_skill, auto_chain."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from em_cubed.gateway.tool_registry import ToolRegistry


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


def _handle_search_skills(args: dict[str, Any]) -> dict[str, Any]:
    from pathlib import Path

    from em_cubed.search import search_registry

    query = args.get("query", "")
    max_res = args.get("max_results", 10)
    reg_path = Path("registry.json")
    if not reg_path.exists():
        reg_path = Path("src/em_cubed/registry.json")
    if reg_path.exists():
        matches = search_registry(query, registry_path=reg_path, max_results=max_res, use_whoosh=False)
    else:
        from em_cubed.skills import SkillRegistry

        r = SkillRegistry(Path("skills"), reg_path)
        matches = [s.to_dict() for s in r.search(query)[:max_res]] if hasattr(r, "search") else []  # type: ignore[attr-defined]
    return {
        "query": query,
        "count": len(matches),
        "skills": [
            {
                "skill_id": m.get("skill_id", m.get("name", "")),
                "name": m.get("name", ""),
                "domain": m.get("domain", ""),
                "surfaces": m.get("surfaces", []),
                "description": m.get("description", ""),
            }
            for m in matches
        ],
    }


def _handle_list_surfaces(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.surfaces import (
        ClingoSurface,
        DatalogSurface,
        HySurface,
        JanusSurface,
        KanrenSurface,
        PrologSurface,
        PythonSurface,
        QuickJSSurface,
        SQLiteSurface,
        WASMSurface,
        Z3Surface,
    )

    raw_classes = [
        PythonSurface,
        PrologSurface,
        Z3Surface,
        DatalogSurface,
        SQLiteSurface,
        HySurface,
        QuickJSSurface,
        WASMSurface,
        ClingoSurface,
        KanrenSurface,
        JanusSurface,
    ]
    surfaces = [cls() for cls in raw_classes if cls is not None]
    return {
        "surfaces": [
            {
                "name": s.name,
                "description": s.description,
                "available": s.available,
            }
            for s in surfaces
        ]
    }


def _handle_execute_skill(args: dict[str, Any]) -> dict[str, Any]:
    import asyncio
    from pathlib import Path as _Path

    from em_cubed.plugin_registry import PluginRegistry
    from em_cubed.skills import SkillRegistry
    from em_cubed.skills.executor import SkillExecutionRequest, SkillExecutor, get_skill_executor

    skills_dir = _Path("skills")
    reg_file = _Path("registry.json")
    reg = SkillRegistry(skills_dir, reg_file)
    pm = PluginRegistry()
    executor = get_skill_executor() or SkillExecutor(pm, reg, skills_dir)

    skill_id = args.get("skill_id", "")
    surface = args.get("surface")
    input_data = args.get("input_data", {})
    req = SkillExecutionRequest(skill_id=skill_id, input_data=input_data, surface=surface)
    res = asyncio.run(executor.execute(req))
    return {
        "status": "ok" if res.success else "error",
        "value": res.output if res.success else res.error,
        "execution_time": res.execution_time_ms,
    }


def _handle_auto_chain(args: dict[str, Any]) -> dict[str, Any]:
    from em_cubed.skills.auto_chain import AutoChainer

    chainer = AutoChainer()
    goal = args.get("goal", "")
    inputs = args.get("inputs", {})
    return chainer.find_chain(input_schema=inputs, goal_description=goal)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_all(registry: "ToolRegistry") -> None:
    """Register all skill tool handlers with *registry*."""
    registry.register("em_cubed_search_skills", _handle_search_skills)
    registry.register("em_cubed_list_surfaces", _handle_list_surfaces)
    registry.register("em_cubed_execute_skill", _handle_execute_skill)
    registry.register("em_cubed_auto_chain", _handle_auto_chain)
