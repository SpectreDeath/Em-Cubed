import pytest
import json
from em_cubed.search import search_registry


# Disable whoosh for tests to ensure consistent behavior
def search_registry_test(query, registry_path, max_results=10):
    return search_registry(query, registry_path, max_results, use_whoosh=False)


class TestSearchRegistry:
    @pytest.fixture
    def sample_registry(self, tmp_path):
        """Create a sample registry file for testing."""
        registry_data = [
            {
                "name": "Math Calculator",
                "domain": "Mathematics",
                "purpose": "Perform basic arithmetic operations",
                "description": "Simple calculator for addition, subtraction, multiplication, division",
                "surfaces": ["python"],
                "logic_tags": [],
                "heuristic_tags": ["add", "subtract", "multiply", "divide"],
                "score": 0,
            },
            {
                "name": "Logic Solver",
                "domain": "Logic",
                "purpose": "Solve logical puzzles and problems",
                "description": "Advanced logical reasoning and puzzle solving",
                "surfaces": ["prolog"],
                "logic_tags": ["solve", "puzzle"],
                "heuristic_tags": [],
                "score": 0,
            },
            {
                "name": "Data Processor",
                "domain": "Data",
                "purpose": "Process and transform data",
                "description": "General purpose data processing and transformation",
                "surfaces": ["python", "hy"],
                "logic_tags": [],
                "heuristic_tags": ["process", "transform"],
                "score": 0,
            },
        ]

        registry_file = tmp_path / "registry.json"
        with open(registry_file, "w") as f:
            json.dump(registry_data, f)

        return registry_file

    def test_search_basic_match(self, sample_registry):
        """Test basic search matching."""
        results = search_registry_test("calculator", sample_registry)
        assert len(results) == 1
        assert results[0]["name"] == "Math Calculator"
        assert results[0]["score"] > 0

    def test_search_no_matches(self, sample_registry):
        """Test search with no matches."""
        results = search_registry_test("nonexistent", sample_registry)
        assert len(results) == 0

    def test_search_multiple_results(self, sample_registry):
        """Test search returning multiple results."""
        results = search_registry_test("process", sample_registry)
        assert len(results) >= 1
        # Should find Data Processor due to heuristic_tags match

    def test_search_surface_filtering(self, sample_registry):
        """Test search by surface type."""
        results = search_registry_test("python", sample_registry)
        assert len(results) >= 2  # Math Calculator and Data Processor

    def test_search_max_results(self, sample_registry):
        """Test max_results parameter."""
        results = search_registry_test("a", sample_registry, max_results=1)  # Match all
        assert len(results) == 1

    def test_search_scoring_logic(self, sample_registry):
        """Test that scoring works correctly (name matches > purpose matches > description matches)."""
        results = search_registry_test("math", sample_registry)
        assert len(results) == 1
        assert results[0]["name"] == "Math Calculator"
        assert results[0]["score"] > 0

    def test_search_case_insensitive(self, sample_registry):
        """Test that search is case insensitive."""
        results1 = search_registry_test("CALCULATOR", sample_registry)
        results2 = search_registry_test("calculator", sample_registry)
        assert len(results1) == len(results2) == 1
        assert results1[0]["name"] == results2[0]["name"]

    def test_search_missing_registry(self, tmp_path):
        """Test error handling when registry file doesn't exist."""
        missing_file = tmp_path / "missing.json"
        results = search_registry_test("test", missing_file)
        assert len(results) == 1
        assert "error" in results[0]

    def test_search_empty_query(self, sample_registry):
        """Test search with empty query."""
        results = search_registry_test("", sample_registry)
        assert len(results) == 0

    def test_search_logic_tags(self, sample_registry):
        """Test search matching logic_tags."""
        results = search_registry_test("solve", sample_registry)
        assert len(results) == 1
        assert results[0]["name"] == "Logic Solver"

    def test_search_heuristic_tags(self, sample_registry):
        """Test search matching heuristic_tags."""
        results = search_registry_test("transform", sample_registry)
        assert len(results) == 1
        assert results[0]["name"] == "Data Processor"

    def test_search_multi_surface_skill(self, sample_registry):
        """Test search finds multi-surface skills."""
        results = search_registry_test("hy", sample_registry)
        assert len(results) == 1
        assert results[0]["name"] == "Data Processor"
        assert "hy" in results[0]["surfaces"]
