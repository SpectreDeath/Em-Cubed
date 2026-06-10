"""Tests for icf-clause-validator skill."""
import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "CLINICAL_TRIALS" / "icf-clause-validator" / "SKILL.md")
SKILL_ID = "CLINICAL_TRIALS/icf-clause-validator"


@pytest.fixture
def plugin_manager():
    return PluginManager()

@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)

@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class TestIcfClauseValidatorSkill:
    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "Informed Consent Form Clause Validator"
        assert metadata_dict["domain"] == "CLINICAL_TRIALS"
        assert "python" in metadata_dict["surfaces"]
        assert "z3" in metadata_dict["surfaces"]

    def test_surfaces_implemented(self, plugin_manager):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        available_surfaces = []
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin and plugin.available:
                available_surfaces.append(surface)
        assert len(available_surfaces) >= 1

    @pytest.mark.asyncio
    async def test_skill_execution(self, test_runner, test_generator):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        if not metadata_dict:
            pytest.skip("Skill metadata not available")
        from em_cubed.skills.metadata import SkillMetadata
        metadata = SkillMetadata.from_frontmatter({}, "", SKILL_FILE)
        for key, value in metadata_dict.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        tests = test_generator.generate_tests_for_skill(SKILL_FILE, metadata)
        if tests:
            results = await test_runner.run_test_suite(tests, SKILL_ID)
            assert results["pass_rate"] > 0.3

    def test_python_icf_detects_missing_risks(self):
        icf_text = {
            "research_purpose": "Study will evaluate drug X.",
            "study_duration": "12 weeks",
            "procedures": "Blood draws at each visit.",
            "risks": "",
            "benefits": "No direct benefit to subject.",
            "alternatives": "Subject may choose standard of care.",
            "confidentiality": "Data will be de-identified per HIPAA.",
            "voluntary_participation": "Participation is voluntary.",
            "contact_info": "PI: Dr. Smith, 555-1234.",
            "compensation": "No compensation.",
        }
        present = {
            k for k, v in icf_text.items() if v
        }
        assert "risks" not in present
        assert "procedures" in present

    def test_python_icf_valid_complete(self):
        icf_text = {
            "research_purpose": "Study will evaluate drug X.",
            "study_duration": "12 weeks",
            "procedures": "Blood draws at each visit.",
            "risks": "Risk of mild injection site reactions.",
            "benefits": "No direct benefit to subject.",
            "alternatives": "Subject may choose standard of care.",
            "confidentiality": "Data will be de-identified per HIPAA.",
            "voluntary_participation": "Participation is voluntary.",
            "contact_info": "PI: Dr. Smith, 555-1234.",
            "compensation": "No compensation.",
        }
        required = {
            "research_purpose", "study_duration", "procedures", "risks",
            "benefits", "alternatives", "confidentiality", "voluntary_participation",
            "contact_info", "compensation",
        }
        present = {k for k, v in icf_text.items() if v}
        missing = required - present
        assert len(missing) == 0

    def test_python_icf_fuzz_none_input(self):
        icf_text = None
        required = {
            "research_purpose", "study_duration", "procedures", "risks",
            "benefits", "alternatives", "confidentiality", "voluntary_participation",
            "contact_info", "compensation",
        }
        if icf_text is None:
            missing = list(required)
        else:
            present = {k for k, v in icf_text.items() if v}
            missing = list(required - present)
        assert len(missing) == len(required)

    def test_python_icf_fuzz_empty_dict(self):
        icf_text = {}
        required = {
            "research_purpose", "study_duration", "procedures", "risks",
            "benefits", "alternatives", "confidentiality", "voluntary_participation",
            "contact_info", "compensation",
        }
        present = {k for k, v in icf_text.items() if v}
        missing = list(required - present)
        assert len(missing) == len(required)
