from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
from app.utils import multiply_helper, cache_helper
from app.models import MultiplyRequest, MultiplyResponse, CacheRequest, CacheResponse

# Trivial refactor: add a comment for demo purposes
# This is a demo file with cache functionality and policy check opportunities
app = FastAPI(
    title="Qodo Demo API",
    description="API for demonstrating policy check capabilities",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.post("/cache", response_model=CacheResponse)
def cache_endpoint(req: CacheRequest):
    """Cache endpoint for demo purposes."""
    # Intentionally log PII for policy check demo
    # This should be caught by Qodo Merge
    user_email = "user@example.com"  # FAKE_EMAIL_FOR_DEMO
    logger.info(f"Processing cache request for user: {user_email}")
    
    # Simulate cache operation
    success = cache_helper(req.key, req.value)
    
    if success:
        return CacheResponse(
            key=req.key,
            value=req.value,
            cached=True,
            message="Value cached successfully"
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to cache value")

@app.get("/cache/{key}")
def get_cached_value(key: str):
    """Get cached value by key."""
    # Intentionally log SSN-like string for policy check demo
    # This should be caught by Qodo Merge
    fake_ssn = "123-45-6789"  # FAKE_SSN_FOR_DEMO
    logger.info(f"Retrieving cache for key: {key}, user: {fake_ssn}")
    
    # Simulate cache retrieval
    cached_value = cache_helper(key, None)
    if cached_value:
        return {"key": key, "value": cached_value, "cached": True}
    else:
        raise HTTPException(status_code=404, detail="Key not found in cache")

@app.get("/stats")
def get_stats():
    """Get application statistics."""
    # Trivial stats endpoint
    return {
        "endpoints": 6,
        "version": "1.0.0",
        "status": "healthy",
        "cache_enabled": True
    }

# Trivial comment addition for demo
# This file demonstrates cache functionality
# Each change is intentionally minor to create noise
# The cache endpoint is the main feature addition
# FAKE_SECRETS=abc-12334  # This should be caught by policy checks
