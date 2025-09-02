"""
Enterprise Governance API - Governance Models
Models for governance policies, access control, and compliance management.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid

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
    UNDER_REVIEW = "under_review"

class PolicyStatus(str, Enum):
    """Policy status values."""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class ComplianceFramework(str, Enum):
    """Compliance frameworks."""
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    NIST = "nist"
    CUSTOM = "custom"

class GovernanceConfig(BaseModel):
    """Governance configuration for the system."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Configuration identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Configuration name")
    description: Optional[str] = Field(None, max_length=500, description="Configuration description")
    
    # Governance settings
    governance_tier: GovernanceTier = Field(default=GovernanceTier.STANDARD, description="Governance tier")
    compliance_level: ComplianceLevel = Field(default=ComplianceLevel.INTERMEDIATE, description="Compliance level")
    risk_tolerance: RiskLevel = Field(default=RiskLevel.MEDIUM, description="Risk tolerance level")
    
    # Access control settings
    require_approval: bool = Field(default=True, description="Whether approval is required")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    auto_approval_limit: Optional[Decimal] = Field(None, ge=0, description="Auto-approval cost limit")
    require_mfa: bool = Field(default=False, description="Whether MFA is required")
    require_strong_passwords: bool = Field(default=True, description="Whether strong passwords are required")
    
    # Usage limits
    daily_request_limit: Optional[int] = Field(None, ge=0, description="Daily request limit")
    monthly_cost_limit: Optional[Decimal] = Field(None, ge=0, description="Monthly cost limit")
    concurrent_request_limit: Optional[int] = Field(None, ge=0, description="Concurrent request limit")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Compliance settings
    data_retention_days: int = Field(default=90, description="Data retention period")
    audit_logging_enabled: bool = Field(default=True, description="Whether audit logging is enabled")
    compliance_reporting_enabled: bool = Field(default=False, description="Whether compliance reporting is enabled")
    data_encryption_required: bool = Field(default=True, description="Whether data encryption is required")
    
    # Model provider settings
    allowed_providers: List[str] = Field(default_factory=list, description="Allowed model providers")
    self_hosted_allowed: bool = Field(default=False, description="Whether self-hosted models are allowed")
    cost_threshold_alerts: bool = Field(default=True, description="Whether cost threshold alerts are enabled")
    provider_rotation_enabled: bool = Field(default=False, description="Whether provider rotation is enabled")
    
    # Team settings
    default_team_governance_tier: GovernanceTier = Field(default=GovernanceTier.STANDARD, description="Default governance tier for teams")
    team_budget_limits: Dict[str, Decimal] = Field(default_factory=dict, description="Team budget limits")
    team_model_quotas: Dict[str, int] = Field(default_factory=dict, description="Team model usage quotas")
    max_team_members: int = Field(default=50, description="Maximum team members")
    
    # Notification settings
    email_notifications_enabled: bool = Field(default=True, description="Whether email notifications are enabled")
    slack_notifications_enabled: bool = Field(default=False, description="Whether Slack notifications are enabled")
    webhook_notifications_enabled: bool = Field(default=False, description="Whether webhook notifications are enabled")
    notification_webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    
    # Review and audit settings
    review_cycle: str = Field(default="quarterly", description="Review cycle")
    audit_frequency: str = Field(default="monthly", description="Audit frequency")
    compliance_review_frequency: str = Field(default="monthly", description="Compliance review frequency")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Configuration tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the configuration")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the configuration")
    
    @validator('auto_approval_limit')
    def validate_auto_approval_limit(cls, v):
        """Validate auto approval limit is reasonable."""
        if v and v > 10000:
            raise ValueError("Auto approval limit cannot exceed $10,000")
        return v
    
    @validator('monthly_cost_limit')
    def validate_monthly_cost_limit(cls, v):
        """Validate monthly cost limit is reasonable."""
        if v and v > 1000000:
            raise ValueError("Monthly cost limit cannot exceed $1,000,000")
        return v
    
    @root_validator
    def validate_enterprise_governance(cls, values):
        """Validate enterprise governance requirements."""
        governance_tier = values.get('governance_tier')
        compliance_level = values.get('compliance_level')
        
        if governance_tier == GovernanceTier.ENTERPRISE:
            if compliance_level != ComplianceLevel.ENTERPRISE:
                raise ValueError("Enterprise governance tier requires enterprise compliance level")
            
            if not values.get('compliance_reporting_enabled'):
                raise ValueError("Enterprise governance requires compliance reporting")
            
            if not values.get('audit_logging_enabled'):
                raise ValueError("Enterprise governance requires audit logging")
            
            if not values.get('data_encryption_required'):
                raise ValueError("Enterprise governance requires data encryption")
        
        if governance_tier == GovernanceTier.RESTRICTED:
            if not values.get('require_mfa'):
                raise ValueError("Restricted governance tier requires MFA")
            
            if not values.get('require_strong_passwords'):
                raise ValueError("Restricted governance tier requires strong passwords")
        
        return values

