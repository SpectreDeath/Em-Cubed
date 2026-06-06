"""Tests for bayesian-evidence-updater skill."""

import pytest
from pathlib import Path
from em_cubed.skills.testing import SkillTestGenerator, SkillTestRunner
from em_cubed.indexer import get_skill_metadata
from em_cubed.plugin_manager import PluginManager

SKILL_FILE = Path(Path(__file__).parent.parent.parent / "skills" / "ANALYTICS" / "bayesian-evidence-updater" / "SKILL.md")
SKILL_ID = "ANALYTICS/bayesian-evidence-updater"


@pytest.fixture
def plugin_manager():
    """Get plugin manager."""
    return PluginManager()


@pytest.fixture
def test_generator(plugin_manager):
    """Get test generator."""
    return SkillTestGenerator(plugin_manager)


@pytest.fixture
def test_runner(plugin_manager):
    """Get test runner."""
    return SkillTestRunner(plugin_manager, None)


class Testbayesian_evidence_updaterSkill:
    """Test suite for bayesian-evidence-updater."""

    def test_metadata_valid(self):
        """Test skill metadata is valid."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        assert metadata_dict is not None
        assert metadata_dict["name"] == "bayesian-evidence-updater"
        assert metadata_dict["domain"] == "ANALYTICS"
        assert len(metadata_dict["surfaces"]) >= 1

    def test_surfaces_implemented(self, plugin_manager):
        """Test at least one required surface is available."""
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        available_surfaces = []
        for surface in metadata_dict.get("surfaces", []):
            plugin = plugin_manager.get(surface)
            if plugin and plugin.available:
                available_surfaces.append(surface)
        assert len(available_surfaces) >= 1, f"No available surfaces found for {metadata_dict['name']}"

    @pytest.mark.asyncio
    async def test_skill_execution(self, test_runner, test_generator):
        """Test basic skill execution."""
        from em_cubed.skills.metadata import SkillMetadata
        metadata_dict = get_skill_metadata(SKILL_FILE, SKILL_FILE.parent.parent.parent)
        if not metadata_dict:
            pytest.skip("Skill metadata not available")
        
        metadata = SkillMetadata.from_frontmatter({}, "", SKILL_FILE)
        for key, value in metadata_dict.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)

        tests = test_generator.generate_tests_for_skill(SKILL_FILE, metadata)
        if tests:
            results = await test_runner.run_test_suite(tests, SKILL_ID)
            assert results["pass_rate"] > 0.3, f"Pass rate too low: {results['pass_rate']}"

    def test_python_posterior_calculation(self):
        """Test the Python posterior calculation logic."""
        matrix = [
            {"hypothesis_id": "H1_Accidental", "prior_probability": 0.20},
            {"hypothesis_id": "H2_Medical_Malpractice", "prior_probability": 0.20},
            {"hypothesis_id": "H3_Suicide", "prior_probability": 0.20},
            {"hypothesis_id": "H4_Family_Homicide", "prior_probability": 0.20},
            {"hypothesis_id": "H5_Outsider_Homicide", "prior_probability": 0.20},
        ]
        likelihoods = {
            "H1_Accidental": 0.1,
            "H2_Medical_Malpractice": 0.6,
            "H3_Suicide": 0.15,
            "H4_Family_Homicide": 0.3,
            "H5_Outsider_Homicide": 0.05,
        }

        result = calculate_posterior_update(matrix, likelihoods)
        
        assert result["status"] == "success"
        assert result["marginal_likelihood"] > 0
        
        total_prob = sum(d["posterior_probability"] for d in result["distribution"])
        assert abs(total_prob - 1.0) < 0.001, f"Distribution should sum to 1.0, got {total_prob}"

    def test_zero_evidence_error(self):
        """Test error handling for zero marginal probability."""
        matrix = [
            {"hypothesis_id": "H1_Accidental", "prior_probability": 0.20},
        ]
        likelihoods = {
            "H1_Accidental": 0.0,
        }

        result = calculate_posterior_update(matrix, likelihoods)
        
        assert result["status"] == "error"
        assert "Zero marginal" in result["message"]


def calculate_posterior_update(matrix, likelihood_dict):
    """Copy of the Python function for unit testing."""
    total_probability_evidence = 0.0
    unnormalized_posteriors = {}
    
    for row in matrix:
        h_id = row['hypothesis_id']
        prior = row['prior_probability']
        likelihood = likelihood_dict.get(h_id, 0.1)
        unnormalized_posterior = likelihood * prior
        unnormalized_posteriors[h_id] = unnormalized_posterior
        total_probability_evidence += unnormalized_posterior
        
    if total_probability_evidence == 0:
        return {'status': 'error', 'message': 'Zero marginal probability matrix'}
        
    updated_distribution = []
    for row in matrix:
        h_id = row['hypothesis_id']
        posterior = unnormalized_posteriors[h_id] / total_probability_evidence
        updated_distribution.append({
            'hypothesis_id': h_id,
            'posterior_probability': posterior
        })
        
    return {
        'status': 'success',
        'marginal_likelihood': total_probability_evidence,
        'distribution': updated_distribution
    }