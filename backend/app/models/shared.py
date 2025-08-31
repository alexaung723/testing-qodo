"""
Shared models for cross-team collaboration and governance.
These models are used across multiple teams and services.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid

class EntityType(str, Enum):
    """Types of entities in the system."""
    USER = "user"
    PROJECT = "project"
    TASK = "task"
    MODEL = "model"
    DEPLOYMENT = "deployment"
    AUDIT_LOG = "audit_log"

class AccessLevel(str, Enum):
    """User access levels."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"

class ModelProvider(str, Enum):
    """Available model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    AWS = "aws"
    SELF_HOSTED = "self_hosted"

class BaseEntity(BaseModel):
    """Base entity with common fields for all shared models."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: str = Field(..., description="User ID who created the entity")
    updated_by: Optional[str] = Field(None, description="User ID who last updated the entity")
    entity_type: EntityType = Field(..., description="Type of entity")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        from_attributes = True
        use_enum_values = True

class User(BaseEntity):
    """User model with access control and governance."""
    email: str = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="User first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User last name")
    access_level: AccessLevel = Field(default=AccessLevel.READ, description="User access level")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    team_id: Optional[str] = Field(None, description="Team ID the user belongs to")
    department: Optional[str] = Field(None, description="User department")
    is_active: bool = Field(default=True, description="Whether user account is active")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    governance_tier: str = Field(default="standard", description="Governance tier for the user")
    
    entity_type: EntityType = Field(default=EntityType.USER)
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def can_deploy_models(self) -> bool:
        """Check if user can deploy models."""
        return "models:deploy" in self.permissions
    
    @property
    def can_manage_governance(self) -> bool:
        """Check if user can manage governance."""
        return "governance:write" in self.permissions

