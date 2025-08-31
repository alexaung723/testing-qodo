"""
This module contains models for the multiply endpoint.
Updated for demo purposes with search functionality.
"""

# Trivial refactor: add a comment for demo purposes
# This file demonstrates model updates for the search feature

from pydantic import BaseModel, Field
from typing import List, Optional

class MultiplyRequest(BaseModel):
    a: int = Field(..., description="First number to multiply")
    b: int = Field(..., description="Second number to multiply")

class MultiplyResponse(BaseModel):
    result: int = Field(..., description="Result of multiplication")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    limit: Optional[int] = Field(default=10, description="Maximum number of results")
    filters: Optional[dict] = Field(default_factory=dict, description="Search filters")

class SearchResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    results: List[str] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total number of results")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")

# Trivial model for demo purposes
class DemoModel(BaseModel):
    """Demo model for showcasing PR changes."""
    name: str = Field(..., description="Demo name")
    value: int = Field(..., description="Demo value")

# Trivial comment addition for demo
# This file shows how models evolve over time
# Each field addition represents a small change
# The search models are the main feature addition
