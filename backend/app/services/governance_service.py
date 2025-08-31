"""
Governance service for managing access control, usage limits, and compliance.
This service ensures consistent governance across teams.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.shared import User, Team, SharedModel
from app.models.governance import (
    GovernanceConfig, 
    AccessControl, 
    UsageMetrics, 
    ComplianceRequirement,
    GovernanceApproval
)

logger = logging.getLogger(__name__)

class DeploymentCheckResult:
    """Result of a deployment limit check."""
    
    def __init__(self, allowed: bool, reason: str = "", usage_consumed: float = 0.0):
        self.allowed = allowed
        self.reason = reason
        self.usage_consumed = usage_consumed

class GovernanceService:
    """Service for managing governance policies and compliance."""
    
    def __init__(self):
        """Initialize governance service."""
        self._governance_configs = self._initialize_governance_configs()
        self._access_controls = self._initialize_access_controls()
        self._compliance_requirements = self._initialize_compliance_requirements()
        self._approvals = {}
        self._approval_counter = 1
    
    async def get_config(self) -> GovernanceConfig:
        """Get current governance configuration."""
        # In a real app, this would get the active configuration
        # For demo purposes, return the first config
        return self._governance_configs[0] if self._governance_configs else None
    
    async def update_config(self, config_update: GovernanceConfig, user_id: str) -> GovernanceConfig:
        """Update governance configuration."""
        logger.info(f"User {user_id} updating governance configuration")
        
        # Validate configuration update
        validation_result = self.validate_config_update(config_update)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid configuration: {validation_result.errors}")
        
        # Check if user has permission to update config
        user = await self._get_user(user_id)
        if not user or not user.can_manage_governance:
            raise ValueError("User does not have permission to update governance configuration")
        
        # Update configuration
        config_update.id = str(len(self._governance_configs) + 1)
        config_update.updated_by = user_id
        config_update.updated_at = datetime.utcnow()
        
        self._governance_configs.append(config_update)
        
        logger.info(f"Governance configuration updated by user {user_id}")
        return config_update
    
    def validate_config_update(self, config: GovernanceConfig) -> Dict[str, Any]:
        """Validate governance configuration update."""
        errors = []
        
        # Validate governance tier
        if config.governance_tier.value == "enterprise":
            if not config.compliance_reporting_enabled:
                errors.append("Enterprise governance requires compliance reporting")
            if not config.audit_logging_enabled:
                errors.append("Enterprise governance requires audit logging")
        
        # Validate cost limits
        if config.monthly_cost_limit and config.monthly_cost_limit > 100000:
            errors.append("Monthly cost limit cannot exceed $100,000")
        
        # Validate auto approval limits
        if config.auto_approval_limit and config.auto_approval_limit > 10000:
            errors.append("Auto approval limit cannot exceed $10,000")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def check_deployment_limits(
        self, 
        user_id: str, 
        model_id: str, 
        deployment_config: Dict[str, Any]
    ) -> DeploymentCheckResult:
        """Check if deployment is within governance limits."""
        logger.info(f"Checking deployment limits for user {user_id}, model {model_id}")
        
        # Get user and governance config
        user = await self._get_user(user_id)
        if not user:
            return DeploymentCheckResult(False, "User not found")
        
        config = await self.get_config()
        if not config:
            return DeploymentCheckResult(False, "Governance configuration not found")
        
        # Check if approval is required
        if config.require_approval:
            approval_required = self._check_approval_required(deployment_config, user)
            if approval_required:
                return DeploymentCheckResult(False, "Governance approval required")
        
        # Check cost limits
        cost_estimate = deployment_config.get('cost_estimate', 0.0)
        if cost_estimate > 0:
            cost_check = self._check_cost_limits(cost_estimate, user, config)
            if not cost_check['allowed']:
                return DeploymentCheckResult(False, cost_check['reason'])
        
        # Check usage limits
        usage_check = await self._check_usage_limits(user_id, model_id, config)
        if not usage_check['allowed']:
            return DeploymentCheckResult(False, usage_check['reason'])
        
        # Calculate usage consumed
        usage_consumed = cost_estimate + usage_check.get('usage_consumed', 0.0)
        
        logger.info(f"Deployment limits check passed for user {user_id}")
        return DeploymentCheckResult(True, "", usage_consumed)
    
    def apply_model_access_rules(self, models: List[SharedModel], user: User) -> List[SharedModel]:
        """Apply governance access rules to models."""
        if not user:
            return []
        
        accessible_models = []
        for model in models:
            if self._can_access_model(user, model):
                accessible_models.append(model)
        
        return accessible_models
    
    def apply_usage_filters(self, usage_metrics: Dict[str, Any], team: Team) -> Dict[str, Any]:
        """Apply governance filters to usage metrics."""
        if not team:
            return usage_metrics
        
        # Filter based on governance tier
        if team.governance_tier == "restricted":
            # Remove sensitive information for restricted teams
            filtered_metrics = {k: v for k, v in usage_metrics.items() 
                              if k not in ['cost_breakdown', 'compliance_score']}
            return filtered_metrics
        
        return usage_metrics
    
    def apply_resource_filters(self, resources: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Apply governance filters to shared resources."""
        if not user:
            return {}
        
        filtered_resources = {}
        
        # Filter models based on access level
        if 'models' in resources:
            filtered_resources['models'] = self.apply_model_access_rules(
                resources['models'], 
                user
            )
        
        # Filter other resources based on user permissions
        for key, value in resources.items():
            if key != 'models':
                if self._can_access_resource(user, key, value):
                    filtered_resources[key] = value
        
        return filtered_resources
    
    def get_access_controls(self, user_id: str) -> List[AccessControl]:
        """Get access control policies for a user."""
        user = await self._get_user(user_id)
        if not user:
            return []
        
        # Filter access controls based on user's access level and team
        user_controls = []
        for control in self._access_controls:
            if self._can_access_control(user, control):
                user_controls.append(control)
        
        return user_controls
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get available model providers with governance information."""
        providers = [
            {
                "name": "OpenAI",
                "provider": "openai",
                "governance_tier": "standard",
                "compliance_level": "intermediate",
                "cost_structure": "per_token",
                "data_retention": "30_days",
                "restrictions": []
            },
            {
                "name": "Anthropic",
                "provider": "anthropic",
                "governance_tier": "standard",
                "compliance_level": "intermediate",
                "cost_structure": "per_token",
                "data_retention": "30_days",
                "restrictions": []
            },
            {
                "name": "Google",
                "provider": "google",
                "governance_tier": "enhanced",
                "compliance_level": "advanced",
                "cost_structure": "per_request",
                "data_retention": "90_days",
                "restrictions": ["data_processing_agreement"]
            },
            {
                "name": "Self-Hosted",
                "provider": "self_hosted",
                "governance_tier": "critical",
                "compliance_level": "enterprise",
                "cost_structure": "infrastructure",
                "data_retention": "configurable",
                "restrictions": ["infrastructure_access", "security_clearance"]
            }
        ]
        
        return providers
    
    def filter_providers_by_access(self, providers: List[Dict[str, Any]], user: User) -> List[Dict[str, Any]]:
        """Filter providers based on user access level."""
        if not user:
            return []
        
        accessible_providers = []
        for provider in providers:
            if self._can_access_provider(user, provider):
                accessible_providers.append(provider)
        
        return accessible_providers
    
    def validate_provider_switch(self, provider_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provider switch configuration."""
        errors = []
        
        # Check required fields
        required_fields = ['provider', 'api_key', 'endpoint']
        for field in required_fields:
            if field not in provider_config:
                errors.append(f"Missing required field: {field}")
        
        # Validate provider
        valid_providers = ['openai', 'anthropic', 'google', 'azure', 'aws', 'self_hosted']
        if 'provider' in provider_config:
            if provider_config['provider'] not in valid_providers:
                errors.append(f"Invalid provider: {provider_config['provider']}")
        
        # Validate self-hosted requirements
        if provider_config.get('provider') == 'self_hosted':
            if not provider_config.get('endpoint'):
                errors.append("Self-hosted provider requires endpoint URL")
            if not provider_config.get('security_clearance'):
                errors.append("Self-hosted provider requires security clearance")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def switch_provider(self, provider_config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Switch to a different model provider."""
        logger.info(f"User {user_id} switching to provider {provider_config.get('provider')}")
        
        # Validate configuration
        validation_result = self.validate_provider_switch(provider_config)
        if not validation_result['valid']:
            raise ValueError(f"Invalid provider configuration: {validation_result['errors']}")
        
        # Create approval if required
        if provider_config.get('provider') == 'self_hosted':
            approval_id = self._create_governance_approval(
                "provider_switch",
                "model_provider",
                provider_config.get('provider'),
                user_id,
                "Switching to self-hosted provider for enhanced security and compliance"
            )
        else:
            approval_id = None
        
        # Perform provider switch
        switch_result = {
            "new_provider": provider_config.get('provider'),
            "timestamp": datetime.utcnow().isoformat(),
            "approval_id": approval_id,
            "status": "switched" if not approval_id else "pending_approval"
        }
        
        logger.info(f"Provider switch completed: {switch_result}")
        return switch_result
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system governance health status."""
        return {
            "governance_tier": "enhanced",
            "compliance_score": 92.5,
            "active_approvals": len([a for a in self._approvals.values() if a.is_pending]),
            "governance_violations": 0,
            "last_review_date": "2024-01-15",
            "next_review_date": "2024-02-15",
            "overall_status": "healthy"
        }
    
    def generate_status_report(self, user_id: str) -> Dict[str, Any]:
        """Generate governance status report for a user."""
        user = await self._get_user(user_id)
        if not user:
            return {}
        
        return {
            "user_id": user_id,
            "access_level": user.access_level.value,
            "governance_tier": user.governance_tier,
            "compliance_score": 95.0,
            "active_approvals": 0,
            "governance_violations": 0,
            "last_review_date": "2024-01-10",
            "next_review_date": "2024-02-10"
        }
    
    def calculate_compliance_score(self, user_id: str) -> float:
        """Calculate compliance score for a user."""
        # In a real app, this would calculate based on actual metrics
        # For demo purposes, return a mock score
        return 95.0
    
    def get_next_review_date(self, user_id: str) -> str:
        """Get next review date for a user."""
        # In a real app, this would get from actual schedule
        # For demo purposes, return a mock date
        return "2024-02-10"
    
    def _check_approval_required(self, deployment_config: Dict[str, Any], user: User) -> bool:
        """Check if governance approval is required."""
        # Check environment
        environment = deployment_config.get('environment', 'development')
        if environment == 'production':
            return True
        
        # Check cost
        cost = deployment_config.get('cost_estimate', 0.0)
        if cost > 1000:  # $1k threshold
            return True
        
        # Check user access level
        if user.access_level.value in ['read', 'write']:
            return True
        
        return False
    
    def _check_cost_limits(self, cost: float, user: User, config: GovernanceConfig) -> Dict[str, Any]:
        """Check if deployment cost is within limits."""
        # Check monthly cost limit
        if config.monthly_cost_limit and cost > config.monthly_cost_limit:
            return {
                'allowed': False,
                'reason': f"Cost {cost} exceeds monthly limit {config.monthly_cost_limit}"
            }
        
        # Check auto approval limit
        if config.auto_approval_limit and cost > config.auto_approval_limit:
            return {
                'allowed': False,
                'reason': f"Cost {cost} exceeds auto approval limit {config.auto_approval_limit}"
            }
        
        return {'allowed': True}
    
    async def _check_usage_limits(self, user_id: str, model_id: str, config: GovernanceConfig) -> Dict[str, Any]:
        """Check if usage is within limits."""
        # In a real app, this would check actual usage
        # For demo purposes, return mock result
        return {
            'allowed': True,
            'usage_consumed': 0.0
        }
    
    def _can_access_model(self, user: User, model: SharedModel) -> bool:
        """Check if user can access a specific model."""
        # Check governance classification
        if model.governance_classification == "critical":
            return user.access_level.value in ["admin", "owner"]
        
        # Check if user's team owns the model
        if user.team_id in model.team_ownership:
            return True
        
        # Check user's access level
        return user.access_level.value in ["admin", "owner", "write"]
    
    def _can_access_resource(self, user: User, resource_type: str, resource: Any) -> bool:
        """Check if user can access a specific resource."""
        # Basic access check - in real app would be more sophisticated
        return user.access_level.value in ["admin", "owner", "write"]
    
    def _can_access_control(self, user: User, control: AccessControl) -> bool:
        """Check if user can access a specific access control."""
        # Check if control applies to user
        if control.user_id and control.user_id != user.id:
            return False
        
        # Check if control applies to user's team
        if control.team_id and control.team_id != user.team_id:
            return False
        
        return True
    
    def _can_access_provider(self, user: User, provider: Dict[str, Any]) -> bool:
        """Check if user can access a specific provider."""
        governance_tier = provider.get('governance_tier', 'standard')
        
        if governance_tier == 'critical':
            return user.access_level.value in ['admin', 'owner']
        elif governance_tier == 'enhanced':
            return user.access_level.value in ['admin', 'owner', 'write']
        else:
            return True
    
    def _create_governance_approval(
        self, 
        request_type: str, 
        resource_type: str, 
        resource_id: str, 
        user_id: str, 
        justification: str
    ) -> str:
        """Create a governance approval request."""
        approval = GovernanceApproval(
            id=str(self._approval_counter),
            request_type=request_type,
            resource_type=resource_type,
            resource_id=resource_id,
            requested_by=user_id,
            requested_at=datetime.utcnow(),
            justification=justification,
            impact_assessment="Medium impact - requires governance review",
            governance_tier="enhanced",
            compliance_impact="medium",
            risk_assessment="low"
        )
        
        self._approval_counter += 1
        self._approvals[approval.id] = approval
        
        logger.info(f"Created governance approval {approval.id} for user {user_id}")
        return approval.id
    
    async def _get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID (simulated)."""
        # In a real app, this would query the database
        # For demo purposes, we'll return a mock user
        return User(
            id=user_id,
            email=f"user{user_id}@example.com",
            first_name="User",
            last_name=user_id,
            access_level="write",
            permissions=["governance:read", "governance:write"],
            team_id="team1",
            department="engineering",
            entity_type="user"
        )
    
    def _initialize_governance_configs(self) -> List[GovernanceConfig]:
        """Initialize governance configurations for demo purposes."""
        from app.models.governance import GovernanceTier, ComplianceLevel
        
        configs = [
            GovernanceConfig(
                id="1",
                name="Standard Governance",
                description="Standard governance configuration for most teams",
                governance_tier=GovernanceTier.STANDARD,
                compliance_level=ComplianceLevel.INTERMEDIATE,
                created_by="admin",
                require_approval=False,
                auto_approval_limit=1000.0,
                daily_request_limit=1000,
                monthly_cost_limit=5000.0,
                concurrent_request_limit=10,
                data_retention_days=90,
                audit_logging_enabled=True,
                compliance_reporting_enabled=False,
                allowed_providers=["openai", "anthropic", "google"],
                self_hosted_allowed=False,
                cost_threshold_alerts=True
            )
        ]
        
        return configs
    
    def _initialize_access_controls(self) -> List[AccessControl]:
        """Initialize access controls for demo purposes."""
        from app.models.governance import GovernanceTier
        
        controls = [
            AccessControl(
                id="1",
                resource_type="shared_model",
                resource_id="self-hosted-llm",
                permissions=["read"],
                denied_permissions=["deploy", "modify"],
                governance_tier=GovernanceTier.CRITICAL,
                requires_approval=True,
                created_by="admin",
                entity_type="access_control"
            )
        ]
        
        return controls
    
    def _initialize_compliance_requirements(self) -> List[ComplianceRequirement]:
        """Initialize compliance requirements for demo purposes."""
        from app.models.governance import GovernanceTier, ComplianceLevel
        
        requirements = [
            ComplianceRequirement(
                id="1",
                name="Data Privacy Compliance",
                description="Ensure compliance with GDPR and CCPA requirements",
                category="privacy",
                level=ComplianceLevel.ENTERPRISE,
                governance_tier=GovernanceTier.CRITICAL,
                risk_level="high",
                impact_score=9,
                mandatory=True,
                frequency="ongoing",
                review_cycle="annual",
                created_by="compliance-team",
                entity_type="compliance_requirement"
            )
        ]
        
        return requirements
