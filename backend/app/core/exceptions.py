"""
Enterprise Governance API - Custom Exceptions
Comprehensive exception handling for enterprise applications.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RESOURCE = "resource"
    RATE_LIMIT = "rate_limit"
    INTERNAL = "internal"
    EXTERNAL = "external"
    GOVERNANCE = "governance"
    COMPLIANCE = "compliance"
    COST = "cost"
    SECURITY = "security"
    NETWORK = "network"
    DATABASE = "database"
    CACHE = "cache"
    INTEGRATION = "integration"

class BaseException(Exception):
    """Base exception class for the application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.INTERNAL,
                 details: Optional[Dict[str, Any]] = None,
                 user_message: Optional[str] = None,
                 retry_after: Optional[int] = None,
                 support_reference: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.user_message = user_message or message
        self.retry_after = retry_after
        self.support_reference = support_reference
        self.timestamp = datetime.utcnow()
        self.correlation_id = None
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for tracing."""
        self.correlation_id = correlation_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "details": self.details,
            "user_message": self.user_message,
            "retry_after": self.retry_after,
            "support_reference": self.support_reference,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }

# Validation and Input Errors
class ValidationError(BaseException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, constraints: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            details={
                "field": field,
                "value": value,
                "constraints": constraints
            },
            **kwargs
        )
        self.field = field
        self.value = value
        self.constraints = constraints

class InvalidInputError(BaseException):
    """Raised when input is invalid or malformed."""
    
    def __init__(self, message: str, input_data: Optional[Any] = None, 
                 expected_format: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="INVALID_INPUT",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            details={
                "input_data": input_data,
                "expected_format": expected_format
            },
            **kwargs
        )
        self.input_data = input_data
        self.expected_format = expected_format

# Authentication and Authorization Errors
class AuthenticationError(BaseException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, auth_method: Optional[str] = None,
                 user_id: Optional[str] = None, session_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            details={
                "auth_method": auth_method,
                "user_id": user_id,
                "session_id": session_id
            },
            **kwargs
        )
        self.auth_method = auth_method
        self.user_id = user_id
        self.session_id = session_id

class AuthorizationError(BaseException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str, required_permissions: Optional[List[str]] = None,
                 user_permissions: Optional[List[str]] = None, resource_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHORIZATION,
            details={
                "required_permissions": required_permissions,
                "user_permissions": user_permissions,
                "resource_id": resource_id
            },
            **kwargs
        )
        self.required_permissions = required_permissions
        self.user_permissions = user_permissions
        self.resource_id = resource_id

class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, message: str, required_permissions: List[str],
                 user_permissions: List[str], **kwargs):
        super().__init__(
            message=message,
            required_permissions=required_permissions,
            user_permissions=user_permissions,
            error_code="INSUFFICIENT_PERMISSIONS",
            **kwargs
        )

# Resource and Data Errors
class ResourceNotFoundError(BaseException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, search_criteria: Optional[Dict[str, Any]] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RESOURCE,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "search_criteria": search_criteria
            },
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.search_criteria = search_criteria

class ResourceConflictError(BaseException):
    """Raised when there's a conflict with a resource."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, conflict_type: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RESOURCE,
            details={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "conflict_type": conflict_type
            },
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.conflict_type = conflict_type

class ResourceLimitExceededError(BaseException):
    """Raised when resource limits are exceeded."""
    
    def __init__(self, message: str, limit_type: Optional[str] = None,
                 current_usage: Optional[Any] = None, limit_value: Optional[Any] = None,
                 reset_time: Optional[datetime] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="RESOURCE_LIMIT_EXCEEDED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RESOURCE,
            details={
                "limit_type": limit_type,
                "current_usage": current_usage,
                "limit_value": limit_value,
                "reset_time": reset_time.isoformat() if reset_time else None
            },
            **kwargs
        )
        self.limit_type = limit_type
        self.current_usage = current_usage
        self.limit_value = limit_value
        self.reset_time = reset_time

# Rate Limiting and Throttling Errors
class RateLimitExceededError(BaseException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, rate_limit: Optional[int] = None,
                 current_usage: Optional[int] = None, window_seconds: Optional[int] = None,
                 retry_after: Optional[int] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RATE_LIMIT,
            retry_after=retry_after,
            details={
                "rate_limit": rate_limit,
                "current_usage": current_usage,
                "window_seconds": window_seconds
            },
            **kwargs
        )
        self.rate_limit = rate_limit
        self.current_usage = current_usage
        self.window_seconds = window_seconds

class ThrottlingError(BaseException):
    """Raised when request throttling occurs."""
    
    def __init__(self, message: str, throttle_type: Optional[str] = None,
                 throttle_duration: Optional[int] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="THROTTLING_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RATE_LIMIT,
            details={
                "throttle_type": throttle_type,
                "throttle_duration": throttle_duration
            },
            **kwargs
        )
        self.throttle_type = throttle_type
        self.throttle_duration = throttle_duration

