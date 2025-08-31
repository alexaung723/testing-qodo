"""
Enterprise Governance API - Shared Models
Core data models used across multiple teams and services.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

class EntityType(str, Enum):
    """Types of entities in the system."""
    USER = "user"
    TEAM = "team"
    PROJECT = "project"
    MODEL = "model"
    DEPLOYMENT = "deployment"
    AUDIT_LOG = "audit_log"
    GOVERNANCE_CONFIG = "governance_config"
    ACCESS_CONTROL = "access_control"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"
    APPROVAL_REQUEST = "approval_request"

class AccessLevel(str, Enum):
    """User access levels."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"
    SUPER_ADMIN = "super_admin"

class GovernanceTier(str, Enum):
    """Governance tiers for different levels of control."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    ENTERPRISE = "enterprise"
    RESTRICTED = "restricted"

class ComplianceLevel(str, Enum):
    """Compliance levels for regulatory requirements."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class RiskLevel(str, Enum):
    """Risk levels for governance and compliance."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApprovalStatus(str, Enum):
    """Approval request statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class DeploymentStatus(str, Enum):
    """Model deployment statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    SCALING = "scaling"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class BaseEntity(BaseModel):
    """Base entity with common fields for all shared models."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the entity")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the entity")
    entity_type: EntityType = Field(..., description="Type of entity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Entity tags")
    is_active: bool = Field(default=True, description="Whether entity is active")
    version: str = Field(default="1.0.0", description="Entity version")
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }

class User(BaseEntity):
    """User model with comprehensive access control and governance."""
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username for authentication")
    first_name: str = Field(..., min_length=1, max_length=50, description="User first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User last name")
    display_name: Optional[str] = Field(None, description="Display name for UI")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")
    
    # Access control
    access_level: AccessLevel = Field(default=AccessLevel.READ, description="User access level")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    roles: List[str] = Field(default_factory=list, description="User roles")
    
    # Team and organization
    team_id: Optional[str] = Field(None, description="Primary team ID")
    team_ids: List[str] = Field(default_factory=list, description="All team IDs user belongs to")
    department: Optional[str] = Field(None, description="User department")
    organization: Optional[str] = Field(None, description="User organization")
    location: Optional[str] = Field(None, description="User location")
    
    # Governance and compliance
    governance_tier: GovernanceTier = Field(default=GovernanceTier.STANDARD, description="User governance tier")
    compliance_level: ComplianceLevel = Field(default=ComplianceLevel.INTERMEDIATE, description="User compliance level")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="User risk level")
    
    # Account status
    is_active: bool = Field(default=True, description="Whether user account is active")
    is_verified: bool = Field(default=False, description="Whether user email is verified")
    is_locked: bool = Field(default=False, description="Whether user account is locked")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_attempts: int = Field(default=0, description="Failed login attempts")
    
    # Security
    password_hash: Optional[str] = Field(None, description="Hashed password")
    mfa_enabled: bool = Field(default=False, description="Whether MFA is enabled")
    mfa_secret: Optional[str] = Field(None, description="MFA secret key")
    api_key_hash: Optional[str] = Field(None, description="Hashed API key")
    
    # Preferences
    timezone: str = Field(default="UTC", description="User timezone")
    language: str = Field(default="en", description="User language preference")
    notification_preferences: Dict[str, bool] = Field(default_factory=dict, description="Notification preferences")
    
    entity_type: EntityType = Field(default=EntityType.USER)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v or '.' not in v:
            raise ValueError("Invalid email format")
        return v.lower()
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be between 3 and 30 characters")
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain alphanumeric characters, underscores, and hyphens")
        return v.lower()
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def can_deploy_models(self) -> bool:
        """Check if user can deploy models."""
        return "models:deploy" in self.permissions or self.access_level in [AccessLevel.ADMIN, AccessLevel.OWNER, AccessLevel.SUPER_ADMIN]
    
    @property
    def can_manage_governance(self) -> bool:
        """Check if user can manage governance."""
        return "governance:write" in self.permissions or self.access_level in [AccessLevel.ADMIN, AccessLevel.OWNER, AccessLevel.SUPER_ADMIN]
    
    @property
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return "users:write" in self.permissions or self.access_level in [AccessLevel.ADMIN, AccessLevel.OWNER, AccessLevel.SUPER_ADMIN]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.access_level in [AccessLevel.ADMIN, AccessLevel.OWNER, AccessLevel.SUPER_ADMIN]
    
    @property
    def is_super_admin(self) -> bool:
        """Check if user is a super admin."""
        return self.access_level == AccessLevel.SUPER_ADMIN

