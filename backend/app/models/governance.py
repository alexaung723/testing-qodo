"""
Governance models for access control, usage limits, and compliance.
These models ensure consistent governance across teams.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum

class GovernanceTier(str, Enum):
    """Governance tiers for different levels of control."""
    STANDARD = "standard"
    ENHANCED = "enhanced"
    CRITICAL = "critical"
    RESTRICTED = "restricted"

class ComplianceLevel(str, Enum):
    """Compliance levels for different requirements."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class ModelAccessLevel(str, Enum):
    """Access levels for model usage."""
    READ_ONLY = "read_only"
    LIMITED = "limited"
    STANDARD = "standard"
    UNRESTRICTED = "unrestricted"

class GovernanceConfig(BaseModel):
    """Configuration for governance policies."""
    id: str = Field(..., description="Configuration identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Configuration name")
    description: Optional[str] = Field(None, max_length=500, description="Configuration description")
    governance_tier: GovernanceTier = Field(default=GovernanceTier.STANDARD, description="Governance tier")
    compliance_level: ComplianceLevel = Field(default=ComplianceLevel.BASIC, description="Compliance level")
    enabled: bool = Field(default=True, description="Whether configuration is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the configuration")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the configuration")
    
    # Access control settings
    require_approval: bool = Field(default=False, description="Whether approval is required")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    auto_approval_limit: Optional[float] = Field(None, ge=0, description="Auto-approval cost limit")
    
    # Usage limits
    daily_request_limit: Optional[int] = Field(None, ge=0, description="Daily request limit")
    monthly_cost_limit: Optional[float] = Field(None, ge=0, description="Monthly cost limit")
    concurrent_request_limit: Optional[int] = Field(None, ge=0, description="Concurrent request limit")
    
    # Compliance settings
    data_retention_days: Optional[int] = Field(None, ge=0, description="Data retention period in days")
    audit_logging_enabled: bool = Field(default=True, description="Whether audit logging is enabled")
    compliance_reporting: bool = Field(default=False, description="Whether compliance reporting is enabled")
    
    # Model provider settings
    allowed_providers: List[str] = Field(default_factory=list, description="Allowed model providers")
    self_hosted_allowed: bool = Field(default=False, description="Whether self-hosted models are allowed")
    cost_threshold_alerts: bool = Field(default=True, description="Whether cost threshold alerts are enabled")
    
    @validator('auto_approval_limit')
    def validate_auto_approval_limit(cls, v, values):
        """Validate auto approval limit is reasonable."""
        if v and v > 10000:
            raise ValueError("Auto approval limit cannot exceed $10,000")
        return v
    
    @validator('monthly_cost_limit')
    def validate_monthly_cost_limit(cls, v, values):
        """Validate monthly cost limit is reasonable."""
        if v and v > 100000:
            raise ValueError("Monthly cost limit cannot exceed $100,000")
        return v

class AccessControl(BaseModel):
    """Access control policy for resources."""
    id: str = Field(..., description="Access control identifier")
    resource_type: str = Field(..., description="Type of resource being controlled")
    resource_id: Optional[str] = Field(None, description="Specific resource ID")
    user_id: Optional[str] = Field(None, description="Specific user ID")
    team_id: Optional[str] = Field(None, description="Specific team ID")
    department: Optional[str] = Field(None, description="Specific department")
    
    # Permissions
    permissions: List[str] = Field(default_factory=list, description="Allowed permissions")
    denied_permissions: List[str] = Field(default_factory=list, description="Denied permissions")
    
    # Conditions
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Access conditions")
    time_restrictions: Optional[Dict[str, Any]] = Field(None, description="Time-based restrictions")
    ip_restrictions: Optional[List[str]] = Field(None, description="IP address restrictions")
    
    # Governance
    governance_tier: GovernanceTier = Field(default=GovernanceTier.STANDARD, description="Governance tier")
    requires_approval: bool = Field(default=False, description="Whether access requires approval")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the access control")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the access control")
    is_active: bool = Field(default=True, description="Whether access control is active")
    
    @property
    def is_restrictive(self) -> bool:
        """Check if access control is restrictive."""
        return len(self.denied_permissions) > len(self.permissions)
    
    @property
    def requires_governance_review(self) -> bool:
        """Check if access control requires governance review."""
        return self.governance_tier in [GovernanceTier.CRITICAL, GovernanceTier.RESTRICTED]

