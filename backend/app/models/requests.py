"""
Enterprise Governance API - Request Models
Request models for all API endpoints with comprehensive validation.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

class RequestPriority(str, Enum):
    """Request priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class DeploymentEnvironment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    DEMO = "demo"

class ModelDeploymentRequest(BaseModel):
    """Request model for deploying AI models."""
    model_id: str = Field(..., description="ID of the model to deploy")
    deployment_name: str = Field(..., min_length=1, max_length=100, description="Deployment name")
    description: Optional[str] = Field(None, max_length=500, description="Deployment description")
    
    # Deployment configuration
    environment: DeploymentEnvironment = Field(..., description="Deployment environment")
    region: str = Field(..., description="Deployment region")
    availability_zone: Optional[str] = Field(None, description="Availability zone")
    instance_type: str = Field(..., description="Instance type for deployment")
    
    # Infrastructure configuration
    scaling_config: Dict[str, Any] = Field(default_factory=dict, description="Scaling configuration")
    monitoring_config: Dict[str, Any] = Field(default_factory=dict, description="Monitoring configuration")
    security_config: Dict[str, Any] = Field(default_factory=dict, description="Security configuration")
    network_config: Dict[str, Any] = Field(default_factory=dict, description="Network configuration")
    
    # Governance and compliance
    governance_tier: Optional[str] = Field(None, description="Governance tier for deployment")
    compliance_level: Optional[str] = Field(None, description="Compliance level required")
    risk_assessment: Optional[str] = Field(None, description="Risk assessment level")
    
    # Cost and resources
    cost_estimate: Optional[Decimal] = Field(None, ge=0, description="Estimated monthly cost")
    budget_allocation: Optional[str] = Field(None, description="Budget allocation source")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")
    
    # Timeline
    requested_deployment_date: Optional[datetime] = Field(None, description="Requested deployment date")
    maintenance_window: Optional[str] = Field(None, description="Preferred maintenance window")
    
    # Approval workflow
    requires_approval: bool = Field(default=True, description="Whether deployment requires approval")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    priority: RequestPriority = Field(default=RequestPriority.NORMAL, description="Request priority")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Deployment tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('deployment_name')
    def validate_deployment_name(cls, v):
        """Validate deployment name format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Deployment name can only contain alphanumeric characters, hyphens, and underscores")
        return v
    
    @validator('requested_deployment_date')
    def validate_deployment_date(cls, v):
        """Validate deployment date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Deployment date must be in the future")
        return v
    
    @validator('cost_estimate')
    def validate_cost_estimate(cls, v):
        """Validate cost estimate is reasonable."""
        if v and v > 100000:
            raise ValueError("Cost estimate cannot exceed $100,000")
        return v
    
    @root_validator
    def validate_production_deployment(cls, values):
        """Validate production deployment requirements."""
        environment = values.get('environment')
        cost_estimate = values.get('cost_estimate')
        
        if environment == DeploymentEnvironment.PRODUCTION:
            if not values.get('governance_tier'):
                raise ValueError("Production deployments require governance tier specification")
            
            if not values.get('compliance_level'):
                raise ValueError("Production deployments require compliance level specification")
            
            if cost_estimate and cost_estimate > 10000:
                values['requires_approval'] = True
        
        return values

