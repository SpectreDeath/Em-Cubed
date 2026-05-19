"""FastAPI application for Em-Cubed skill execution and search."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog

from fastapi import Depends, status

from em_cubed.search import search_registry
from em_cubed.plugin_manager import PluginManager
from em_cubed import __version__
from em_cubed.telemetry.api import initialize_telemetry_api, get_telemetry_api, initialize_websocket_handler, get_websocket_handler
from em_cubed.skills.telemetry import get_telemetry_collector

logger = structlog.get_logger()

app = FastAPI(
    title="Em-Cubed API",
    description="Multi-Surface Skill Framework API",
    version=__version__
)

# Initialize plugin manager
plugin_manager = PluginManager()

# Allow overriding for testing
def get_registry_path():
    return Path(os.getenv("EM_CUBED_REGISTRY", "registry.json"))


# API key authentication
def get_api_key(request: Request):
    """Extract API key from X-API-Key header."""
    return request.headers.get("X-API-Key")

def require_api_key(api_key: str = Depends(get_api_key)):
    """Dependency that validates API key if EM_CUBED_API_KEY is configured."""
    configured_key = os.getenv("EM_CUBED_API_KEY")
    if configured_key and api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

# Initialize telemetry
telemetry_collector = get_telemetry_collector()
telemetry_api = initialize_telemetry_api(telemetry_collector)
websocket_handler = initialize_websocket_handler(telemetry_collector)

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10

class ExecuteRequest(BaseModel):
    surface: str
    code: str
    context: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = None

@app.get("/health")
async def health(api_key: str = Depends(require_api_key)):
    """Health check endpoint."""
    return {
        "status": "ok",
        "surfaces": plugin_manager.list_plugins(),
    }

@app.post("/search")
async def search(request: SearchRequest, api_key: str = Depends(require_api_key)):
    """Search the skill registry."""
    try:
        results = search_registry(request.query, get_registry_path(), request.max_results)
        return {"results": results}
    except Exception as e:
        logger.exception("Search failed", error=str(e), query=request.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/search")
async def search_get(q: str, top: int = 10, api_key: str = Depends(require_api_key)):
    """Search the skill registry via GET."""
    try:
        results = search_registry(q, get_registry_path(), top)
        return {"results": results}
    except Exception as e:
        logger.exception("Search failed", error=str(e), query=q)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Telemetry endpoints
@app.get("/telemetry/health")
async def telemetry_health(api_key: str = Depends(require_api_key)):
    """Get telemetry system health."""
    api = get_telemetry_api()
    if api:
        return api.get_system_health()
    return {"status": "unavailable"}


@app.get("/telemetry/skills")
async def get_available_skills(api_key: str = Depends(require_api_key)):
    """Get list of skills with telemetry data."""
    api = get_telemetry_api()
    if api:
        return {"skills": api.get_available_skills()}
    return {"skills": []}


@app.get("/telemetry/skill/{skill_id}")
async def get_skill_metrics(skill_id: str, window_seconds: int = 3600, api_key: str = Depends(require_api_key)):
    """Get metrics for a specific skill."""
    api = get_telemetry_api()
    if api:
        return api.get_skill_metrics(skill_id, window_seconds)
    return {"count": 0}


@app.get("/telemetry/stats")
async def get_overall_stats(api_key: str = Depends(require_api_key)):
    """Get overall telemetry statistics."""
    api = get_telemetry_api()
    if api:
        return api.get_overall_stats()
    return {"total_executions": 0}


@app.get("/telemetry/recent")
async def get_recent_executions(limit: int = 50, api_key: str = Depends(require_api_key)):
    """Get recent skill executions."""
    api = get_telemetry_api()
    if api:
        return {"executions": api.get_recent_executions(limit)}
    return {"executions": []}


@app.get("/telemetry/skill/{skill_id}/executions")
async def get_skill_executions(skill_id: str, limit: int = 50, api_key: str = Depends(require_api_key)):
    """Get executions for a specific skill."""
    api = get_telemetry_api()
    if api:
        return {"executions": api.get_skill_executions(skill_id, limit)}
    return {"executions": []}


# WebSocket endpoint for real-time updates
@app.websocket("/telemetry/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time telemetry updates."""
    await websocket.accept()
    handler = get_websocket_handler()
    if handler:
        handler.subscribe(websocket)
        try:
            while True:
                # Keep connection alive, in a real implementation we'd handle incoming messages
                data = await websocket.receive_text()
                # Echo back or handle as needed
                await websocket.send_text(f"Echo: {data}")
        except Exception:
            if handler:
                handler.unsubscribe(websocket)


@app.post("/execute")
async def execute_code(request: ExecuteRequest, api_key: str = Depends(require_api_key)):
    """Execute code on specified surface."""
    surface = plugin_manager.get(request.surface)

    if not surface:
        available_surfaces = plugin_manager.get_available_surfaces()
        raise HTTPException(status_code=400, detail=f"Unknown surface: {request.surface}. Available: {', '.join(available_surfaces)}")

    if not surface.available:
        raise HTTPException(status_code=503, detail=f"Surface '{request.surface}' is not available")

    try:
        result = await surface.execute(request.code, request.context)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Execution failed", error=str(e), surface=request.surface, code_length=len(request.code))
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.get("/surfaces")
async def list_surfaces(api_key: str = Depends(require_api_key)):
    """List available surfaces and their status."""
    return {
        "surfaces": plugin_manager.get_surface_info()
    }