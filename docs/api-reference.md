# Em-Cubed API Reference

## Overview

The Em-Cubed API provides REST endpoints for searching skills and executing code across multiple programming surfaces (Python, Prolog, Hy Lisp, etc.).

## Authentication

All endpoints require an API key in the `X-API-Key` header if `EM_CUBED_API_KEY` environment variable is set.

## Endpoints

### GET /health

Health check endpoint that returns system status and available surfaces.

**Response:**
```json
{
  "status": "ok",
  "surfaces": ["python", "prolog", "hy", "z3", "datalog"]
}
```

### POST /search

Search the skill registry for relevant skills.

**Request Body:**
```json
{
  "query": "string",     // Search query
  "max_results": 10      // Maximum number of results (default: 10)
}
```

**Response:**
```json
{
  "results": [
    {
      "name": "Skill Name",
      "domain": "Domain",
      "purpose": "Brief purpose statement",
      "description": "Full skill description",
      "path": "skills/domain/skill-name/SKILL.md",
      "surfaces": ["python", "prolog"],
      "logic_tags": ["constraint", "optimization"],
      "heuristic_tags": ["graph", "search"],
      "tags": ["constraint", "optimization", "graph", "search"],
      "score": 0.95
    }
  ]
}
```

**Error Response:**
```json
[{
  "error": "Registry file not found. Run indexer first."
}]
```

### GET /search

Same as POST /search but with query parameters.

**Parameters:**
- `q`: Search query (required)
- `top`: Maximum results (default: 10)

**Example:** `GET /search?q=math&top=5`

### POST /execute

Execute code on a specified surface.

**Request Body:**
```json
{
  "surface": "python",           // Surface name (python, prolog, hy, z3, datalog)
  "code": "print('hello')",      // Code to execute
  "context": {"var": "value"},   // Optional context variables (Python only)
  "timeout": 10.0                // Optional timeout in seconds
}
```

**Response (Success):**
```json
{
  "status": "ok",
  "value": "result"  // Execution result
}
```

**Response (Execution Error):**
```json
{
  "status": "error",
  "message": "Error details from surface"
}
```

**HTTP Error Responses:**
```json
{
  "detail": "Error message"
}
```
- `400`: Invalid surface, malformed code
- `401`: Invalid or missing API key
- `500`: Internal server error
- `503`: Surface not available
```

### GET /surfaces

List all surfaces with their availability status and descriptions.

**Response:**
```json
{
  "surfaces": [
    {
      "name": "python",
      "description": "Safe Python execution with asteval",
      "available": true
    },
    {
      "name": "prolog",
      "description": "Prolog execution via PySWIP",
      "available": false
    }
  ]
}
```

## Surface-Specific Details

### Python Surface
- **Security:** Uses asteval for safe execution
- **Limitations:** No file I/O, imports, or system calls
- **Context:** Variables passed in `context` are available in code
- **Return:** Last expression result

### Prolog Surface
- **Syntax:** Standard Prolog with queries starting with `?-`
- **Results:** Query results as list of bindings
- **Timeout:** Applies to query execution

### Other Surfaces
- Z3: SMT solver for logical constraints
- Hy: Lisp syntax compiling to Python AST
- Datalog: Logic programming with stratified negation

## Error Handling

All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid surface, malformed code)
- `401`: Unauthorized (invalid API key)
- `500`: Internal server error
- `503`: Service unavailable (surface not available)

Error responses include a `detail` field with error description.

## Examples

### Search for math skills
```bash
curl -X POST http://localhost:8000/search \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "calculate", "max_results": 5}'
```

### Execute Python code
```bash
curl -X POST http://localhost:8000/execute \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "surface": "python",
    "code": "x = 2 + 3; x * 4",
    "context": {"extra": 10}
  }'
```

### Execute Prolog query
```bash
curl -X POST http://localhost:8000/execute \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "surface": "prolog",
    "code": "?- member(X, [1,2,3,4])"
  }'
```