class Team(BaseEntity):
    """Team model for cross-team collaboration and governance."""
    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, max_length=500, description="Team description")
    display_name: Optional[str] = Field(None, description="Display name for UI")
    logo_url: Optional[str] = Field(None, description="Team logo URL")
    
    # Team structure
    lead_id: str = Field(..., description="User ID of the team lead")
    member_ids: List[str] = Field(default_factory=list, description="Team member IDs")
    admin_ids: List[str] = Field(default_factory=list, description="Team admin IDs")
    parent_team_id: Optional[str] = Field(None, description="Parent team ID for hierarchical structure")
    child_team_ids: List[str] = Field(default_factory=list, description="Child team IDs")
    
    # Organization
    department: str = Field(..., description="Department the team belongs to")
    organization: str = Field(..., description="Organization the team belongs to")
    location: Optional[str] = Field(None, description="Team location")
    timezone: str = Field(default="UTC", description="Team timezone")
    
    # Governance and compliance
    governance_tier: GovernanceTier = Field(..., description="Team governance tier")
    compliance_level: ComplianceLevel = Field(..., description="Team compliance level")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Team risk level")
    
    # Access control
    permissions: List[str] = Field(default_factory=list, description="Team permissions")
    roles: List[str] = Field(default_factory=list, description="Team roles")
    access_controls: List[str] = Field(default_factory=list, description="Access control policy IDs")
    
    # Budget and resources
    budget_limit: Optional[Decimal] = Field(None, ge=0, description="Monthly budget limit")
    budget_used: Decimal = Field(default=Decimal('0'), ge=0, description="Budget used this month")
    model_usage_quota: Optional[int] = Field(None, ge=0, description="Monthly model usage quota")
    model_usage_used: int = Field(default=0, ge=0, description="Model usage this month")
    
    # Team settings
    review_cycle: str = Field(default="quarterly", description="Team review cycle")
    next_review_date: Optional[datetime] = Field(None, description="Next review date")
    auto_approval_limit: Optional[Decimal] = Field(None, ge=0, description="Auto-approval cost limit")
    requires_approval: bool = Field(default=True, description="Whether team actions require approval")
    
    # Compliance requirements
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirement IDs")
    audit_frequency: str = Field(default="monthly", description="Audit frequency")
    last_audit_date: Optional[datetime] = Field(None, description="Last audit date")
    next_audit_date: Optional[datetime] = Field(None, description="Next audit date")
    
    entity_type: EntityType = Field(default=EntityType.TEAM)
    
    @validator('next_review_date')
    def validate_review_date(cls, v):
        """Validate that review date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Review date must be in the future")
        return v
    
    @validator('next_audit_date')
    def validate_audit_date(cls, v):
        """Validate that audit date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Audit date must be in the future")
        return v
    
    @property
    def member_count(self) -> int:
        """Get the number of team members."""
        return len(self.member_ids) + 1  # +1 for team lead
    
    @property
    def is_over_budget(self) -> bool:
        """Check if team is over budget."""
        if self.budget_limit is None:
            return False
        return self.budget_used > self.budget_limit
    
    @property
    def is_over_quota(self) -> bool:
        """Check if team is over usage quota."""
        if self.model_usage_quota is None:
            return False
        return self.model_usage_used > self.model_usage_quota
    
    @property
    def budget_remaining(self) -> Optional[Decimal]:
        """Get remaining budget."""
        if self.budget_limit is None:
            return None
        return max(Decimal('0'), self.budget_limit - self.budget_used)
    
    @property
    def quota_remaining(self) -> Optional[int]:
        """Get remaining usage quota."""
        if self.model_usage_quota is None:
            return None
        return max(0, self.model_usage_quota - self.model_usage_used)
    
    @property
    def budget_usage_percentage(self) -> Optional[float]:
        """Get budget usage percentage."""
        if self.budget_limit is None or self.budget_limit == 0:
            return None
        return float((self.budget_used / self.budget_limit) * 100)
    
    @property
    def quota_usage_percentage(self) -> Optional[float]:
        """Get quota usage percentage."""
        if self.model_usage_quota is None or self.model_usage_quota == 0:
            return None
        return (self.model_usage_used / self.model_usage_quota) * 100

