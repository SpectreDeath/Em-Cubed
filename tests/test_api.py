import json

import httpx
import pytest

from api.main import app


class TestAPI:
    @pytest.fixture
    async def client(self):
        """Create a test client for the FastAPI app."""
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as c:
            yield c

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

        monkeypatch.setattr(
            "em_cubed.search.get_search_index", lambda index_dir=None: WhooshSearchIndex(tmp_path / "whoosh_index")
        )

        return registry_file

    @pytest.mark.anyio
    async def test_health_endpoint(self, client):
        """Test the health endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert "surfaces" in data

        surfaces_dict = data["surfaces"]
        assert surfaces_dict.get("python") is True
        if surfaces_dict.get("prolog"):
            assert surfaces_dict.get("prolog") is True
        if surfaces_dict.get("hy"):
            assert surfaces_dict.get("hy") is True

    @pytest.mark.anyio
    async def test_surfaces_endpoint(self, client):
        """Test the surfaces listing endpoint."""
        response = await client.get("/surfaces")
        assert response.status_code == 200

        data = response.json()
        assert "surfaces" in data

        surfaces = data["surfaces"]
        actual_surface_names = {s["name"] for s in surfaces}
        assert "python" in actual_surface_names, "Python surface should always be available"

        available_surfaces = {s["name"] for s in surfaces if s.get("available", False)}
        assert "python" in available_surfaces, "Python surface should be available"

        for surface in surfaces:
            assert "name" in surface
            assert "available" in surface
            assert "description" in surface

    @pytest.mark.anyio
    async def test_search_endpoint_basic(self, client, sample_registry):
        """Test basic search functionality."""
        response = await client.post("/search", json={"query": "calculator"})
        assert response.status_code == 200

        data = response.json()
        assert "results" in data

        results = data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Math Calculator"

    @pytest.mark.anyio
    async def test_search_endpoint_no_results(self, client, sample_registry):
        """Test search with no results."""
        response = await client.post("/search", json={"query": "nonexistent"})
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 0

    @pytest.mark.anyio
    async def test_search_endpoint_max_results(self, client, sample_registry):
        """Test search with max_results parameter."""
        response = await client.post("/search", json={"query": "a", "max_results": 1})
        assert response.status_code == 200

        data = response.json()
        assert len(data["results"]) == 1

    @pytest.mark.anyio
    async def test_search_endpoint_missing_registry(self, client, monkeypatch):
        """Test search when registry file doesn't exist."""
        monkeypatch.setenv("EM_CUBED_REGISTRY", "/nonexistent/path/registry.json")

        response = await client.post("/search", json={"query": "test"})
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert "error" in data["results"][0]

    @pytest.mark.anyio
    async def test_execute_endpoint_python_simple(self, client):
        """Test executing simple Python code."""
        payload = {"surface": "python", "code": "1 + 2"}

        response = await client.post("/execute", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["value"] == 3

    @pytest.mark.anyio
    async def test_execute_endpoint_python_with_context(self, client):
        """Test executing Python code with context."""
        payload = {"surface": "python", "code": "x + y", "context": {"x": 10, "y": 20}}

        response = await client.post("/execute", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["value"] == 30

    @pytest.mark.anyio
    async def test_execute_endpoint_python_function(self, client):
        """Test executing Python code with simple operations."""
        payload = {"surface": "python", "code": "5 + 3"}

        response = await client.post("/execute", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["value"] == 8

    @pytest.mark.anyio
    async def test_execute_endpoint_unknown_surface(self, client):
        """Test executing on unknown surface."""
        payload = {"surface": "unknown", "code": "1 + 1"}

        response = await client.post("/execute", json=payload)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "Unknown surface" in data["detail"]

    @pytest.mark.anyio
    async def test_execute_endpoint_python_error(self, client):
        """Test executing Python code with syntax error."""
        payload = {
            "surface": "python",
            "code": "invalid syntax here +++",
        }

        response = await client.post("/execute", json=payload)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "syntax" in data["detail"]

    @pytest.mark.anyio
    async def test_execute_endpoint_python_unsafe_code(self, client):
        """Test that unsafe code is blocked by asteval."""
        payload = {
            "surface": "python",
            "code": "__import__('os')",
        }

        response = await client.post("/execute", json=payload)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data

    @pytest.mark.anyio
    async def test_execute_endpoint_prolog(self, client):
        """Test executing Prolog code (if available)."""
        payload = {"surface": "prolog", "code": "X is 1 + 2."}

        response = await client.post("/execute", json=payload)

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "ok"
        else:
            assert response.status_code in {400, 500, 503}

    @pytest.mark.anyio
    async def test_execute_endpoint_hy(self, client):
        """Test executing Hy code (if available)."""
        payload = {"surface": "hy", "code": "(+ 1 2)"}

        response = await client.post("/execute", json=payload)

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "ok"
            assert data["value"] == 3
        else:
            assert response.status_code == 503
            data = response.json()
            assert "is not available" in data["detail"]

    @pytest.mark.anyio
    async def test_api_key_required_when_configured(self, monkeypatch):
        """Test that API key is required when EM_CUBED_API_KEY is set."""
        monkeypatch.setenv("EM_CUBED_API_KEY", "test-secret-key")

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as test_client:
            response = await test_client.get("/health")
            assert response.status_code == 401

            response = await test_client.get("/health", headers={"X-API-Key": "wrong-key"})
            assert response.status_code == 401

            response = await test_client.get("/health", headers={"X-API-Key": "test-secret-key"})
            assert response.status_code == 200

    @pytest.mark.anyio
    async def test_api_key_optional_when_not_configured(self, monkeypatch):
        """Test that API key is optional when EM_CUBED_API_KEY is not set."""
        monkeypatch.delenv("EM_CUBED_API_KEY", raising=False)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as test_client:
            response = await test_client.get("/health")
            assert response.status_code == 200

            response = await test_client.get("/health", headers={"X-API-Key": "any-key"})
            assert response.status_code == 200