class GovernanceConfigUpdateRequest(BaseModel):
    """Request model for updating governance configuration."""
    config_id: Optional[str] = Field(None, description="Configuration ID for updates")
    name: str = Field(..., min_length=1, max_length=100, description="Configuration name")
    description: Optional[str] = Field(None, max_length=500, description="Configuration description")
    
    # Governance settings
    governance_mode: str = Field(..., description="Governance mode")
    compliance_level: str = Field(..., description="Compliance level")
    risk_tolerance: str = Field(..., description="Risk tolerance level")
    
    # Access control settings
    require_approval: bool = Field(default=True, description="Whether approval is required")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    auto_approval_limit: Optional[Decimal] = Field(None, ge=0, description="Auto-approval cost limit")
    
    # Usage limits
    daily_request_limit: Optional[int] = Field(None, ge=0, description="Daily request limit")
    monthly_cost_limit: Optional[Decimal] = Field(None, ge=0, description="Monthly cost limit")
    concurrent_request_limit: Optional[int] = Field(None, ge=0, description="Concurrent request limit")
    
    # Compliance settings
    data_retention_days: Optional[int] = Field(None, ge=0, description="Data retention period")
    audit_logging_enabled: bool = Field(default=True, description="Whether audit logging is enabled")
    compliance_reporting_enabled: bool = Field(default=False, description="Whether compliance reporting is enabled")
    
    # Model provider settings
    allowed_providers: List[str] = Field(default_factory=list, description="Allowed model providers")
    self_hosted_allowed: bool = Field(default=False, description="Whether self-hosted models are allowed")
    cost_threshold_alerts: bool = Field(default=True, description="Whether cost threshold alerts are enabled")
    
    # Team settings
    default_team_governance_tier: str = Field(default="standard", description="Default governance tier for teams")
    team_budget_limits: Dict[str, Decimal] = Field(default_factory=dict, description="Team budget limits")
    team_model_quotas: Dict[str, int] = Field(default_factory=dict, description="Team model usage quotas")
    
    # Notification settings
    email_notifications_enabled: bool = Field(default=True, description="Whether email notifications are enabled")
    slack_notifications_enabled: bool = Field(default=False, description="Whether Slack notifications are enabled")
    webhook_notifications_enabled: bool = Field(default=False, description="Whether webhook notifications are enabled")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Configuration tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
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
        governance_mode = values.get('governance_mode')
        compliance_level = values.get('compliance_level')
        
        if governance_mode == "enterprise":
            if compliance_level != "enterprise":
                raise ValueError("Enterprise governance mode requires enterprise compliance level")
            
            if not values.get('compliance_reporting_enabled'):
                raise ValueError("Enterprise governance requires compliance reporting")
            
            if not values.get('audit_logging_enabled'):
                raise ValueError("Enterprise governance requires audit logging")
        
        return values

class AccessControlRequest(BaseModel):
    """Request model for managing access control policies."""
    policy_id: Optional[str] = Field(None, description="Policy ID for updates")
    name: str = Field(..., min_length=1, max_length=100, description="Policy name")
    description: Optional[str] = Field(None, max_length=500, description="Policy description")
    
    # Policy scope
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
    governance_tier: str = Field(..., description="Governance tier")
    requires_approval: bool = Field(default=False, description="Whether access requires approval")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    
    # Compliance
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    audit_frequency: str = Field(default="monthly", description="Audit frequency")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Policy tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('permissions')
    def validate_permissions(cls, v):
        """Validate permissions are not conflicting."""
        if not v:
            raise ValueError("At least one permission must be specified")
        return v
    
    @root_validator
    def validate_policy_scope(cls, values):
        """Validate policy scope is properly defined."""
        resource_type = values.get('resource_type')
        resource_id = values.get('resource_id')
        user_id = values.get('user_id')
        team_id = values.get('team_id')
        department = values.get('department')
        
        # At least one scope must be defined
        if not any([resource_id, user_id, team_id, department]):
            raise ValueError("Policy must define at least one scope (resource, user, team, or department)")
        
        return values

