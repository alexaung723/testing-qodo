"""
Constants for the Qodo Demo API.
This file demonstrates constant definitions.
"""

# Trivial constants for demo purposes
# This file shows constant evolution
# Each constant represents a small addition

# Application constants
APP_NAME = "Qodo Demo API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API for demonstrating large PR review capabilities"

# API constants
API_PREFIX = "/api/v1"
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30

# HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

# HTTP methods
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"
HTTP_PATCH = "PATCH"

# Content types
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_TEXT = "text/plain"
CONTENT_TYPE_HTML = "text/html"

# Database constants
DB_DEFAULT_TIMEOUT = 30
DB_MAX_CONNECTIONS = 10
DB_MIN_CONNECTIONS = 1

# Search constants
SEARCH_DEFAULT_LIMIT = 10
SEARCH_MAX_LIMIT = 100
SEARCH_MIN_QUERY_LENGTH = 1
SEARCH_MAX_QUERY_LENGTH = 100

# Cache constants
CACHE_DEFAULT_TTL = 300
CACHE_MAX_TTL = 3600
CACHE_MIN_TTL = 60

# Logging constants
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# Time constants
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7

# File constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [".txt", ".json", ".csv", ".xml"]
MAX_FILENAME_LENGTH = 255

# Security constants
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
TOKEN_EXPIRY_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5

# Validation constants
EMAIL_MAX_LENGTH = 254
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50
PHONE_MAX_LENGTH = 20

# Pagination constants
DEFAULT_PAGE = 1
MIN_PAGE = 1
MAX_PAGE = 10000

# Sorting constants
SORT_ASC = "asc"
SORT_DESC = "desc"
DEFAULT_SORT_FIELD = "created_at"
DEFAULT_SORT_ORDER = SORT_DESC

# Filter constants
FILTER_OPERATORS = ["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "like"]
DEFAULT_FILTER_OPERATOR = "eq"

# Response constants
RESPONSE_SUCCESS = "success"
RESPONSE_ERROR = "error"
RESPONSE_WARNING = "warning"
RESPONSE_INFO = "info"

# Trivial helper function for demo
def get_constant_value(constant_name: str):
    """Get the value of a constant by name."""
    return globals().get(constant_name)

# Trivial comment addition for demo
# This file shows constant evolution
# Each constant represents a small addition
