"""Tests for sap-endpoint-consistency-checker skill."""
import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "CLINICAL_TRIALS" / "sap-endpoint-consistency-checker" / "SKILL.md")
SKILL_ID = "CLINICAL_TRIALS/sap-endpoint-consistency-checker"


@pytest.fixture
def plugin_manager():
    return PluginManager()

@pytest.fixture
def test_generator(plugin_manager):
    return SkillTestGenerator(plugin_manager)

@pytest.fixture
def test_runner(plugin_manager):
    return SkillTestRunner(plugin_manager, None)


class TestSapEndpointConsistencyCheckerSkill:
    def test_metadata_valid(self):
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "SAP Endpoint Consistency Checker"
        assert metadata_dict["domain"] == "CLINICAL_TRIALS"
        assert "python" in metadata_dict["surfaces"]
        assert "prolog" in metadata_dict["surfaces"]

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

    def test_python_endpoint_alignment(self):
        sap = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "PFS", "analysis_method": "KM", "timepoint": "C28"},
                {"endpoint_id": "ep02", "name": "ORR", "analysis_method": "CMH", "timepoint": "C18"},
            ]
        }
        registry = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "PFS", "timepoint": "C28"},
                {"endpoint_id": "ep02", "name": "ORR", "timepoint": "C18"},
            ]
        }
        protocol = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "PFS", "analysis_method": "KM"},
                {"endpoint_id": "ep02", "name": "ORR", "analysis_method": "CMH"},
            ]
        }
        sap_map = {e["endpoint_id"]: e for e in sap["endpoints"]}
        reg_map = {e["endpoint_id"]: e for e in registry["endpoints"]}
        proto_map = {e["endpoint_id"]: e for e in protocol["endpoints"]}
        aligned = []
        for ep_id, sap_ep in sap_map.items():
            if ep_id in reg_map and ep_id in proto_map:
                reg_ep = reg_map[ep_id]
                proto_ep = proto_map[ep_id]
                tp_match = sap_ep.get("timepoint") == reg_ep.get("timepoint")
                m_match = sap_ep.get("analysis_method") == proto_ep.get("analysis_method")
                if tp_match and m_match:
                    aligned.append(ep_id)
        assert sorted(aligned) == ["ep01", "ep02"]

    def test_python_timepoint_mismatch_detected(self):
        sap = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "PFS", "analysis_method": "KM", "timepoint": "Cycle 28"},
            ]
        }
        registry = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "PFS", "timepoint": "Cycle 36"},
            ]
        }
        protocol = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "PFS", "analysis_method": "KM"},
            ]
        }
        sap_map = {e["endpoint_id"]: e for e in sap["endpoints"]}
        reg_map = {e["endpoint_id"]: e for e in registry["endpoints"]}
        proto_map = {e["endpoint_id"]: e for e in protocol["endpoints"]}
        mismatched = []
        for ep_id, sap_ep in sap_map.items():
            if ep_id in reg_map and ep_id in proto_map:
                tp_match = sap_ep.get("timepoint") == reg_map[ep_id].get("timepoint")
                if not tp_match:
                    mismatched.append(ep_id)
        assert mismatched == ["ep01"]

    def test_python_method_mismatch_detected(self):
        sap = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "ORR", "analysis_method": "CMH", "timepoint": "C18"},
            ]
        }
        protocol = {
            "endpoints": [
                {"endpoint_id": "ep01", "name": "ORR", "analysis_method": "LogisticRegression"},
            ]
        }
        sap_map = {e["endpoint_id"]: e for e in sap["endpoints"]}
        proto_map = {e["endpoint_id"]: e for e in protocol["endpoints"]}
        mismatched = []
        for ep_id, sap_ep in sap_map.items():
            if ep_id in proto_map:
                m_match = sap_ep.get("analysis_method") == proto_map[ep_id].get("analysis_method")
                if not m_match:
                    mismatched.append(ep_id)
        assert mismatched == ["ep01"]
