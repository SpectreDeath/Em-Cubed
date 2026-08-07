"""Unit tests for production REST API endpoints in api/loopy_ontology_router.py."""

import httpx
import pytest
from fastapi import FastAPI

from api.loopy_ontology_router import router

app = FastAPI()
app.include_router(router)


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.anyio
async def test_loopy_execute_endpoint(client):
    payload = {
        "skill_name": "production-rest-governance-agent",
        "max_iterations": 3,
        "input_payload": {"test": "data"},
    }
    response = await client.post("/api/v1/loopy/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["skill_name"] == "production-rest-governance-agent"
    assert "audit_report" in data


@pytest.mark.anyio
async def test_ontology_validate_endpoint(client):
    payload = {
        "subject": "Order_99",
        "predicate": "has_status",
        "object": "Approved",
        "confidence": 1.0,
        "payload": {},
    }
    response = await client.post("/api/v1/ontology/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["passed"] is True
    assert data["triple"]["subject"] == "Order_99"


@pytest.mark.anyio
async def test_ontology_graph_rag_endpoint(client):
    response = await client.get("/api/v1/ontology/graph-rag?entity_id=Order_99&max_depth=2")
    assert response.status_code == 200
    data = response.json()
    assert data["entity_id"] == "Order_99"
    assert "context_string" in data


@pytest.mark.anyio
async def test_ontology_federated_status_endpoint(client):
    response = await client.get("/api/v1/ontology/federated-status")
    assert response.status_code == 200
    data = response.json()
    assert data["aligned"] is True
