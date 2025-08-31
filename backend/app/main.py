from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from app.utils import multiply_helper, search_helper, format_helper
from app.models import MultiplyRequest, MultiplyResponse, SearchRequest, SearchResponse

# Trivial refactor: add a comment for demo purposes
# This is a demo file with many changes to showcase PR review capabilities
app = FastAPI(
    title="Qodo Demo API",
    description="API for demonstrating large PR review capabilities",
    version="1.0.0"
)

@app.post("/multiply", response_model=MultiplyResponse)
def multiply_endpoint(req: MultiplyRequest):
    # Inefficient loop for demo (suggestion opportunity)
    # This could be optimized with simple multiplication
    result = 0
    for _ in range(req.b):
        for _ in range(req.a):
            result += 1
    return MultiplyResponse(result=result)

@app.get("/health")
def health():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "timestamp": "2024-01-15T10:00:00Z"}

@app.get("/docs-update")
def docs_update():
    """Trivial docstring update for demo purposes."""
    return {"docs": "updated", "version": "1.0.0"}

@app.post("/search", response_model=SearchResponse)
def search_endpoint(req: SearchRequest):
    """New search endpoint for demo purposes."""
    # Trivial validation logic
    if not req.query or len(req.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Simulate search results
    results = search_helper(req.query, req.limit)
    return SearchResponse(
        query=req.query,
        results=results,
        total_count=len(results)
    )

@app.get("/search/simple")
def simple_search(query: str = Query(..., min_length=1)):
    """Simple search endpoint for quick queries."""
    # Trivial endpoint for demo
    return {"query": query, "results": [f"Result for {query}"]}

@app.get("/stats")
def get_stats():
    """Get application statistics."""
    # Trivial stats endpoint
    return {
        "endpoints": 6,
        "version": "1.0.0",
        "status": "healthy"
    }

# Trivial comment addition for demo
# This file demonstrates many small changes
# Each change is intentionally minor to create noise
# The search endpoint is the main feature addition