# Database and Storage Errors
class DatabaseConnectionError(BaseException):
    """Raised when database connection fails."""
    
    def __init__(self, message: str, database_type: Optional[str] = None,
                 connection_string: Optional[str] = None, retry_count: Optional[int] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_CONNECTION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            details={
                "database_type": database_type,
                "connection_string": connection_string,
                "retry_count": retry_count
            },
            **kwargs
        )
        self.database_type = database_type
        self.connection_string = connection_string
        self.retry_count = retry_count

class DatabaseQueryError(BaseException):
    """Raised when database query fails."""
    
    def __init__(self, message: str, query: Optional[str] = None,
                 parameters: Optional[Dict[str, Any]] = None, execution_time: Optional[float] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_QUERY_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.DATABASE,
            details={
                "query": query,
                "parameters": parameters,
                "execution_time": execution_time
            },
            **kwargs
        )
        self.query = query
        self.parameters = parameters
        self.execution_time = execution_time

class DatabaseMigrationError(BaseException):
    """Raised when database migration fails."""
    
    def __init__(self, message: str, migration_version: Optional[str] = None,
                 migration_name: Optional[str] = None, rollback_required: bool = False,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_MIGRATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            details={
                "migration_version": migration_version,
                "migration_name": migration_name,
                "rollback_required": rollback_required
            },
            **kwargs
        )
        self.migration_version = migration_version
        self.migration_name = migration_name
        self.rollback_required = rollback_required

# Governance and Compliance Errors
class GovernanceException(BaseException):
    """Raised when governance policies are violated."""
    
    def __init__(self, message: str, governance_tier: Optional[str] = None,
                 compliance_impact: Optional[str] = None, policy_id: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="GOVERNANCE_VIOLATION",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.GOVERNANCE,
            details={
                "governance_tier": governance_tier,
                "compliance_impact": compliance_impact,
                "policy_id": policy_id
            },
            **kwargs
        )
        self.governance_tier = governance_tier
        self.compliance_impact = compliance_impact
        self.policy_id = policy_id

class ComplianceException(BaseException):
    """Raised when compliance requirements are not met."""
    
    def __init__(self, message: str, requirement: Optional[str] = None,
                 risk_level: Optional[str] = None, compliance_framework: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="COMPLIANCE_VIOLATION",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.COMPLIANCE,
            details={
                "requirement": requirement,
                "risk_level": risk_level,
                "compliance_framework": compliance_framework
            },
            **kwargs
        )
        self.requirement = requirement
        self.risk_level = risk_level
        self.compliance_framework = compliance_framework

class AccessControlException(BaseException):
    """Raised when access control policies are violated."""
    
    def __init__(self, message: str, required_permissions: Optional[List[str]] = None,
                 user_permissions: Optional[List[str]] = None, resource_type: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="ACCESS_CONTROL_VIOLATION",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHORIZATION,
            details={
                "required_permissions": required_permissions,
                "user_permissions": user_permissions,
                "resource_type": resource_type
            },
            **kwargs
        )
        self.required_permissions = required_permissions
        self.user_permissions = user_permissions
        self.resource_type = resource_type

# Cost and Resource Management Errors
class CostLimitExceededError(BaseException):
    """Raised when cost limits are exceeded."""
    
    def __init__(self, message: str, cost_type: Optional[str] = None,
                 current_cost: Optional[float] = None, cost_limit: Optional[float] = None,
                 reset_period: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="COST_LIMIT_EXCEEDED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.COST,
            details={
                "cost_type": cost_type,
                "current_cost": current_cost,
                "cost_limit": cost_limit,
                "reset_period": reset_period
            },
            **kwargs
        )
        self.cost_type = cost_type
        self.current_cost = current_cost
        self.cost_limit = cost_limit
        self.reset_period = reset_period

class ResourceQuotaExceededError(BaseException):
    """Raised when resource quotas are exceeded."""
    
    def __init__(self, message: str, quota_type: Optional[str] = None,
                 current_usage: Optional[int] = None, quota_limit: Optional[int] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="RESOURCE_QUOTA_EXCEEDED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.RESOURCE,
            details={
                "quota_type": quota_type,
                "current_usage": current_usage,
                "quota_limit": quota_limit
            },
            **kwargs
        )
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.quota_limit = quota_limit

# Security and Network Errors
class SecurityException(BaseException):
    """Raised when security violations occur."""
    
    def __init__(self, message: str, security_level: Optional[str] = None,
                 threat_type: Optional[str] = None, ip_address: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="SECURITY_VIOLATION",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY,
            details={
                "security_level": security_level,
                "threat_type": threat_type,
                "ip_address": ip_address
            },
            **kwargs
        )
        self.security_level = security_level
        self.threat_type = threat_type
        self.ip_address = ip_address