class AccessControl(BaseModel):
    """Access control policy for resources."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Policy identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Policy name")
    description: Optional[str] = Field(None, max_length=500, description="Policy description")
    
    # Policy scope
    resource_type: str = Field(..., description="Type of resource being controlled")
    resource_id: Optional[str] = Field(None, description="Specific resource ID")
    user_id: Optional[str] = Field(None, description="Specific user ID")
    team_id: Optional[str] = Field(None, description="Specific team ID")
    department: Optional[str] = Field(None, description="Specific department")
    organization: Optional[str] = Field(None, description="Specific organization")
    
    # Permissions
    permissions: List[str] = Field(default_factory=list, description="Allowed permissions")
    denied_permissions: List[str] = Field(default_factory=list, description="Denied permissions")
    conditional_permissions: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Conditional permissions")
    
    # Conditions
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Access conditions")
    time_restrictions: Optional[Dict[str, Any]] = Field(None, description="Time-based restrictions")
    ip_restrictions: Optional[List[str]] = Field(None, description="IP address restrictions")
    device_restrictions: Optional[List[str]] = Field(None, description="Device restrictions")
    location_restrictions: Optional[List[str]] = Field(None, description="Location restrictions")
    
    # Governance
    governance_tier: GovernanceTier = Field(..., description="Governance tier")
    requires_approval: bool = Field(default=False, description="Whether access requires approval")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    approval_expiry_hours: Optional[int] = Field(None, ge=1, description="Approval expiry time in hours")
    
    # Compliance
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    audit_frequency: str = Field(default="monthly", description="Audit frequency")
    compliance_tags: List[str] = Field(default_factory=list, description="Compliance tags")
    
    # Policy lifecycle
    status: PolicyStatus = Field(default=PolicyStatus.DRAFT, description="Policy status")
    effective_date: Optional[datetime] = Field(None, description="Policy effective date")
    expiry_date: Optional[datetime] = Field(None, description="Policy expiry date")
    review_date: Optional[datetime] = Field(None, description="Next review date")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Policy tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the policy")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the policy")
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permissions are not conflicting."""
        if not v:
            raise ValueError("At least one permission must be specified")
        return v
    
    @validator('effective_date')
    def validate_effective_date(cls, v):
        """Validate effective date is not in the past."""
        if v and v <= datetime.utcnow():
            raise ValueError("Effective date must be in the future")
        return v
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        """Validate expiry date is after effective date."""
        if v and 'effective_date' in values and values['effective_date']:
            if v <= values['effective_date']:
                raise ValueError("Expiry date must be after effective date")
        return v
    
    @root_validator
    def validate_policy_scope(cls, values):
        """Validate policy scope is properly defined."""
        resource_type = values.get('resource_type')
        resource_id = values.get('resource_id')
        user_id = values.get('user_id')
        team_id = values.get('team_id')
        department = values.get('department')
        organization = values.get('organization')
        
        # At least one scope must be defined
        if not any([resource_id, user_id, team_id, department, organization]):
            raise ValueError("Policy must define at least one scope (resource, user, team, department, or organization)")
        
        return values
    
    @property
    def is_active(self) -> bool:
        """Check if policy is active."""
        if self.status != PolicyStatus.ACTIVE:
            return False
        
        if self.effective_date and datetime.utcnow() < self.effective_date:
            return False
        
        if self.expiry_date and datetime.utcnow() > self.expiry_date:
            return False
        
        return True
    
    @property
    def requires_review(self) -> bool:
        """Check if policy requires review."""
        if not self.review_date:
            return False
        
        return datetime.utcnow() >= self.review_date
    
    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until policy expires."""
        if not self.expiry_date:
            return None
        
        delta = self.expiry_date - datetime.utcnow()
        return max(0, delta.days)

class UsageMetrics(BaseModel):
    """Usage metrics for governance and compliance tracking."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Metrics identifier")
    entity_id: str = Field(..., description="Entity ID (user, team, project)")
    entity_type: str = Field(..., description="Entity type")
    
    # Usage metrics
    total_requests: int = Field(default=0, ge=0, description="Total number of requests")
    successful_requests: int = Field(default=0, ge=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, ge=0, description="Number of failed requests")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens processed")
    
    # Cost metrics
    total_cost: Decimal = Field(default=Decimal('0'), ge=0, description="Total cost")
    cost_by_provider: Dict[str, Decimal] = Field(default_factory=dict, description="Cost breakdown by provider")
    cost_by_service: Dict[str, Decimal] = Field(default_factory=dict, description="Cost breakdown by service")
    cost_by_model: Dict[str, Decimal] = Field(default_factory=dict, description="Cost breakdown by model")
    
    # Performance metrics
    average_response_time: Optional[float] = Field(None, ge=0, description="Average response time")
    response_time_p50: Optional[float] = Field(None, ge=0, description="50th percentile response time")
    response_time_p95: Optional[float] = Field(None, ge=0, description="95th percentile response time")
    response_time_p99: Optional[float] = Field(None, ge=0, description="99th percentile response time")
    
    # Error metrics
    error_rate: Optional[float] = Field(None, ge=0, le=100, description="Error rate percentage")
    error_by_type: Dict[str, int] = Field(default_factory=dict, description="Error count by type")
    retry_count: int = Field(default=0, ge=0, description="Total retry attempts")
    
    # Compliance metrics
    compliance_score: Optional[float] = Field(None, ge=0, le=100, description="Compliance score")
    governance_violations: int = Field(default=0, ge=0, description="Number of governance violations")
    policy_violations: int = Field(default=0, ge=0, description="Number of policy violations")
    
    # Time period
    period_start: datetime = Field(..., description="Period start timestamp")
    period_end: datetime = Field(..., description="Period end timestamp")
    period_type: str = Field(..., description="Period type (hourly, daily, weekly, monthly)")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Metrics tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @validator('period_end')
    def validate_period_end(cls, v, values):
        """Validate period end is after period start."""
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError("Period end must be after period start")
        return v
    
    @property
    def success_rate(self) -> Optional[float]:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return None
        
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> Optional[float]:
        """Calculate failure rate percentage."""
        if self.total_requests == 0:
            return None
        
        return (self.failed_requests / self.total_requests) * 100
    
    @property
    def cost_per_request(self) -> Optional[Decimal]:
        """Calculate cost per request."""
        if self.total_requests == 0:
            return None
        
        return self.total_cost / self.total_requests
    
    @property
    def cost_per_token(self) -> Optional[Decimal]:
        """Calculate cost per token."""
        if self.total_tokens == 0:
            return None
        
        return self.total_cost / self.total_tokens
    
    @property
    def period_duration_hours(self) -> float:
        """Calculate period duration in hours."""
        delta = self.period_end - self.period_start
        return delta.total_seconds() / 3600