class Project(BaseEntity):
    """Project model for cross-team collaboration and governance."""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    display_name: Optional[str] = Field(None, description="Display name for UI")
    logo_url: Optional[str] = Field(None, description="Project logo URL")
    
    # Project structure
    owner_id: str = Field(..., description="User ID who owns the project")
    team_ids: List[str] = Field(default_factory=list, description="Teams involved in the project")
    member_ids: List[str] = Field(default_factory=list, description="Project member IDs")
    admin_ids: List[str] = Field(default_factory=list, description="Project admin IDs")
    
    # Project details
    status: str = Field(default="active", description="Project status")
    priority: str = Field(default="medium", description="Project priority")
    category: str = Field(..., description="Project category")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    
    # Timeline
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    estimated_duration_days: Optional[int] = Field(None, ge=0, description="Estimated duration in days")
    
    # Governance and compliance
    governance_level: GovernanceTier = Field(..., description="Governance level for the project")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirement IDs")
    risk_assessment: RiskLevel = Field(default=RiskLevel.LOW, description="Project risk level")
    
    # Budget and resources
    budget_limit: Optional[Decimal] = Field(None, ge=0, description="Project budget limit")
    budget_used: Decimal = Field(default=Decimal('0'), ge=0, description="Budget used so far")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")
    
    # Review and approval
    review_cycle: str = Field(default="monthly", description="Project review cycle")
    next_review_date: Optional[datetime] = Field(None, description="Next review date")
    requires_approval: bool = Field(default=True, description="Whether project changes require approval")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    
    # Compliance tracking
    audit_frequency: str = Field(default="monthly", description="Audit frequency")
    last_audit_date: Optional[datetime] = Field(None, description="Last audit date")
    next_audit_date: Optional[datetime] = Field(None, description="Next audit date")
    compliance_score: Optional[float] = Field(None, ge=0, le=100, description="Compliance score")
    
    entity_type: EntityType = Field(default=EntityType.PROJECT)
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date."""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError("End date must be after start date")
        return v
    
    @validator('next_review_date')
    def validate_review_date(cls, v):
        """Validate that review date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Review date must be in the future")
        return v
    
    @property
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status.lower() == "active"
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status.lower() == "completed"
    
    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue."""
        if not self.end_date:
            return False
        return datetime.utcnow() > self.end_date
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until end date."""
        if not self.end_date:
            return None
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def budget_remaining(self) -> Optional[Decimal]:
        """Get remaining budget."""
        if self.budget_limit is None:
            return None
        return max(Decimal('0'), self.budget_limit - self.budget_used)
    
    @property
    def budget_usage_percentage(self) -> Optional[float]:
        """Get budget usage percentage."""
        if self.budget_limit is None or self.budget_limit == 0:
            return None
        return float((self.budget_used / self.budget_limit) * 100)
    
    @property
    def progress_percentage(self) -> Optional[float]:
        """Calculate project progress percentage."""
        if not self.start_date or not self.end_date:
            return None
        
        total_duration = (self.end_date - self.start_date).days
        if total_duration <= 0:
            return 100.0
        
        elapsed_duration = (datetime.utcnow() - self.start_date).days
        progress = min(100.0, max(0.0, (elapsed_duration / total_duration) * 100))
        return progress

