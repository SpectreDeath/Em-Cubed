from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI(title='Em-Cubed API', version='0.1.0')

@app.get('/health')
async def health():
    return {'status': 'ok'}

@app.get('/surfaces')
async def list_surfaces():
    # Will be connected to registry
    return {'surfaces': []}

@app.post('/skills/{name}/run')
async def run_skill(name: str, context: Dict[str, Any]):
    return {'result': None}

@app.post('/index')
async def index_document(doc: Dict[str, Any]):
    return {'indexed': True}

@app.get('/search')
async def search(query: str):
    return {'results': []}