class Project(BaseEntity):
    """Project model with governance and access control."""
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    owner_id: str = Field(..., description="User ID who owns the project")
    team_ids: List[str] = Field(default_factory=list, description="Teams involved in the project")
    status: str = Field(default="active", description="Project status")
    governance_level: str = Field(default="standard", description="Governance level for the project")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")
    review_cycle: str = Field(default="monthly", description="Review cycle for the project")
    next_review_date: Optional[datetime] = Field(None, description="Next review date")
    
    entity_type: EntityType = Field(default=EntityType.PROJECT)
    
    @validator('next_review_date')
    def validate_review_date(cls, v):
        """Validate that review date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("Review date must be in the future")
        return v

class Task(BaseEntity):
    """Task model with governance and tracking."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    status: str = Field(default="todo", description="Task status")
    priority: str = Field(default="medium", description="Task priority")
    assignee_id: Optional[str] = Field(None, description="User ID assigned to the task")
    project_id: Optional[str] = Field(None, description="Project ID this task belongs to")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours to complete")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    governance_impact: str = Field(default="low", description="Governance impact level")
    compliance_notes: Optional[str] = Field(None, description="Compliance-related notes")
    
    entity_type: EntityType = Field(default=EntityType.TASK)
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until due date."""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.utcnow()
        return max(0, delta.days)

class SharedModel(BaseEntity):
    """Shared model for cross-team usage."""
    name: str = Field(..., min_length=1, max_length=100, description="Model name")
    version: str = Field(..., description="Model version")
    description: Optional[str] = Field(None, max_length=500, description="Model description")
    model_type: str = Field(..., description="Type of model (e.g., classification, generation)")
    provider: ModelProvider = Field(..., description="Model provider")
    endpoint_url: Optional[str] = Field(None, description="Model endpoint URL")
    api_key_required: bool = Field(default=True, description="Whether API key is required")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")
    cost_per_request: Optional[float] = Field(None, ge=0, description="Cost per request")
    governance_classification: str = Field(default="standard", description="Governance classification")
    compliance_tags: List[str] = Field(default_factory=list, description="Compliance tags")
    usage_limits: Dict[str, Any] = Field(default_factory=dict, description="Usage limits")
    team_ownership: List[str] = Field(default_factory=list, description="Teams that own this model")
    
    entity_type: EntityType = Field(default=EntityType.MODEL)
    
    @validator('endpoint_url')
    def validate_endpoint_url(cls, v, values):
        """Validate endpoint URL for self-hosted models."""
        if values.get('provider') == ModelProvider.SELF_HOSTED and not v:
            raise ValueError("Endpoint URL is required for self-hosted models")
        return v

class Deployment(BaseEntity):
    """Model deployment with governance controls."""
    model_id: str = Field(..., description="ID of the deployed model")
    environment: str = Field(..., description="Deployment environment")
    region: str = Field(..., description="Deployment region")
    instance_type: str = Field(..., description="Instance type for deployment")
    scaling_config: Dict[str, Any] = Field(default_factory=dict, description="Scaling configuration")
    monitoring_config: Dict[str, Any] = Field(default_factory=dict, description="Monitoring configuration")
    governance_approval_id: Optional[str] = Field(None, description="Governance approval ID")
    compliance_status: str = Field(default="pending", description="Compliance status")
    cost_estimate: Optional[float] = Field(None, ge=0, description="Estimated monthly cost")
    deployment_date: Optional[datetime] = Field(None, description="Actual deployment date")
    
    entity_type: EntityType = Field(default=EntityType.DEPLOYMENT)
    
    @property
    def is_production(self) -> bool:
        """Check if deployment is in production."""
        return self.environment.lower() == "production"
    
    @property
    def requires_governance_approval(self) -> bool:
        """Check if deployment requires governance approval."""
        return self.is_production or self.cost_estimate and self.cost_estimate > 1000

class AuditLog(BaseEntity):
    """Audit log for governance and compliance."""
    user_id: str = Field(..., description="User ID who performed the action")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of the resource affected")
    endpoint: str = Field(..., description="API endpoint accessed")
    ip_address: Optional[str] = Field(None, description="IP address of the request")
    user_agent: Optional[str] = Field(None, description="User agent of the request")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional action details")
    compliance_impact: str = Field(default="low", description="Compliance impact level")
    governance_tier: str = Field(default="standard", description="Governance tier for the action")
    
    entity_type: EntityType = Field(default=EntityType.AUDIT_LOG)
    
    @property
    def is_high_impact(self) -> bool:
        """Check if action has high compliance impact."""
        return self.compliance_impact.lower() == "high"
    
    @property
    def requires_review(self) -> bool:
        """Check if action requires governance review."""
        return self.is_high_impact or self.governance_tier == "critical"

class Team(BaseEntity):
    """Team model for cross-team collaboration."""
    name: str = Field(..., min_length=1, max_length=100, description="Team name")
    description: Optional[str] = Field(None, max_length=500, description="Team description")
    lead_id: str = Field(..., description="User ID of the team lead")
    member_ids: List[str] = Field(default_factory=list, description="Team member IDs")
    department: str = Field(..., description="Department the team belongs to")
    governance_tier: str = Field(default="standard", description="Governance tier for the team")
    compliance_requirements: List[str] = Field(default_factory=list, description="Team compliance requirements")
    review_cycle: str = Field(default="quarterly", description="Team review cycle")
    next_review_date: Optional[datetime] = Field(None, description="Next review date")
    budget_limit: Optional[float] = Field(None, ge=0, description="Monthly budget limit")
    model_usage_quota: Optional[int] = Field(None, ge=0, description="Monthly model usage quota")
    
    entity_type: EntityType = Field(default=EntityType.USER)  # Reusing USER type for teams
    
    @property
    def member_count(self) -> int:
        """Get the number of team members."""
        return len(self.member_ids) + 1  # +1 for team lead
    
    @property
    def is_over_budget(self) -> bool:
        """Check if team is over budget (placeholder for demo)."""
        return False  # In real app, this would check actual spending
