"""Contract and regression tests for Em-Cubed skill catalog, discovery, and runtime invariants."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def _split_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---"), f"Missing YAML frontmatter start in {path}"
    _, fm_raw, body = text.split("---", 2)
    data = yaml.safe_load(fm_raw)
    assert isinstance(data, dict), f"Frontmatter did not parse to dict in {path}"
    return data, body


def test_all_skill_md_frontmatter_and_validator_clean(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every SKILL.md parses cleanly with PyYAML and passes SkillValidator with zero ERRORs."""
    from em_cubed.skills.metadata import SkillMetadata
    from em_cubed.skills.validator import SkillValidator, ValidationSeverity

    monkeypatch.chdir(REPO_ROOT)

    for root_rel in ("skills", ".agents/skills", "examples"):
        root = REPO_ROOT / root_rel
        if not root.exists():
            continue
        for md in sorted(root.rglob("SKILL.md")):
            fm, _ = _split_frontmatter(md)
            assert fm.get("name"), f"Missing name in {md}"

    validator = SkillValidator()
    skill_files = sorted((REPO_ROOT / "skills").rglob("SKILL.md"))
    assert len(skill_files) >= 170

    seen_names: dict[str, Path] = {}
    for md in skill_files:
        fm, body = _split_frontmatter(md)
        name = str(fm["name"])
        assert name not in seen_names, f"Duplicate skill name '{name}' in {md} and {seen_names[name]}"
        seen_names[name] = md

        meta = SkillMetadata.from_frontmatter(fm, body=body, file_path=md)
        result = validator.validate_skill_file(md, meta)
        errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
        assert not errors, f"SkillValidator errors in {md.relative_to(REPO_ROOT)}: {errors}"


def test_registry_json_matches_skills_directory() -> None:
    """registry.json has exact 1:1 parity with SKILL.md specs under skills/."""
    registry_path = REPO_ROOT / "registry.json"
    entries = json.loads(registry_path.read_text(encoding="utf-8"))
    assert isinstance(entries, list)

    reg_ids = [item["skill_id"] for item in entries]
    for item in entries:
        raw_path = item["path"]
        assert "\\" not in raw_path and not Path(raw_path).is_absolute(), (
            f"Non-portable path in registry.json: {raw_path}"
        )
    reg_paths = {(REPO_ROOT / item["path"]).resolve() for item in entries}
    disk_files = sorted((REPO_ROOT / "skills").rglob("SKILL.md"))
    disk_paths = {p.resolve() for p in disk_files}

    assert len(entries) == len(set(reg_ids)), "Duplicate skill_id entries in registry.json"
    assert reg_paths == disk_paths, (
        f"Mismatch registry vs disk: missing={sorted(str(p) for p in disk_paths - reg_paths)}, "
        f"stale={sorted(str(p) for p in reg_paths - disk_paths)}"
    )


def test_markdown_relative_links_and_license_exist() -> None:
    """No broken relative markdown links or machine-local file:// URIs in docs or skills."""
    assert (REPO_ROOT / "LICENSE").is_file()

    md_targets: list[Path] = [REPO_ROOT / "README.md"]
    for folder in ("docs", "skills", ".agents/skills"):
        root = REPO_ROOT / folder
        if root.exists():
            md_targets.extend(sorted(root.rglob("*.md")))

    broken: list[str] = []
    for md_path in md_targets:
        stripped = FENCE_RE.sub("", md_path.read_text(encoding="utf-8"))
        for match in MD_LINK_RE.finditer(stripped):
            raw_target = match.group(1).strip("<>")
            if raw_target.startswith("file:///"):
                broken.append(f"{md_path.relative_to(REPO_ROOT)} -> absolute file URI: {raw_target}")
                continue
            if raw_target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            rel_part = raw_target.split("#", 1)[0].split("?", 1)[0]
            if not rel_part:
                continue
            resolved = (md_path.parent / rel_part).resolve()
            if not resolved.exists():
                broken.append(f"{md_path.relative_to(REPO_ROOT)} -> missing target: {raw_target}")

    assert not broken, "Broken markdown links:\n" + "\n".join(broken)


def test_plugin_discovery_covers_all_exported_surfaces_and_dataclasses(tmp_path: Path) -> None:
    """PluginDiscovery wires all *Surface exports and registers sys.modules for dataclass plugins."""
    from em_cubed import surfaces
    from em_cubed.plugin_discovery import PluginDiscovery

    discovery = PluginDiscovery()
    eager, lazy = discovery.discover_builtin_surfaces()
    discovered = {**eager, **lazy}

    exported_surfaces = {
        getattr(surfaces, name)
        for name in surfaces.__all__
        if name.endswith("Surface")
    }
    assert surfaces.JanusSurface in exported_surfaces
    assert surfaces.WASMSurface in exported_surfaces
    assert exported_surfaces.issubset(set(discovered.values()))

    # Verify Python 3.13 @dataclass directory plugin loading works cleanly via sys.modules registration
    plugin_file = tmp_path / "dummy_dataclass_plugin.py"
    plugin_file.write_text(
        "from dataclasses import dataclass\n"
        "from em_cubed.plugin import SurfacePlugin\n\n"
        "@dataclass\n"
        "class DummyPlugin(SurfacePlugin):\n"
        "    name: str = 'dummy_dc'\n"
        "    available: bool = True\n"
        "    async def execute(self, code: str, context=None, timeout=None):\n"
        "        return {'status': 'success', 'value': code}\n"
        "    def health(self) -> bool:\n"
        "        return True\n"
        "    def extract_tags(self) -> list[str]:\n"
        "        return ['dummy']\n"
        "    def shutdown(self) -> None:\n"
        "        pass\n",
        encoding="utf-8",
    )
    loaded = discovery.discover_directory_plugins(tmp_path)
    assert "dummy_dc" in loaded
    sys.modules.pop("em_cubed_plugin_dummy_dataclass_plugin", None)