class UsageMetrics(BaseModel):
    """Usage metrics for governance and cost control."""
    id: str = Field(..., description="Usage metrics identifier")
    user_id: str = Field(..., description="User ID for the metrics")
    team_id: Optional[str] = Field(None, description="Team ID for the metrics")
    department: Optional[str] = Field(None, description="Department for the metrics")
    
    # Time period
    period_start: datetime = Field(..., description="Start of the metrics period")
    period_end: datetime = Field(..., description="End of the metrics period")
    period_type: str = Field(..., description="Type of period (daily, weekly, monthly)")
    
    # Usage counts
    total_requests: int = Field(default=0, ge=0, description="Total number of requests")
    successful_requests: int = Field(default=0, ge=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, ge=0, description="Number of failed requests")
    
    # Cost metrics
    total_cost: float = Field(default=0.0, ge=0, description="Total cost for the period")
    average_cost_per_request: float = Field(default=0.0, ge=0, description="Average cost per request")
    cost_breakdown: Dict[str, float] = Field(default_factory=dict, description="Cost breakdown by provider")
    
    # Performance metrics
    average_response_time: float = Field(default=0.0, ge=0, description="Average response time in seconds")
    p95_response_time: float = Field(default=0.0, ge=0, description="95th percentile response time")
    p99_response_time: float = Field(default=0.0, ge=0, description="99th percentile response time")
    
    # Model usage
    models_used: List[str] = Field(default_factory=list, description="Models used during the period")
    provider_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by provider")
    
    # Governance metrics
    governance_violations: int = Field(default=0, ge=0, description="Number of governance violations")
    compliance_score: float = Field(default=100.0, ge=0, le=100, description="Compliance score")
    review_required: bool = Field(default=False, description="Whether review is required")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    @property
    def is_over_limit(self) -> bool:
        """Check if usage is over any configured limits."""
        # This would check against governance config limits
        return False  # Placeholder for demo

class ComplianceRequirement(BaseModel):
    """Compliance requirement for governance."""
    id: str = Field(..., description="Compliance requirement identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Requirement name")
    description: str = Field(..., min_length=1, max_length=1000, description="Requirement description")
    category: str = Field(..., description="Requirement category")
    level: ComplianceLevel = Field(..., description="Compliance level")
    
    # Requirements
    mandatory: bool = Field(default=True, description="Whether requirement is mandatory")
    frequency: str = Field(default="ongoing", description="Compliance frequency")
    review_cycle: str = Field(default="annual", description="Review cycle")
    
    # Governance
    governance_tier: GovernanceTier = Field(..., description="Governance tier")
    risk_level: str = Field(default="low", description="Risk level")
    impact_score: int = Field(default=1, ge=1, le=10, description="Impact score (1-10)")
    
    # Documentation
    documentation_url: Optional[str] = Field(None, description="URL to requirement documentation")
    examples: List[str] = Field(default_factory=list, description="Example implementations")
    checklist: List[str] = Field(default_factory=list, description="Compliance checklist")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the requirement")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the requirement")
    is_active: bool = Field(default=True, description="Whether requirement is active")
    
    @property
    def is_critical(self) -> bool:
        """Check if requirement is critical."""
        return self.governance_tier == GovernanceTier.CRITICAL or self.impact_score >= 8
    
    @property
    def requires_annual_review(self) -> bool:
        """Check if requirement requires annual review."""
        return self.review_cycle.lower() in ["annual", "yearly"]

class GovernanceApproval(BaseModel):
    """Governance approval for high-impact changes."""
    id: str = Field(..., description="Approval identifier")
    request_type: str = Field(..., description="Type of approval request")
    resource_type: str = Field(..., description="Type of resource being approved")
    resource_id: str = Field(..., description="ID of the resource being approved")
    
    # Request details
    requested_by: str = Field(..., description="User ID who requested approval")
    requested_at: datetime = Field(..., description="When approval was requested")
    justification: str = Field(..., min_length=1, max_length=1000, description="Justification for the request")
    impact_assessment: str = Field(..., min_length=1, max_length=1000, description="Impact assessment")
    
    # Approval workflow
    approvers: List[str] = Field(default_factory=list, description="List of approver user IDs")
    current_approver: Optional[str] = Field(None, description="Current approver in the workflow")
    approval_status: str = Field(default="pending", description="Current approval status")
    
    # Governance
    governance_tier: GovernanceTier = Field(..., description="Governance tier for the approval")
    compliance_impact: str = Field(default="low", description="Compliance impact level")
    risk_assessment: str = Field(default="low", description="Risk assessment")
    
    # Timeline
    requested_completion_date: Optional[datetime] = Field(None, description="Requested completion date")
    approved_at: Optional[datetime] = Field(None, description="When approval was granted")
    completed_at: Optional[datetime] = Field(None, description="When request was completed")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @property
    def is_approved(self) -> bool:
        """Check if approval has been granted."""
        return self.approval_status.lower() == "approved"
    
    @property
    def is_pending(self) -> bool:
        """Check if approval is still pending."""
        return self.approval_status.lower() == "pending"
    
    @property
    def is_urgent(self) -> bool:
        """Check if approval is urgent."""
        if not self.requested_completion_date:
            return False
        days_remaining = (self.requested_completion_date - datetime.utcnow()).days
        return days_remaining <= 3