class SharedModel(BaseEntity):
    """Shared model for cross-team AI model usage."""
    name: str = Field(..., min_length=1, max_length=100, description="Model name")
    version: str = Field(..., description="Model version")
    description: Optional[str] = Field(None, max_length=500, description="Model description")
    display_name: Optional[str] = Field(None, description="Display name for UI")
    logo_url: Optional[str] = Field(None, description="Model logo URL")
    
    # Model details
    model_type: str = Field(..., description="Type of model (e.g., classification, generation)")
    architecture: str = Field(..., description="Model architecture")
    parameters: Optional[int] = Field(None, ge=0, description="Number of model parameters")
    input_format: str = Field(..., description="Input format expected by the model")
    output_format: str = Field(..., description="Output format produced by the model")
    
    # Provider information
    provider: str = Field(..., description="Model provider (e.g., OpenAI, Anthropic, Google)")
    provider_model_id: Optional[str] = Field(None, description="Provider's model identifier")
    endpoint_url: Optional[str] = Field(None, description="Model endpoint URL")
    api_key_required: bool = Field(default=True, description="Whether API key is required")
    
    # Performance and limits
    rate_limit: Optional[int] = Field(None, ge=0, description="Rate limit per minute")
    concurrent_limit: Optional[int] = Field(None, ge=0, description="Concurrent request limit")
    max_input_length: Optional[int] = Field(None, ge=0, description="Maximum input length")
    max_output_length: Optional[int] = Field(None, ge=0, description="Maximum output length")
    
    # Cost and pricing
    cost_per_request: Optional[Decimal] = Field(None, ge=0, description="Cost per request")
    cost_per_token: Optional[Decimal] = Field(None, ge=0, description="Cost per token")
    cost_per_second: Optional[Decimal] = Field(None, ge=0, description="Cost per second of processing")
    
    # Governance and compliance
    governance_classification: GovernanceTier = Field(..., description="Governance classification")
    compliance_level: ComplianceLevel = Field(..., description="Compliance level")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Model risk level")
    
    # Access control
    team_ownership: List[str] = Field(default_factory=list, description="Teams that own this model")
    access_controls: List[str] = Field(default_factory=list, description="Access control policy IDs")
    requires_approval: bool = Field(default=True, description="Whether model usage requires approval")
    
    # Usage and monitoring
    usage_limits: Dict[str, Any] = Field(default_factory=dict, description="Usage limits")
    monitoring_enabled: bool = Field(default=True, description="Whether monitoring is enabled")
    alerting_enabled: bool = Field(default=True, description="Whether alerting is enabled")
    
    # Compliance and audit
    compliance_tags: List[str] = Field(default_factory=list, description="Compliance tags")
    audit_requirements: List[str] = Field(default_factory=list, description="Audit requirement IDs")
    data_retention_policy: Optional[str] = Field(None, description="Data retention policy")
    
    # Model lifecycle
    lifecycle_stage: str = Field(default="development", description="Model lifecycle stage")
    deprecation_date: Optional[datetime] = Field(None, description="Model deprecation date")
    replacement_model_id: Optional[str] = Field(None, description="Replacement model ID")
    
    entity_type: EntityType = Field(default=EntityType.MODEL)
    
    @validator('endpoint_url')
    def validate_endpoint_url(cls, v, values):
        """Validate endpoint URL for self-hosted models."""
        if values.get('provider') == 'self_hosted' and not v:
            raise ValueError("Endpoint URL is required for self-hosted models")
        return v
    
    @property
    def is_deprecated(self) -> bool:
        """Check if model is deprecated."""
        if not self.deprecation_date:
            return False
        return datetime.utcnow() > self.deprecation_date
    
    @property
    def is_self_hosted(self) -> bool:
        """Check if model is self-hosted."""
        return self.provider.lower() == "self_hosted"
    
    @property
    def is_restricted(self) -> bool:
        """Check if model has restricted access."""
        return self.governance_classification in [GovernanceTier.ENTERPRISE, GovernanceTier.RESTRICTED]
    
    @property
    def requires_governance_approval(self) -> bool:
        """Check if model requires governance approval."""
        return self.governance_classification in [GovernanceTier.ENHANCED, GovernanceTier.ENTERPRISE, GovernanceTier.RESTRICTED]