def test_skill_metadata_metrics_dict_hydration_and_auto_chainer(monkeypatch: pytest.MonkeyPatch) -> None:
    """SkillMetadata hydrates dict RuntimeMetrics and AutoChainer._get_registry instantiates SkillRegistry."""
    from em_cubed.skills.auto_chain import AutoChainer
    from em_cubed.skills.metadata import SkillMetadata
    from em_cubed.skills.registry import SkillRegistry

    monkeypatch.chdir(REPO_ROOT)

    meta = SkillMetadata(
        name="metrics-check",
        domain="GENERAL",
        version="1.0.0",
        surfaces=["python"],
        purpose="Verify dict metrics population",
        description="Checks runtime metrics dictionary hydration.",
        dependencies=[],
        metrics={  # type: ignore[arg-type]
            "applied_count": 4,
            "success_count": 3,
            "token_savings_avg": 12.5,
        },
    )
    assert meta.metrics.applied_count == 4
    assert meta.metrics.success_count == 3
    assert meta.metrics.total_token_usage == pytest.approx(50.0)

    default_registry = SkillRegistry()
    assert default_registry.skills_dir == Path("skills")

    chainer = AutoChainer(registry_path=str(REPO_ROOT / "registry.json"))
    reg = chainer._get_registry()
    assert isinstance(reg, SkillRegistry)
    assert reg.registry_file == REPO_ROOT / "registry.json"


def test_container_executor_main_runs_with_mocked_executor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """container_executor.main initializes SkillRegistry without TypeError and outputs valid JSON."""
    from em_cubed import container_executor

    code_file = tmp_path / "code.py"
    code_file.write_text("result = 42\n", encoding="utf-8")
    ctx_file = tmp_path / "context.json"
    ctx_file.write_text(
        json.dumps(
            {
                "surface": "python",
                "skills_dir": str(REPO_ROOT / "skills"),
                "registry_file": str(REPO_ROOT / "registry.json"),
                "skill_input": {"x": 1},
            }
        ),
        encoding="utf-8",
    )

    mock_result = SimpleNamespace(
        success=True,
        output={"answer": 42},
        error=None,
        execution_time_ms=1.5,
        surface_used="python",
    )
    mock_executor = MagicMock()
    mock_executor.execute = AsyncMock(return_value=mock_result)

    monkeypatch.setattr(sys, "argv", ["em_cubed.container_executor", str(code_file), str(ctx_file), "5.0"])
    with patch.object(container_executor, "SkillExecutor", return_value=mock_executor) as exec_cls:
        container_executor.main()

    assert exec_cls.called
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert payload["status"] == "ok"
    assert payload["value"] == {"answer": 42}


@pytest.mark.asyncio
async def test_core_untested_modules_contracts() -> None:
    """Verify PluginRegistry, SHACLValidator, LandlockSandbox, RustSurface, and ArrowSharedSubstrate."""
    from em_cubed.ontology.shacl_validator import SHACLValidator
    from em_cubed.plugin_registry import PluginRegistry
    from em_cubed.security.landlock_sandbox import LandlockSandbox
    from em_cubed.surfaces.rust_surface import RustSurface
    from em_cubed.surfaces.shared_substrate_arrow import ArrowSharedSubstrate

    # PluginRegistry lifecycle
    registry = PluginRegistry()
    plugin = MagicMock()
    registry.register("mock_plugin", plugin)
    assert registry.get("mock_plugin") is plugin
    assert registry.initialize_plugin("mock_plugin") is True
    assert registry.shutdown_plugin("mock_plugin") is True
    assert registry.unregister("mock_plugin") is True
    assert registry.get("mock_plugin") is None

    # SHACLValidator valid vs violation graphs
    validator = SHACLValidator()
    bad_report = validator.validate([{"subject": "S1", "predicate": "rdf:type", "object": "bfo:Process"}])
    assert not bad_report.conforms
    assert bad_report.violation_count == 1
    good_report = validator.validate(
        [
            {"subject": "S1", "predicate": "rdf:type", "object": "bfo:Process"},
            {"subject": "S1", "predicate": "bfo:has_participant", "object": "Agent1"},
        ]
    )
    assert good_report.conforms
    assert good_report.violation_count == 0

    # LandlockSandbox safe initialization
    sandbox = LandlockSandbox(allowed_paths=["/tmp"])
    assert isinstance(sandbox.is_supported, bool)
    if not sandbox.is_supported:
        assert sandbox.apply_sandbox() is False

    # RustSurface ctypes evaluation
    rust_surface = RustSurface()
    res = await rust_surface.execute("import ctypes\nresult = ctypes.sizeof(ctypes.c_int)")
    assert res["status"] == "success"
    assert res["value"] >= 4

    # ArrowSharedSubstrate IPC roundtrip
    substrate = ArrowSharedSubstrate()
    assert substrate.register_table("nums", {"a": [1, 2], "b": [3, 4]}) is True
    payload = substrate.serialize_ipc("nums")
    assert payload is not None
    assert substrate.deserialize_ipc("nums_copy", payload) is True
    assert substrate.to_pydict("nums_copy") == {"a": [1, 2], "b": [3, 4]}
    substrate.clear()
    assert substrate.get_table("nums") is None
