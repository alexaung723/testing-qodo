"""
Middleware module for the Qodo Demo API.
This file demonstrates middleware functionality.
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Trivial middleware for demo purposes
# This file shows middleware evolution
# Each function represents a small addition

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Trivial logging for demo
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request details
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
        )
        
        return response

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware for adding timing headers."""
    
    async def dispatch(self, request: Request, call_next):
        # Trivial timing for demo
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add timing header
        response.headers["X-Request-Time"] = str(duration)
        
        return response

class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation."""
    
    async def dispatch(self, request: Request, call_next):
        # Trivial validation for demo
        if request.method == "POST":
            # Check content type
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type:
                logger.warning(f"Invalid content type: {content_type}")
        
        # Process request
        response = await call_next(request)
        
        return response

# Trivial helper function for demo
def setup_middleware(app):
    """Setup middleware for the application."""
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(ValidationMiddleware)

# Trivial comment addition for demo
# This file shows middleware evolution
# Each middleware represents a small addition