class ComplianceRequirement(BaseModel):
    """Compliance requirement for governance."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Requirement identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Requirement name")
    description: str = Field(..., min_length=1, max_length=1000, description="Requirement description")
    
    # Compliance details
    framework: ComplianceFramework = Field(..., description="Compliance framework")
    requirement_id: str = Field(..., description="Framework requirement ID")
    requirement_type: str = Field(..., description="Type of requirement")
    category: str = Field(..., description="Requirement category")
    
    # Risk and impact
    risk_level: RiskLevel = Field(..., description="Risk level")
    impact_level: str = Field(..., description="Impact level")
    business_criticality: str = Field(..., description="Business criticality")
    
    # Implementation
    implementation_status: str = Field(default="not_started", description="Implementation status")
    implementation_date: Optional[datetime] = Field(None, description="Implementation date")
    implementation_notes: Optional[str] = Field(None, description="Implementation notes")
    
    # Validation
    validation_status: str = Field(default="not_validated", description="Validation status")
    validation_date: Optional[datetime] = Field(None, description="Validation date")
    validation_method: Optional[str] = Field(None, description="Validation method")
    validation_evidence: List[str] = Field(default_factory=list, description="Validation evidence")
    
    # Monitoring
    monitoring_frequency: str = Field(default="monthly", description="Monitoring frequency")
    last_monitoring_date: Optional[datetime] = Field(None, description="Last monitoring date")
    next_monitoring_date: Optional[datetime] = Field(None, description="Next monitoring date")
    
    # Compliance score
    compliance_score: Optional[float] = Field(None, ge=0, le=100, description="Compliance score")
    compliance_status: str = Field(default="unknown", description="Compliance status")
    
    # Dependencies
    dependencies: List[str] = Field(default_factory=list, description="Dependent requirement IDs")
    dependent_on: List[str] = Field(default_factory=list, description="Requirements this depends on")
    
    # Additional information
    tags: List[str] = Field(default_factory=list, description="Requirement tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the requirement")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the requirement")
    
    @validator('compliance_score')
    def validate_compliance_score(cls, v):
        """Validate compliance score is within range."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Compliance score must be between 0 and 100")
        return v
    
    @validator('next_monitoring_date')
    def validate_next_monitoring_date(cls, v):
        """Validate next monitoring date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Next monitoring date must be in the future")
        return v
    
    @property
    def is_compliant(self) -> bool:
        """Check if requirement is compliant."""
        if self.compliance_score is None:
            return False
        
        return self.compliance_score >= 80  # 80% threshold for compliance
    
    @property
    def is_implemented(self) -> bool:
        """Check if requirement is implemented."""
        return self.implementation_status == "completed"
    
    @property
    def is_validated(self) -> bool:
        """Check if requirement is validated."""
        return self.validation_status == "validated"
    
    @property
    def requires_monitoring(self) -> bool:
        """Check if requirement requires monitoring."""
        if not self.next_monitoring_date:
            return False
        
        return datetime.utcnow() >= self.next_monitoring_date
    
    @property
    def days_until_monitoring(self) -> Optional[int]:
        """Calculate days until next monitoring."""
        if not self.next_monitoring_date:
            return None
        
        delta = self.next_monitoring_date - datetime.utcnow()
        return max(0, delta.days)

class GovernanceApproval(BaseModel):
    """Governance approval for high-impact changes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Approval identifier")
    request_type: str = Field(..., description="Type of approval request")
    resource_type: str = Field(..., description="Type of resource being approved")
    resource_id: str = Field(..., description="ID of the resource being approved")
    
    # Request details
    title: str = Field(..., min_length=1, max_length=200, description="Request title")
    description: str = Field(..., min_length=1, max_length=1000, description="Request description")
    justification: str = Field(..., min_length=1, max_length=1000, description="Business justification")
    
    # Impact assessment
    impact_level: str = Field(..., description="Impact level of the request")
    risk_assessment: RiskLevel = Field(..., description="Risk assessment")
    compliance_impact: str = Field(..., description="Compliance impact")
    cost_impact: Optional[Decimal] = Field(None, ge=0, description="Cost impact")
    security_impact: str = Field(..., description="Security impact")
    
    # Approval workflow
    requester_id: str = Field(..., description="User ID of the requester")
    approvers: List[str] = Field(..., description="List of approver user IDs")
    current_approver: Optional[str] = Field(None, description="Current approver in the workflow")
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Current approval status")
    
    # Timeline
    requested_completion_date: Optional[datetime] = Field(None, description="Requested completion date")
    urgency_level: str = Field(default="normal", description="Urgency level")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Approval history
    approval_history: List[Dict[str, Any]] = Field(default_factory=list, description="Approval history")
    approval_notes: List[str] = Field(default_factory=list, description="Approval notes")
    
    # Governance
    governance_tier: GovernanceTier = Field(..., description="Governance tier")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    risk_mitigation: Optional[str] = Field(None, description="Risk mitigation plan")
    
    # Additional information
    attachments: List[str] = Field(default_factory=list, description="Attachment file IDs")
    references: List[str] = Field(default_factory=list, description="Reference document IDs")
    tags: List[str] = Field(default_factory=list, description="Request tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('requested_completion_date')
    def validate_completion_date(cls, v):
        """Validate that completion date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Completion date must be in the future")
        return v
    
    @validator('approvers')
    def validate_approvers(cls, v):
        """Validate that approvers are specified."""
        if not v:
            raise ValueError("At least one approver must be specified")
        return v
    
    @property
    def is_approved(self) -> bool:
        """Check if request is approved."""
        return self.approval_status == ApprovalStatus.APPROVED
    
    @property
    def is_rejected(self) -> bool:
        """Check if request is rejected."""
        return self.approval_status == ApprovalStatus.REJECTED
    
    @property
    def is_pending(self) -> bool:
        """Check if request is pending."""
        return self.approval_status == ApprovalStatus.PENDING
    
    @property
    def is_expired(self) -> bool:
        """Check if request is expired."""
        if not self.requested_completion_date:
            return False
        
        return datetime.utcnow() > self.requested_completion_date
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until completion date."""
        if not self.requested_completion_date:
            return None
        
        delta = self.requested_completion_date - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def is_high_impact(self) -> bool:
        """Check if request has high impact."""
        return self.impact_level.lower() in ["high", "critical"]
    
    @property
    def is_high_risk(self) -> bool:
        """Check if request has high risk."""
        return self.risk_assessment in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    @property
    def requires_urgent_attention(self) -> bool:
        """Check if request requires urgent attention."""
        if self.urgency_level.lower() == "urgent":
            return True
        
        if self.days_remaining is not None and self.days_remaining <= 3:
            return True
        
        return False
