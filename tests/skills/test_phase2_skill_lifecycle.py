"""Unit tests for Phase 2: Skill Compiler, Skill Hub, Lockfile, and Signatures."""

import tempfile
from pathlib import Path

import pytest

from em_cubed.skills.hub import SkillHub
from em_cubed.skills.skill_compiler import SkillCompiler


def test_skill_compiler_generate():
    compiler = SkillCompiler()
    res = compiler.compile_skill(
        prompt="Perform matrix multiplication and numerical optimization",
        name="matrix-optimizer",
        domain="OPTIMIZATION",
        surfaces=["python", "z3", "sqlite"],
    )

    assert res["name"] == "matrix-optimizer"
    assert res["domain"] == "OPTIMIZATION"
    assert "Python Surface" in res["skill_md"]
    assert "Z3 Surface" in res["skill_md"]
    assert "Sqlite Surface" in res["skill_md"]


def test_skill_compiler_z3_verification():
    compiler = SkillCompiler()
    try:
        import z3  # noqa: F401
        has_z3 = True
    except ImportError:
        has_z3 = False

    if not has_z3:
        pytest.skip("z3-solver is not installed")

    # Test valid entailment: x > 10 => x > 0
    res = compiler.verify_pre_post_conditions("x > 10", "x > 0")
    assert res["valid"] is True

    # Test invalid entailment: x > 0 => x > 10 (fails when x=1)
    res_inv = compiler.verify_pre_post_conditions("x > 0", "x > 10")
    assert res_inv["valid"] is False



def test_skill_hub_lock_and_verify():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        lockfile = tmp_path / "em3.lock"

        # Create a sample skill file
        skill_file = skills_dir / "Test" / "sample.md"
        skill_file.parent.mkdir()
        skill_file.write_text("# Test Skill\nContent", encoding="utf-8")

        hub = SkillHub(skills_dir=skills_dir, lockfile_path=lockfile)

        # 1. Generate lockfile
        payload = hub.generate_lockfile()
        assert payload["skill_count"] == 1
        assert lockfile.exists()

        # 2. Verify integrity
        rel_path = "Test/sample.md"
        verify_res = hub.verify_skill_integrity(rel_path)
        assert verify_res["valid"] is True

        # 3. Modify skill file and check verification failure
        skill_file.write_text("# Modified Skill Content", encoding="utf-8")
        verify_fail = hub.verify_skill_integrity(rel_path)
        assert verify_fail["valid"] is False


def test_skill_hub_install_local():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        skills_dir = tmp_path / "skills"
        lockfile = tmp_path / "em3.lock"

        src_file = tmp_path / "external_skill.md"
        src_file.write_text("# External Skill\nBody", encoding="utf-8")

        hub = SkillHub(skills_dir=skills_dir, lockfile_path=lockfile)
        res = hub.install_skill(str(src_file), "my_ext.md")

        assert res["status"] == "ok"
        assert Path(res["path"]).exists()
        assert lockfile.exists()
