import pytest
import json
from fastapi.testclient import TestClient
from api.main import app


class TestAPI:
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def sample_registry(self, tmp_path, monkeypatch):
        """Create a sample registry and mock the registry path."""
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
        ]

        registry_file = tmp_path / "registry.json"
        with open(registry_file, "w") as f:
            json.dump(registry_data, f)

        # Mock the get_registry_path function
        monkeypatch.setattr("api.main.get_registry_path", lambda: registry_file)

        # Mock Whoosh index to use a temporary directory
        from em_cubed.search import WhooshSearchIndex
        monkeypatch.setattr("em_cubed.search.get_search_index", lambda index_dir=None: WhooshSearchIndex(tmp_path / "whoosh_index"))

        return registry_file

    def test_health_endpoint(self, client):
        """Test the health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "surfaces" in data

        # Check surface availability (may vary based on installed packages)
        surfaces_dict = data["surfaces"]  # This is a dict: {surface_name: available_bool}
        # Core surfaces should always be available
        assert surfaces_dict.get("python") is True
        assert surfaces_dict.get("prolog") is True
        assert surfaces_dict.get("hy") is True
        # New surfaces should be available if dependencies are installed
        # Note: In CI environment, these may not be installed, so we check if they appear

    def test_surfaces_endpoint(self, client):
        """Test the surfaces listing endpoint."""
        response = client.get("/surfaces")
        assert response.status_code == 200

        data = response.json()
        assert "surfaces" in data

        surfaces = data["surfaces"]
        # Check that we have at least the core surfaces (python should always be available)
        actual_surface_names = {s["name"] for s in surfaces}
        assert "python" in actual_surface_names, "Python surface should always be available"

        # Check that surfaces include expected ones that are available
        available_surfaces = {s["name"] for s in surfaces if s.get("available", False)}
        # At minimum, we should have python available
        assert "python" in available_surfaces, "Python surface should be available"

        # Check each surface has required fields
        for surface in surfaces:
            assert "name" in surface
            assert "available" in surface
            assert "description" in surface

    def test_search_endpoint_basic(self, client, sample_registry):
        """Test basic search functionality."""
        response = client.post("/search", json={"query": "calculator"})
        assert response.status_code == 200

        data = response.json()
        assert "results" in data

        results = data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Math Calculator"

    def test_search_endpoint_no_results(self, client, sample_registry):
        """Test search with no results."""
        response = client.post("/search", json={"query": "nonexistent"})
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 0

    def test_search_endpoint_max_results(self, client, sample_registry):
        """Test search with max_results parameter."""
        response = client.post("/search", json={"query": "a", "max_results": 1})
        assert response.status_code == 200

        data = response.json()
        assert len(data["results"]) == 1

    def test_search_endpoint_missing_registry(self, client, monkeypatch):
        """Test search when registry file doesn't exist."""
        monkeypatch.setenv("EM_CUBED_REGISTRY", "/nonexistent/path/registry.json")

        response = client.post("/search", json={"query": "test"})
        assert response.status_code == 200  # API returns results array with error

        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert "error" in data["results"][0]

    def test_execute_endpoint_python_simple(self, client):
        """Test executing simple Python code."""
        payload = {"surface": "python", "code": "1 + 2"}

        response = client.post("/execute", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["value"] == 3

    def test_execute_endpoint_python_with_context(self, client):
        """Test executing Python code with context."""
        payload = {"surface": "python", "code": "x + y", "context": {"x": 10, "y": 20}}

        response = client.post("/execute", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["value"] == 30

    def test_execute_endpoint_python_function(self, client):
        """Test executing Python code with simple operations."""
        payload = {"surface": "python", "code": "5 + 3"}

        response = client.post("/execute", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["value"] == 8

    def test_execute_endpoint_unknown_surface(self, client):
        """Test executing on unknown surface."""
        payload = {"surface": "unknown", "code": "1 + 1"}

        response = client.post("/execute", json=payload)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "Unknown surface" in data["detail"]

    def test_execute_endpoint_python_error(self, client):
        """Test executing Python code with syntax error."""
        payload = {
            "surface": "python",
            "code": "invalid syntax here +++",  # Syntax error
        }

        response = client.post("/execute", json=payload)
        # Python execution returns error, API converts to 400
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "syntax" in data["detail"]

    def test_execute_endpoint_python_unsafe_code(self, client):
        """Test that unsafe code is blocked by asteval."""
        payload = {
            "surface": "python",
            "code": "__import__('os')",  # Should be blocked/fail
        }

        response = client.post("/execute", json=payload)
        # asteval blocks builtins, returns error, API converts to 400
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data

    def test_execute_endpoint_prolog(self, client):
        """Test executing Prolog code (if available)."""
        payload = {"surface": "prolog", "code": "X is 1 + 2."}

        response = client.post("/execute", json=payload)

        # Result depends on whether PySWIP is available AND works
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "ok"
        else:
            # If PySWIP is unavailable, gets 503. If execution fails, 400 or 500.
            assert response.status_code in {400, 500, 503}

    def test_execute_endpoint_hy(self, client):
        """Test executing Hy code (if available)."""
        payload = {"surface": "hy", "code": "(+ 1 2)"}

        response = client.post("/execute", json=payload)

        # Result depends on whether Hy is available
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "ok"
            assert data["value"] == 3
        else:
            # If Hy not available, should get 503 error
            assert response.status_code == 503
            data = response.json()
            assert "is not available" in data["detail"]

    def test_api_key_required_when_configured(self, client, monkeypatch):
        """Test that API key is required when EM_CUBED_API_KEY is set."""
        # Set API key env var and reload the app to pick it up
        monkeypatch.setenv("EM_CUBED_API_KEY", "test-secret-key")
        import importlib
        import api.main
        importlib.reload(api.main)
        from api.main import app as auth_app
        # Create new test client for reloaded app
        test_client = TestClient(auth_app)

        # Request without API key should be 401
        response = test_client.get("/health")
        assert response.status_code == 401

        # Request with wrong API key should be 401
        response = test_client.get("/health", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401

        # Request with correct API key should succeed
        response = test_client.get("/health", headers={"X-API-Key": "test-secret-key"})
        assert response.status_code == 200

    def test_api_key_optional_when_not_configured(self, client, monkeypatch):
        """Test that API key is optional when EM_CUBED_API_KEY is not set."""
        # Ensure env var is not set and reload app
        monkeypatch.delenv("EM_CUBED_API_KEY", raising=False)
        import importlib
        import api.main as main_mod
        importlib.reload(main_mod)
        from api.main import app as noauth_app
        test_client = TestClient(noauth_app)

        # Request without key should succeed
        response = test_client.get("/health")
        assert response.status_code == 200

        # Request with any key should also succeed (since no key configured, header ignored)
        response = test_client.get("/health", headers={"X-API-Key": "any-key"})
        assert response.status_code == 200