class Deployment(BaseEntity):
    """Model deployment with comprehensive governance controls."""
    model_id: str = Field(..., description="ID of the deployed model")
    deployment_name: str = Field(..., min_length=1, max_length=100, description="Deployment name")
    description: Optional[str] = Field(None, max_length=500, description="Deployment description")
    
    # Deployment details
    environment: str = Field(..., description="Deployment environment")
    region: str = Field(..., description="Deployment region")
    availability_zone: Optional[str] = Field(None, description="Availability zone")
    instance_type: str = Field(..., description="Instance type for deployment")
    
    # Infrastructure configuration
    scaling_config: Dict[str, Any] = Field(default_factory=dict, description="Scaling configuration")
    monitoring_config: Dict[str, Any] = Field(default_factory=dict, description="Monitoring configuration")
    security_config: Dict[str, Any] = Field(default_factory=dict, description="Security configuration")
    network_config: Dict[str, Any] = Field(default_factory=dict, description="Network configuration")
    
    # Deployment status
    status: DeploymentStatus = Field(default=DeploymentStatus.PENDING, description="Deployment status")
    health_status: str = Field(default="unknown", description="Deployment health status")
    last_health_check: Optional[datetime] = Field(None, description="Last health check timestamp")
    
    # Governance and approval
    governance_approval_id: Optional[str] = Field(None, description="Governance approval ID")
    compliance_status: str = Field(default="pending", description="Compliance status")
    risk_assessment: RiskLevel = Field(default=RiskLevel.LOW, description="Deployment risk level")
    
    # Cost and resources
    cost_estimate: Optional[Decimal] = Field(None, ge=0, description="Estimated monthly cost")
    actual_cost: Decimal = Field(default=Decimal('0'), ge=0, description="Actual cost so far")
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description="Resource usage metrics")
    
    # Timeline
    deployment_date: Optional[datetime] = Field(None, description="Actual deployment date")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    scheduled_maintenance: Optional[datetime] = Field(None, description="Scheduled maintenance window")
    
    # Performance metrics
    response_time_p50: Optional[float] = Field(None, ge=0, description="50th percentile response time")
    response_time_p95: Optional[float] = Field(None, ge=0, description="95th percentile response time")
    response_time_p99: Optional[float] = Field(None, ge=0, description="99th percentile response time")
    throughput: Optional[float] = Field(None, ge=0, description="Requests per second")
    error_rate: Optional[float] = Field(None, ge=0, le=100, description="Error rate percentage")
    
    # Compliance and audit
    compliance_score: Optional[float] = Field(None, ge=0, le=100, description="Compliance score")
    audit_findings: List[str] = Field(default_factory=list, description="Audit findings")
    last_audit_date: Optional[datetime] = Field(None, description="Last audit date")
    next_audit_date: Optional[datetime] = Field(None, description="Next audit date")
    
    entity_type: EntityType = Field(default=EntityType.DEPLOYMENT)
    
    @property
    def is_production(self) -> bool:
        """Check if deployment is in production."""
        return self.environment.lower() == "production"
    
    @property
    def is_staging(self) -> bool:
        """Check if deployment is in staging."""
        return self.environment.lower() == "staging"
    
    @property
    def is_development(self) -> bool:
        """Check if deployment is in development."""
        return self.environment.lower() == "development"
    
    @property
    def requires_governance_approval(self) -> bool:
        """Check if deployment requires governance approval."""
        return self.is_production or (self.cost_estimate and self.cost_estimate > 1000)
    
    @property
    def is_healthy(self) -> bool:
        """Check if deployment is healthy."""
        return self.health_status.lower() == "healthy"
    
    @property
    def is_active(self) -> bool:
        """Check if deployment is active."""
        return self.status in [DeploymentStatus.ACTIVE, DeploymentStatus.SCALING]
    
    @property
    def cost_variance(self) -> Optional[Decimal]:
        """Calculate cost variance from estimate."""
        if self.cost_estimate is None:
            return None
        return self.actual_cost - self.cost_estimate
    
    @property
    def cost_variance_percentage(self) -> Optional[float]:
        """Calculate cost variance percentage."""
        if self.cost_estimate is None or self.cost_estimate == 0:
            return None
        variance = self.cost_variance
        if variance is None:
            return None
        return float((variance / self.cost_estimate) * 100)
    
    @property
    def uptime_percentage(self) -> Optional[float]:
        """Calculate deployment uptime percentage."""
        if not self.deployment_date:
            return None
        
        total_time = datetime.utcnow() - self.deployment_date
        if total_time.total_seconds() <= 0:
            return 100.0
        
        # This would be calculated from actual monitoring data in a real system
        # For demo purposes, return a mock value
        return 99.5

