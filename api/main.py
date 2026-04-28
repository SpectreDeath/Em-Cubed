"""FastAPI application for Em-Cubed skill execution and search."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog

from em_cubed.search import search_registry
from em_cubed.surfaces import PythonSurface, PrologSurface, HySurface

logger = structlog.get_logger()

app = FastAPI(
    title="Em-Cubed API",
    description="Multi-Surface Skill Framework API",
    version="0.3.0"
)

# Initialize surfaces
python_surface = PythonSurface()
prolog_surface = PrologSurface()
hy_surface = HySurface()

# Get registry path from environment or default
REGISTRY_PATH = Path(os.getenv("EM_CUBED_REGISTRY", "registry.json"))

# Allow overriding for testing
def get_registry_path():
    return REGISTRY_PATH

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10

class ExecuteRequest(BaseModel):
    surface: str
    code: str
    context: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "surfaces": {
            "python": python_surface.available,
            "prolog": prolog_surface.available,
            "hy": hy_surface.available,
        }
    }

@app.post("/search")
async def search(request: SearchRequest):
    """Search the skill registry."""
    try:
        results = search_registry(request.query, get_registry_path(), request.max_results)
        return {"results": results}
    except Exception as e:
        logger.exception("Search failed", error=str(e), query=request.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/search")
async def search_get(q: str, top: int = 10):
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
async def execute_code(request: ExecuteRequest):
    """Execute code on specified surface."""
    surface_map: Dict[str, Any] = {
        "python": python_surface,
        "prolog": prolog_surface,
        "hy": hy_surface,
    }

    if request.surface not in surface_map:
        raise HTTPException(status_code=400, detail=f"Unknown surface: {request.surface}")

    surface = surface_map[request.surface]

    try:
        if request.surface == "python":
            result = await surface.execute(request.code, request.context)
        else:
            # Prolog and Hy surfaces are synchronous
            result = surface.execute(request.code, request.context)

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Execution failed", error=str(e), surface=request.surface, code_length=len(request.code))
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@app.get("/surfaces")
async def list_surfaces():
    """List available surfaces and their status."""
    return {
        "surfaces": [
            {
                "name": "python",
                "available": python_surface.available,
                "description": "Safe Python execution with asteval"
            },
            {
                "name": "prolog",
                "available": prolog_surface.available,
                "description": "Prolog execution via PySWIP"
            },
            {
                "name": "hy",
                "available": hy_surface.available,
                "description": "Hy Lisp execution"
            }
        ]
    }