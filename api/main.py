"""FastAPI application for Em-Cubed skill execution and search."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog

from fastapi import Depends, HTTPException, status

from em_cubed.search import search_registry
from em_cubed.plugin_manager import PluginManager
from em_cubed import __version__

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