class ComplianceReportRequest(BaseModel):
    """Request model for generating compliance reports."""
    report_type: str = Field(..., description="Type of compliance report")
    scope: str = Field(..., description="Report scope (user, team, project, system)")
    entity_id: Optional[str] = Field(None, description="Entity ID for scoped reports")
    
    # Time period
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    granularity: str = Field(default="daily", description="Report granularity")
    
    # Compliance requirements
    compliance_frameworks: List[str] = Field(default_factory=list, description="Compliance frameworks to include")
    regulatory_requirements: List[str] = Field(default_factory=list, description="Regulatory requirements to include")
    audit_standards: List[str] = Field(default_factory=list, description="Audit standards to include")
    
    # Report content
    include_audit_logs: bool = Field(default=True, description="Include audit logs in report")
    include_governance_metrics: bool = Field(default=True, description="Include governance metrics")
    include_cost_analysis: bool = Field(default=True, description="Include cost analysis")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")
    
    # Output format
    output_format: str = Field(default="pdf", description="Output format (pdf, html, json, csv)")
    include_charts: bool = Field(default=True, description="Include charts and visualizations")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Report tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date."""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v
    
    @validator('start_date')
    def validate_start_date(cls, v):
        """Validate that start date is not too far in the past."""
        if v < datetime.utcnow() - timedelta(days=365):
            raise ValueError("Start date cannot be more than 1 year in the past")
        return v

class CostAnalysisRequest(BaseModel):
    """Request model for cost analysis and optimization."""
    analysis_type: str = Field(..., description="Type of cost analysis")
    scope: str = Field(..., description="Analysis scope (user, team, project, system)")
    entity_id: Optional[str] = Field(None, description="Entity ID for scoped analysis")
    
    # Time period
    start_date: datetime = Field(..., description="Analysis start date")
    end_date: datetime = Field(..., description="Analysis end date")
    comparison_period: Optional[str] = Field(None, description="Comparison period for trend analysis")
    
    # Cost breakdown
    include_provider_costs: bool = Field(default=True, description="Include provider costs")
    include_infrastructure_costs: bool = Field(default=True, description="Include infrastructure costs")
    include_operational_costs: bool = Field(default=True, description="Include operational costs")
    include_compliance_costs: bool = Field(default=True, description="Include compliance costs")
    
    # Analysis dimensions
    group_by: List[str] = Field(default_factory=list, description="Grouping dimensions")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Analysis filters")
    metrics: List[str] = Field(default_factory=list, description="Metrics to include")
    
    # Optimization
    include_optimization_recommendations: bool = Field(default=True, description="Include optimization recommendations")
    include_cost_forecasting: bool = Field(default=True, description="Include cost forecasting")
    include_budget_planning: bool = Field(default=True, description="Include budget planning")
    
    # Output format
    output_format: str = Field(default="json", description="Output format (json, csv, excel)")
    include_visualizations: bool = Field(default=True, description="Include visualizations")
    include_detailed_breakdown: bool = Field(default=True, description="Include detailed cost breakdown")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Analysis tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date."""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v
    
    @validator('start_date')
    def validate_start_date(cls, v):
        """Validate that start date is not too far in the past."""
        if v < datetime.utcnow() - timedelta(days=365):
            raise ValueError("Start date cannot be more than 1 year in the past")
        return v

class TeamCollaborationRequest(BaseModel):
    """Request model for team collaboration and resource sharing."""
    collaboration_type: str = Field(..., description="Type of collaboration")
    name: str = Field(..., min_length=1, max_length=100, description="Collaboration name")
    description: Optional[str] = Field(None, max_length=500, description="Collaboration description")
    
    # Team structure
    lead_team_id: str = Field(..., description="ID of the lead team")
    participating_team_ids: List[str] = Field(default_factory=list, description="Participating team IDs")
    stakeholder_team_ids: List[str] = Field(default_factory=list, description="Stakeholder team IDs")
    
    # Collaboration details
    objectives: List[str] = Field(default_factory=list, description="Collaboration objectives")
    deliverables: List[str] = Field(default_factory=list, description="Expected deliverables")
    timeline: Dict[str, datetime] = Field(default_factory=dict, description="Project timeline")
    
    # Resource sharing
    shared_resources: List[str] = Field(default_factory=list, description="Resources to be shared")
    access_levels: Dict[str, str] = Field(default_factory=dict, description="Access levels for each team")
    resource_quotas: Dict[str, Any] = Field(default_factory=dict, description="Resource quotas per team")
    
    # Governance and compliance
    governance_tier: str = Field(..., description="Governance tier for collaboration")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow to use")
    
    # Budget and cost sharing
    budget_allocation: Dict[str, Decimal] = Field(default_factory=dict, description="Budget allocation per team")
    cost_sharing_model: str = Field(default="proportional", description="Cost sharing model")
    cost_limits: Dict[str, Decimal] = Field(default_factory=dict, description="Cost limits per team")
    
    # Communication and coordination
    communication_channels: List[str] = Field(default_factory=list, description="Communication channels")
    meeting_schedule: Optional[str] = Field(None, description="Regular meeting schedule")
    reporting_frequency: str = Field(default="weekly", description="Reporting frequency")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Collaboration tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('participating_team_ids')
    def validate_team_ids(cls, v):
        """Validate that team IDs are unique."""
        if len(v) != len(set(v)):
            raise ValueError("Team IDs must be unique")
        return v
    
    @root_validator
    def validate_budget_allocation(cls, values):
        """Validate budget allocation consistency."""
        budget_allocation = values.get('budget_allocation', {})
        participating_teams = values.get('participating_team_ids', [])
        
        # Check that all participating teams have budget allocation
        for team_id in participating_teams:
            if team_id not in budget_allocation:
                raise ValueError(f"Budget allocation required for team: {team_id}")
        
        return values

