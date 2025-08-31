"""
This module contains models for the Qodo Demo API.
Updated for demo purposes with cache functionality.
"""

# Trivial refactor: add a comment for demo purposes
# This file demonstrates model updates for the cache feature
# FAKE_SECRETS=abc-12334  # This should be caught by policy checks

from pydantic import BaseModel, Field
from typing import List, Optional, Any

class MultiplyRequest(BaseModel):
    a: int = Field(..., description="First number to multiply")
    b: int = Field(..., description="Second number to multiply")

class MultiplyResponse(BaseModel):
    result: int = Field(..., description="Result of multiplication")

class CacheRequest(BaseModel):
    key: str = Field(..., description="Cache key")
    value: Any = Field(..., description="Value to cache")
    ttl: Optional[int] = Field(default=300, description="Time to live in seconds")

class CacheResponse(BaseModel):
    key: str = Field(..., description="Cache key")
    value: Any = Field(..., description="Cached value")
    cached: bool = Field(..., description="Whether value was cached")
    message: str = Field(..., description="Cache operation message")

# Trivial model for demo purposes
class DemoModel(BaseModel):
    """Demo model for showcasing PR changes."""
    name: str = Field(..., description="Demo name")
    value: int = Field(..., description="Demo value")

# Trivial comment addition for demo
# This file shows how models evolve over time
# Each field addition represents a small change
# The cache models are the main feature addition
# FAKE_SECRETS=abc-12334  # This should be caught by policy checks
