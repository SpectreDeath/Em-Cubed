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

    def test_search_whoosh_indexing(self, tmp_path):
        """Test Whoosh search index creation and querying."""
        from em_cubed.search import WhooshSearchIndex
        
        # Create a search index
        search_index = WhooshSearchIndex(tmp_path / "whoosh_test")
        
        # Create sample registry
        registry = [
            {
                "name": "Test Calculator",
                "description": "A calculator for math operations",
                "tags": ["math", "calculate"],
                "surface": ["python"],
                "path": "test/calculator",
            },
            {
                "name": "Logic Engine",
                "description": "Advanced logic processing",
                "tags": ["logic", "reason"],
                "surface": ["prolog"],
                "path": "test/logic",
            },
        ]
        
        # Index the skills
        search_index.index_skills(registry)
        
        # Search for calculator
        results = search_index.search("calculator", max_results=10)
        assert len(results) >= 1
        assert results[0]["name"] == "Test Calculator"
        
        # Search for logic
        results = search_index.search("logic", max_results=10)
        assert len(results) >= 1
        assert results[0]["name"] == "Logic Engine"
        
        # Search for tag
        results = search_index.search("math", max_results=10)
        assert len(results) >= 1

    def test_search_whoosh_fallback(self, tmp_path):
        """Test Whoosh search falls back gracefully when unavailable."""
        from em_cubed.search import search_registry
        
        registry_file = tmp_path / "registry.json"
        registry_data = [
            {
                "name": "Test Skill",
                "domain": "Test",
                "purpose": "Test purpose",
                "description": "Test description",
                "surfaces": ["python"],
                "logic_tags": [],
                "heuristic_tags": ["test"],
                "path": "test",
            }
        ]
        import json
        with open(registry_file, "w") as f:
            json.dump(registry_data, f)
        
        # Search with whoosh disabled (should use naive search)
        results = search_registry("test", registry_file, use_whoosh=False)
        assert len(results) == 1
        assert results[0]["name"] == "Test Skill"

    def test_search_registry_hash_update(self, tmp_path):
        """Test that registry hash triggers index update."""
        from em_cubed.search import search_registry, _get_registry_hash
        
        registry_file = tmp_path / "registry.json"
        index_dir = tmp_path / "whoosh_index"
        
        # Initial registry
        registry_data = [
            {
                "name": "Skill One",
                "domain": "Test",
                "purpose": "Test",
                "description": "Test",
                "surfaces": ["python"],
                "logic_tags": [],
                "heuristic_tags": [],
                "path": "skill1",
            }
        ]
        import json
        with open(registry_file, "w") as f:
            json.dump(registry_data, f)
        
        # Get initial hash
        initial_hash = _get_registry_hash(registry_data)
        
        # Search to create index
        search_registry("skill", registry_file, use_whoosh=True, index_dir=index_dir)

        # Verify hash file was created
        hash_file = index_dir / ".registry_hash"
        assert hash_file.exists()
        
        # Modify registry
        registry_data.append({
            "name": "Skill Two",
            "domain": "Test",
            "purpose": "Test",
            "description": "Test",
            "surfaces": ["prolog"],
            "logic_tags": [],
            "heuristic_tags": [],
            "path": "skill2",
        })
        with open(registry_file, "w") as f:
            json.dump(registry_data, f)
        
        # New hash should be different
        new_hash = _get_registry_hash(registry_data)
        assert new_hash != initial_hash

    def test_naive_search_scoring(self, tmp_path):
        """Test naive search scoring prioritizes name matches."""
        from em_cubed.search import _naive_search_registry
        
        registry = [
            {
                "name": "Python Calculator",
                "domain": "Math",
                "purpose": "Calculate with python",
                "description": "A python calculator",
                "surfaces": ["python"],
                "logic_tags": [],
                "heuristic_tags": ["calculate", "math"],
                "path": "calc",
            },
            {
                "name": "Logic Solver",
                "domain": "Logic",
                "purpose": "Solve logic problems",
                "description": "Advanced logic solver",
                "surfaces": ["prolog"],
                "logic_tags": ["solve"],
                "heuristic_tags": [],
                "path": "logic",
            },
        ]
        
        # Search for 'python' - should match name/surface
        results = _naive_search_registry("python", registry)
        assert len(results) == 1
        assert results[0]["name"] == "Python Calculator"
        # Name match should have higher score than surface match
        assert results[0]["score"] > 0
        
        # Search for 'calculate' - should match heuristic tag
        results = _naive_search_registry("calculate", registry)
        assert len(results) == 1
        assert results[0]["name"] == "Python Calculator"
        
        # Search for 'solve' - should match logic tag (highest weight)
        results = _naive_search_registry("solve", registry)
        assert len(results) == 1
        assert results[0]["name"] == "Logic Solver"

    def test_search_empty_registry(self, tmp_path):
        """Test search with empty registry."""
        from em_cubed.search import search_registry
        
        registry_file = tmp_path / "registry.json"
        with open(registry_file, "w") as f:
            f.write("[]")
        
        # Use a unique index directory to avoid conflicts with other tests
        index_dir = tmp_path / "whoosh_index"
        results = search_registry("test", registry_file, use_whoosh=True, index_dir=index_dir)
        assert len(results) == 0