class ModelUsageRequest(BaseModel):
    """Request model for AI model usage and inference."""
    model_id: str = Field(..., description="ID of the model to use")
    deployment_id: Optional[str] = Field(None, description="Specific deployment ID")
    
    # Input data
    input_data: Dict[str, Any] = Field(..., description="Input data for the model")
    input_format: Optional[str] = Field(None, description="Input data format")
    input_metadata: Optional[Dict[str, Any]] = Field(None, description="Input metadata")
    
    # Model parameters
    parameters: Optional[Dict[str, Any]] = Field(None, description="Model parameters")
    temperature: Optional[float] = Field(None, ge=0, le=2, description="Temperature for generation models")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Top-p sampling parameter")
    
    # Usage tracking
    user_id: str = Field(..., description="User ID making the request")
    team_id: Optional[str] = Field(None, description="Team ID for usage tracking")
    project_id: Optional[str] = Field(None, description="Project ID for usage tracking")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    
    # Priority and limits
    priority: RequestPriority = Field(default=RequestPriority.NORMAL, description="Request priority")
    timeout_seconds: Optional[int] = Field(None, ge=1, description="Request timeout in seconds")
    retry_count: Optional[int] = Field(None, ge=0, description="Number of retry attempts")
    
    # Compliance and governance
    compliance_tags: List[str] = Field(default_factory=list, description="Compliance tags")
    governance_tier: Optional[str] = Field(None, description="Governance tier for this request")
    requires_approval: bool = Field(default=False, description="Whether request requires approval")
    
    # Additional settings
    tags: List[str] = Field(default_factory=list, description="Request tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        """Validate temperature parameter."""
        if v is not None and (v < 0 or v > 2):
            raise ValueError("Temperature must be between 0 and 2")
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        """Validate max tokens parameter."""
        if v is not None and v < 1:
            raise ValueError("Max tokens must be at least 1")
        return v
    
    @validator('top_p')
    def validate_top_p(cls, v):
        """Validate top-p parameter."""
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Top-p must be between 0 and 1")
        return v

class ApprovalRequest(BaseModel):
    """Request model for governance approval workflows."""
    request_type: str = Field(..., description="Type of approval request")
    resource_type: str = Field(..., description="Type of resource being approved")
    resource_id: str = Field(..., description="ID of the resource being approved")
    
    # Request details
    title: str = Field(..., min_length=1, max_length=200, description="Request title")
    description: str = Field(..., min_length=1, max_length=1000, description="Request description")
    justification: str = Field(..., min_length=1, max_length=1000, description="Business justification")
    
    # Impact assessment
    impact_level: str = Field(..., description="Impact level of the request")
    risk_assessment: str = Field(..., description="Risk assessment")
    compliance_impact: str = Field(..., description="Compliance impact")
    cost_impact: Optional[Decimal] = Field(None, ge=0, description="Cost impact")
    
    # Approval workflow
    approvers: List[str] = Field(default_factory=list, description="List of approver user IDs")
    current_approver: Optional[str] = Field(None, description="Current approver in the workflow")
    approval_status: str = Field(default="pending", description="Current approval status")
    
    # Timeline
    requested_completion_date: Optional[datetime] = Field(None, description="Requested completion date")
    urgency_level: str = Field(default="normal", description="Urgency level")
    
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