class AuditLog(BaseEntity):
    """Comprehensive audit log for governance and compliance."""
    user_id: str = Field(..., description="User ID who performed the action")
    session_id: Optional[str] = Field(None, description="User session ID")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of the resource affected")
    
    # Request details
    endpoint: str = Field(..., description="API endpoint accessed")
    method: str = Field(..., description="HTTP method used")
    ip_address: Optional[str] = Field(None, description="IP address of the request")
    user_agent: Optional[str] = Field(None, description="User agent of the request")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    
    # Action details
    details: Optional[Dict[str, Any]] = Field(None, description="Additional action details")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Request parameters")
    response_status: Optional[int] = Field(None, description="HTTP response status")
    response_size: Optional[int] = Field(None, description="Response size in bytes")
    
    # Governance and compliance
    compliance_impact: RiskLevel = Field(default=RiskLevel.LOW, description="Compliance impact level")
    governance_tier: GovernanceTier = Field(default=GovernanceTier.STANDARD, description="Governance tier")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk level")
    
    # Performance metrics
    response_time: Optional[float] = Field(None, ge=0, description="Response time in seconds")
    processing_time: Optional[float] = Field(None, ge=0, description="Processing time in seconds")
    database_queries: Optional[int] = Field(None, ge=0, description="Number of database queries")
    
    # Security and access
    authentication_method: Optional[str] = Field(None, description="Authentication method used")
    authorization_result: Optional[str] = Field(None, description="Authorization result")
    permissions_checked: List[str] = Field(default_factory=list, description="Permissions checked")
    access_granted: bool = Field(default=True, description="Whether access was granted")
    
    # Compliance tracking
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    audit_findings: List[str] = Field(default_factory=list, description="Audit findings")
    compliance_score: Optional[float] = Field(None, ge=0, le=100, description="Compliance score")
    
    # Error and exception handling
    error_type: Optional[str] = Field(None, description="Type of error if any")
    error_message: Optional[str] = Field(None, description="Error message if any")
    stack_trace: Optional[str] = Field(None, description="Stack trace if error occurred")
    
    # Metadata
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    business_context: Optional[str] = Field(None, description="Business context of the action")
    regulatory_context: Optional[str] = Field(None, description="Regulatory context of the action")
    
    entity_type: EntityType = Field(default=EntityType.AUDIT_LOG)
    
    @property
    def is_high_impact(self) -> bool:
        """Check if action has high compliance impact."""
        return self.compliance_impact in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    @property
    def requires_review(self) -> bool:
        """Check if action requires governance review."""
        return (
            self.is_high_impact or 
            self.governance_tier in [GovernanceTier.ENTERPRISE, GovernanceTier.RESTRICTED] or
            self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
    
    @property
    def is_error(self) -> bool:
        """Check if action resulted in an error."""
        return self.error_type is not None or (self.response_status and self.response_status >= 400)
    
    @property
    def is_slow(self) -> bool:
        """Check if action was slow."""
        if self.response_time is None:
            return False
        return self.response_time > 1.0  # Consider >1 second as slow
    
    @property
    def is_unauthorized(self) -> bool:
        """Check if action was unauthorized."""
        return not self.access_granted or (self.response_status and self.response_status == 403)
    
    @property
    def is_suspicious(self) -> bool:
        """Check if action is suspicious."""
        return (
            self.is_unauthorized or
            self.is_error or
            self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] or
            self.compliance_impact in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
