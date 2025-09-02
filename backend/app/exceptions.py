"""
Custom exceptions for the Qodo Demo API.
This file demonstrates exception handling.
"""

from typing import Optional, Dict, Any

# Trivial exceptions for demo purposes
# This file shows exception evolution
# Each class represents a small addition

class QodoDemoException(Exception):
    """Base exception for Qodo Demo API."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        # Trivial initialization for demo
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}

class SearchException(QodoDemoException):
    """Exception raised for search-related errors."""
    
    def __init__(self, message: str, query: Optional[str] = None):
        # Trivial initialization for demo
        super().__init__(message, "SEARCH_ERROR", {"query": query})

class ValidationException(QodoDemoException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        # Trivial initialization for demo
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})

class DatabaseException(QodoDemoException):
    """Exception raised for database errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        # Trivial initialization for demo
        super().__init__(message, "DATABASE_ERROR", {"operation": operation})

class RateLimitException(QodoDemoException):
    """Exception raised for rate limiting."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        # Trivial initialization for demo
        super().__init__(message, "RATE_LIMIT_ERROR", {"retry_after": retry_after})

class ConfigurationException(QodoDemoException):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        # Trivial initialization for demo
        super().__init__(message, "CONFIGURATION_ERROR", {"config_key": config_key})

# Trivial helper function for demo
def format_exception(exception: QodoDemoException) -> Dict[str, Any]:
    """Format exception for API response."""
    return {
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "details": exception.details
        }
    }

# Trivial comment addition for demo
# This file shows exception evolution
# Each exception represents a small addition
