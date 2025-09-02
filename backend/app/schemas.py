"""
Pydantic schemas for the Qodo Demo API.
This file demonstrates schema definitions.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Trivial schemas for demo purposes
# This file shows schema evolution
# Each schema represents a small addition

class BaseSchema(BaseModel):
    """Base schema with common fields."""
    
    class Config:
        # Trivial config for demo
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SearchQuerySchema(BaseSchema):
    """Schema for search query parameters."""
    
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    limit: Optional[int] = Field(default=10, ge=1, le=100, description="Result limit")
    offset: Optional[int] = Field(default=0, ge=0, description="Result offset")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Search filters")
    sort_by: Optional[str] = Field(default="relevance", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$", description="Sort order")
    
    @validator('query')
    def validate_query(cls, v):
        # Trivial validation for demo
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

class SearchResultSchema(BaseSchema):
    """Schema for search results."""
    
    id: str = Field(..., description="Result identifier")
    title: str = Field(..., description="Result title")
    description: Optional[str] = Field(None, description="Result description")
    url: Optional[str] = Field(None, description="Result URL")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")

class SearchResponseSchema(BaseSchema):
    """Schema for search response."""
    
    query: str = Field(..., description="Original search query")
    results: List[SearchResultSchema] = Field(..., description="Search results")
    total_count: int = Field(..., ge=0, description="Total result count")
    page: int = Field(..., ge=1, description="Current page number")
    total_pages: int = Field(..., ge=1, description="Total page count")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
    execution_time: float = Field(..., ge=0.0, description="Query execution time")
    suggestions: Optional[List[str]] = Field(None, description="Search suggestions")

class ApiUsageSchema(BaseSchema):
    """Schema for API usage statistics."""
    
    endpoint: str = Field(..., description="API endpoint")
    method: str = Field(..., description="HTTP method")
    count: int = Field(..., ge=0, description="Request count")
    avg_response_time: float = Field(..., ge=0.0, description="Average response time")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")

class HealthCheckSchema(BaseSchema):
    """Schema for health check response."""
    
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., ge=0.0, description="Service uptime in seconds")
    dependencies: Dict[str, str] = Field(..., description="Dependency statuses")

# Trivial helper function for demo
def create_search_response(query: str, results: List[Dict], total: int) -> SearchResponseSchema:
    """Create a search response from raw data."""
    # Trivial helper for demo
    return SearchResponseSchema(
        query=query,
        results=[SearchResultSchema(**result) for result in results],
        total_count=total,
        page=1,
        total_pages=1,
        has_next=False,
        has_prev=False,
        execution_time=0.1
    )

# Trivial comment addition for demo
# This file shows schema evolution
# Each schema represents a small addition