class NetworkException(BaseException):
    """Raised when network-related errors occur."""
    
    def __init__(self, message: str, network_type: Optional[str] = None,
                 endpoint: Optional[str] = None, status_code: Optional[int] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.NETWORK,
            details={
                "network_type": network_type,
                "endpoint": endpoint,
                "status_code": status_code
            },
            **kwargs
        )
        self.network_type = network_type
        self.endpoint = endpoint
        self.status_code = status_code

# Integration and External Service Errors
class ExternalServiceError(BaseException):
    """Raised when external service calls fail."""
    
    def __init__(self, message: str, service_name: Optional[str] = None,
                 endpoint: Optional[str] = None, status_code: Optional[int] = None,
                 response_body: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.EXTERNAL,
            details={
                "service_name": service_name,
                "endpoint": endpoint,
                "status_code": status_code,
                "response_body": response_body
            },
            **kwargs
        )
        self.service_name = service_name
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_body = response_body

class IntegrationError(BaseException):
    """Raised when integration operations fail."""
    
    def __init__(self, message: str, integration_type: Optional[str] = None,
                 integration_id: Optional[str] = None, operation: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="INTEGRATION_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.INTEGRATION,
            details={
                "integration_type": integration_type,
                "integration_id": integration_id,
                "operation": operation
            },
            **kwargs
        )
        self.integration_type = integration_type
        self.integration_id = integration_id
        self.operation = operation

# Internal and System Errors
class InternalError(BaseException):
    """Raised when internal system errors occur."""
    
    def __init__(self, message: str, component: Optional[str] = None,
                 operation: Optional[str] = None, stack_trace: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="INTERNAL_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.INTERNAL,
            details={
                "component": component,
                "operation": operation,
                "stack_trace": stack_trace
            },
            **kwargs
        )
        self.component = component
        self.operation = operation
        self.stack_trace = stack_trace

class ConfigurationError(BaseException):
    """Raised when configuration errors occur."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_value: Optional[Any] = None, config_file: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.INTERNAL,
            details={
                "config_key": config_key,
                "config_value": config_value,
                "config_file": config_file
            },
            **kwargs
        )
        self.config_key = config_key
        self.config_value = config_value
        self.config_file = config_file

# Cache and Performance Errors
class CacheError(BaseException):
    """Raised when cache operations fail."""
    
    def __init__(self, message: str, cache_type: Optional[str] = None,
                 operation: Optional[str] = None, key: Optional[str] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CACHE,
            details={
                "cache_type": cache_type,
                "operation": operation,
                "key": key
            },
            **kwargs
        )
        self.cache_type = cache_type
        self.operation = operation
        self.key = key

class PerformanceException(BaseException):
    """Raised when performance thresholds are exceeded."""
    
    def __init__(self, message: str, metric_name: Optional[str] = None,
                 current_value: Optional[float] = None, threshold_value: Optional[float] = None,
                 **kwargs):
        super().__init__(
            message=message,
            error_code="PERFORMANCE_THRESHOLD_EXCEEDED",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.INTERNAL,
            details={
                "metric_name": metric_name,
                "current_value": current_value,
                "threshold_value": threshold_value
            },
            **kwargs
        )
        self.metric_name = metric_name
        self.current_value = current_value
        self.threshold_value = threshold_value

# Utility Functions
def create_error_response(exception: BaseException) -> Dict[str, Any]:
    """Create a standardized error response from an exception."""
    return {
        "error": exception.to_dict(),
        "timestamp": datetime.utcnow().isoformat(),
        "success": False
    }

def is_retryable_error(exception: BaseException) -> bool:
    """Check if an error is retryable."""
    retryable_categories = [
        ErrorCategory.NETWORK,
        ErrorCategory.DATABASE,
        ErrorCategory.EXTERNAL,
        ErrorCategory.RATE_LIMIT
    ]
    
    retryable_codes = [
        "RATE_LIMIT_EXCEEDED",
        "THROTTLING_ERROR",
        "NETWORK_ERROR",
        "EXTERNAL_SERVICE_ERROR"
    ]
    
    return (
        exception.category in retryable_categories or
        exception.error_code in retryable_codes
    )

def get_error_severity(exception: BaseException) -> ErrorSeverity:
    """Get the severity level of an exception."""
    return exception.severity

def should_log_error(exception: BaseException) -> bool:
    """Determine if an error should be logged."""
    return exception.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]

def get_user_friendly_message(exception: BaseException) -> str:
    """Get a user-friendly error message."""
    return exception.user_message or "An unexpected error occurred. Please try again later."
