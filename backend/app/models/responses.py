"""
Enterprise Governance API - Response Models
Response models for all API endpoints with comprehensive data structures.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

class ResponseStatus(str, Enum):
    """Response status values."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"

class ErrorCode(str, Enum):
    """Standard error codes."""
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INTERNAL_ERROR = "internal_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    GOVERNANCE_VIOLATION = "governance_violation"
    COMPLIANCE_VIOLATION = "compliance_violation"
    COST_LIMIT_EXCEEDED = "cost_limit_exceeded"

class HealthStatus(str, Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class BaseResponse(BaseModel):
    """Base response model with common fields."""
    status: ResponseStatus = Field(..., description="Response status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    version: str = Field(default="3.0.0", description="API version")
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class ErrorResponse(BaseResponse):
    """Error response model."""
    status: ResponseStatus = Field(default=ResponseStatus.ERROR, description="Response status")
    error_code: ErrorCode = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Detailed error information")
    error_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    retry_after: Optional[int] = Field(None, ge=0, description="Retry after seconds")
    support_reference: Optional[str] = Field(None, description="Support reference ID")
    
    # Governance and compliance information
    governance_tier: Optional[str] = Field(None, description="Governance tier for this error")
    compliance_impact: Optional[str] = Field(None, description="Compliance impact of this error")
    risk_level: Optional[str] = Field(None, description="Risk level of this error")

class SuccessResponse(BaseResponse):
    """Success response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    # Performance metrics
    response_time: Optional[float] = Field(None, ge=0, description="Response time in seconds")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    
    # Governance information
    governance_tier: Optional[str] = Field(None, description="Governance tier for this response")
    compliance_status: Optional[str] = Field(None, description="Compliance status")

class HealthCheckResponse(BaseResponse):
    """Health check response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    overall_status: HealthStatus = Field(..., description="Overall system health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    response_time: float = Field(..., ge=0, description="Response time in seconds")
    
    # Component health
    components: Dict[str, Dict[str, Any]] = Field(..., description="Health status of individual components")
    
    # System information
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Application environment")
    uptime: Optional[float] = Field(None, ge=0, description="System uptime in seconds")
    
    # Additional health metrics
    memory_usage: Optional[float] = Field(None, ge=0, le=100, description="Memory usage percentage")
    cpu_usage: Optional[float] = Field(None, ge=0, le=100, description="CPU usage percentage")
    disk_usage: Optional[float] = Field(None, ge=0, le=100, description="Disk usage percentage")
    
    # Error information
    errors: List[str] = Field(default_factory=list, description="List of health check errors")
    warnings: List[str] = Field(default_factory=list, description="List of health check warnings")

class MetricsResponse(BaseResponse):
    """Metrics response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    period: str = Field(..., description="Metrics period")
    granularity: str = Field(..., description="Metrics granularity")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    
    # Cost metrics
    cost_metrics: Dict[str, Any] = Field(..., description="Cost-related metrics")
    
    # Usage metrics
    usage_metrics: Dict[str, Any] = Field(..., description="Usage-related metrics")
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = Field(..., description="Performance-related metrics")
    
    # Compliance metrics
    compliance_metrics: Dict[str, Any] = Field(..., description="Compliance-related metrics")
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metrics metadata")

class ModelDeploymentResponse(BaseResponse):
    """Model deployment response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    deployment: Dict[str, Any] = Field(..., description="Deployment information")
    governance_approval_id: Optional[str] = Field(None, description="Governance approval ID")
    compliance_status: str = Field(..., description="Compliance status")
    
    # Deployment details
    deployment_id: str = Field(..., description="Unique deployment ID")
    deployment_name: str = Field(..., description="Deployment name")
    deployment_status: str = Field(..., description="Current deployment status")
    
    # Timeline
    created_at: datetime = Field(..., description="Deployment creation timestamp")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    # Cost information
    cost_estimate: Optional[Decimal] = Field(None, ge=0, description="Estimated monthly cost")
    budget_allocation: Optional[str] = Field(None, description="Budget allocation source")
    
    # Governance information
    governance_tier: str = Field(..., description="Governance tier for deployment")
    risk_assessment: str = Field(..., description="Risk assessment level")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow used")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Deployment tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional deployment metadata")

class GovernanceConfigResponse(BaseResponse):
    """Governance configuration response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    config: Dict[str, Any] = Field(..., description="Governance configuration")
    last_updated: datetime = Field(..., description="Last update timestamp")
    updated_by: str = Field(..., description="User ID who last updated the configuration")
    
    # Configuration details
    config_id: str = Field(..., description="Configuration ID")
    config_name: str = Field(..., description="Configuration name")
    config_version: str = Field(..., description="Configuration version")
    
    # Governance settings
    governance_mode: str = Field(..., description="Current governance mode")
    compliance_level: str = Field(..., description="Current compliance level")
    risk_tolerance: str = Field(..., description="Current risk tolerance")
    
    # Access control settings
    require_approval: bool = Field(..., description="Whether approval is required")
    auto_approval_limit: Optional[Decimal] = Field(None, ge=0, description="Auto-approval cost limit")
    
    # Usage limits
    daily_request_limit: Optional[int] = Field(None, ge=0, description="Daily request limit")
    monthly_cost_limit: Optional[Decimal] = Field(None, ge=0, description="Monthly cost limit")
    
    # Compliance settings
    audit_logging_enabled: bool = Field(..., description="Whether audit logging is enabled")
    compliance_reporting_enabled: bool = Field(..., description="Whether compliance reporting is enabled")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Configuration tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional configuration metadata")

class AccessControlResponse(BaseResponse):
    """Access control response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    policy: Dict[str, Any] = Field(..., description="Access control policy")
    
    # Policy details
    policy_id: str = Field(..., description="Policy ID")
    policy_name: str = Field(..., description="Policy name")
    policy_version: str = Field(..., description="Policy version")
    
    # Policy scope
    resource_type: str = Field(..., description="Type of resource being controlled")
    resource_id: Optional[str] = Field(None, description="Specific resource ID")
    user_id: Optional[str] = Field(None, description="Specific user ID")
    team_id: Optional[str] = Field(None, description="Specific team ID")
    
    # Permissions
    permissions: List[str] = Field(..., description="Allowed permissions")
    denied_permissions: List[str] = Field(default_factory=list, description="Denied permissions")
    
    # Governance
    governance_tier: str = Field(..., description="Governance tier")
    requires_approval: bool = Field(..., description="Whether access requires approval")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Policy tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional policy metadata")

class ComplianceReportResponse(BaseResponse):
    """Compliance report response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    report: Dict[str, Any] = Field(..., description="Compliance report")
    
    # Report details
    report_id: str = Field(..., description="Report ID")
    report_type: str = Field(..., description="Report type")
    report_scope: str = Field(..., description="Report scope")
    report_period: str = Field(..., description="Report period")
    
    # Compliance metrics
    overall_compliance_score: float = Field(..., ge=0, le=100, description="Overall compliance score")
    compliance_by_framework: Dict[str, float] = Field(..., description="Compliance scores by framework")
    compliance_by_requirement: Dict[str, float] = Field(..., description="Compliance scores by requirement")
    
    # Risk assessment
    risk_level: str = Field(..., description="Overall risk level")
    risk_by_category: Dict[str, str] = Field(..., description="Risk levels by category")
    risk_findings: List[str] = Field(default_factory=list, description="Risk findings")
    
    # Audit information
    audit_findings: List[str] = Field(default_factory=list, description="Audit findings")
    audit_recommendations: List[str] = Field(default_factory=list, description="Audit recommendations")
    next_audit_date: Optional[datetime] = Field(None, description="Next audit date")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Report tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional report metadata")

class CostAnalysisResponse(BaseResponse):
    """Cost analysis response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    analysis: Dict[str, Any] = Field(..., description="Cost analysis results")
    
    # Analysis details
    analysis_id: str = Field(..., description="Analysis ID")
    analysis_type: str = Field(..., description="Analysis type")
    analysis_scope: str = Field(..., description="Analysis scope")
    analysis_period: str = Field(..., description="Analysis period")
    
    # Cost breakdown
    total_cost: Decimal = Field(..., ge=0, description="Total cost for the period")
    cost_by_provider: Dict[str, Decimal] = Field(..., description="Cost breakdown by provider")
    cost_by_service: Dict[str, Decimal] = Field(..., description="Cost breakdown by service")
    cost_by_team: Dict[str, Decimal] = Field(..., description="Cost breakdown by team")
    
    # Cost trends
    cost_trend: str = Field(..., description="Cost trend direction")
    cost_change_percentage: float = Field(..., description="Cost change percentage")
    cost_forecast: Optional[Dict[str, Decimal]] = Field(None, description="Cost forecast")
    
    # Optimization recommendations
    optimization_recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    potential_savings: Optional[Decimal] = Field(None, ge=0, description="Potential cost savings")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Analysis tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional analysis metadata")

class TeamCollaborationResponse(BaseResponse):
    """Team collaboration response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    collaboration: Dict[str, Any] = Field(..., description="Team collaboration information")
    
    # Collaboration details
    collaboration_id: str = Field(..., description="Collaboration ID")
    collaboration_name: str = Field(..., description="Collaboration name")
    collaboration_type: str = Field(..., description="Collaboration type")
    
    # Team structure
    lead_team_id: str = Field(..., description="Lead team ID")
    participating_teams: List[str] = Field(..., description="Participating team IDs")
    stakeholder_teams: List[str] = Field(default_factory=list, description="Stakeholder team IDs")
    
    # Collaboration status
    status: str = Field(..., description="Collaboration status")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    
    # Resource sharing
    shared_resources: List[str] = Field(default_factory=list, description="Shared resources")
    access_levels: Dict[str, str] = Field(..., description="Access levels for each team")
    
    # Budget and cost sharing
    total_budget: Optional[Decimal] = Field(None, ge=0, description="Total collaboration budget")
    budget_allocation: Dict[str, Decimal] = Field(..., description="Budget allocation per team")
    cost_sharing_model: str = Field(..., description="Cost sharing model")
    
    # Timeline
    start_date: Optional[datetime] = Field(None, description="Collaboration start date")
    end_date: Optional[datetime] = Field(None, description="Collaboration end date")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Collaboration tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional collaboration metadata")

class PaginatedResponse(BaseResponse):
    """Paginated response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    data: List[Dict[str, Any]] = Field(..., description="Response data items")
    
    # Pagination information
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Page size")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=1, description="Total number of pages")
    
    # Navigation
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, ge=1, description="Next page number")
    previous_page: Optional[int] = Field(None, ge=1, description="Previous page number")
    
    # Additional information
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional pagination metadata")

class BulkOperationResponse(BaseResponse):
    """Bulk operation response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    
    # Operation results
    total_operations: int = Field(..., ge=0, description="Total number of operations")
    successful_operations: int = Field(..., ge=0, description="Number of successful operations")
    failed_operations: int = Field(..., ge=0, description="Number of failed operations")
    skipped_operations: int = Field(..., ge=0, description="Number of skipped operations")
    
    # Detailed results
    successful_items: List[Dict[str, Any]] = Field(default_factory=list, description="Successfully processed items")
    failed_items: List[Dict[str, Any]] = Field(default_factory=list, description="Failed items with error details")
    skipped_items: List[Dict[str, Any]] = Field(default_factory=list, description="Skipped items with reasons")
    
    # Performance metrics
    total_processing_time: float = Field(..., ge=0, description="Total processing time in seconds")
    average_processing_time: float = Field(..., ge=0, description="Average processing time per operation")
    
    # Additional information
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional operation metadata")

class AuditLogResponse(BaseResponse):
    """Audit log response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    audit_logs: List[Dict[str, Any]] = Field(..., description="Audit log entries")
    
    # Log summary
    total_logs: int = Field(..., ge=0, description="Total number of audit logs")
    logs_by_action: Dict[str, int] = Field(..., description="Log count by action type")
    logs_by_user: Dict[str, int] = Field(..., description="Log count by user")
    logs_by_resource: Dict[str, int] = Field(..., description="Log count by resource type")
    
    # Compliance information
    compliance_score: Optional[float] = Field(None, ge=0, le=100, description="Overall compliance score")
    governance_violations: int = Field(..., ge=0, description="Number of governance violations")
    security_incidents: int = Field(..., ge=0, description="Number of security incidents")
    
    # Time range
    start_date: datetime = Field(..., description="Start date for the logs")
    end_date: datetime = Field(..., description="End date for the logs")
    
    # Additional information
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional audit log metadata")

class ModelUsageResponse(BaseResponse):
    """Model usage response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    usage_data: Dict[str, Any] = Field(..., description="Model usage information")
    
    # Usage details
    model_id: str = Field(..., description="Model ID")
    deployment_id: Optional[str] = Field(None, description="Deployment ID")
    user_id: str = Field(..., description="User ID")
    
    # Usage metrics
    total_requests: int = Field(..., ge=0, description="Total number of requests")
    successful_requests: int = Field(..., ge=0, description="Number of successful requests")
    failed_requests: int = Field(..., ge=0, description="Number of failed requests")
    
    # Cost information
    total_cost: Decimal = Field(..., ge=0, description="Total cost for usage")
    cost_by_provider: Optional[Decimal] = Field(None, ge=0, description="Cost charged by provider")
    cost_by_team: Optional[Decimal] = Field(None, ge=0, description="Cost allocated to team")
    
    # Performance metrics
    average_response_time: Optional[float] = Field(None, ge=0, description="Average response time")
    total_tokens_processed: Optional[int] = Field(None, ge=0, description="Total tokens processed")
    
    # Compliance information
    compliance_status: str = Field(..., description="Compliance status")
    governance_tier: str = Field(..., description="Governance tier")
    
    # Additional information
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional usage metadata")

class NotificationResponse(BaseResponse):
    """Notification response model."""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS, description="Response status")
    notification: Dict[str, Any] = Field(..., description="Notification information")
    
    # Notification details
    notification_id: str = Field(..., description="Notification ID")
    notification_type: str = Field(..., description="Notification type")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    
    # Recipients
    recipient_ids: List[str] = Field(..., description="Recipient user IDs")
    recipient_teams: List[str] = Field(default_factory=list, description="Recipient team IDs")
    
    # Notification status
    status: str = Field(..., description="Notification status")
    priority: str = Field(..., description="Notification priority")
    read_by: List[str] = Field(default_factory=list, description="User IDs who have read the notification")
    
    # Delivery
    delivery_methods: List[str] = Field(..., description="Delivery methods used")
    delivery_status: Dict[str, str] = Field(..., description="Delivery status by method")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Notification tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional notification metadata")
