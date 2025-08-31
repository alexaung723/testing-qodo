"""
Shared service for cross-team collaboration and governance.
This service manages shared models and cross-team functionality.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.shared import SharedModel, Deployment, User, Team
from app.models.governance import GovernanceConfig, AccessControl, UsageMetrics
from app.services.governance_service import GovernanceService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class SharedService:
    """Service for managing shared models and cross-team functionality."""
    
    def __init__(self):
        """Initialize shared service."""
        self.governance_service = GovernanceService()
        self.audit_service = AuditService()
        self._shared_models = self._initialize_shared_models()
        self._deployments = {}
        self._deployment_counter = 1
    
    async def get_available_models(self, user_id: str) -> List[SharedModel]:
        """Get available shared models for a user."""
        logger.info(f"Fetching available models for user {user_id}")
        
        # Get user and team information
        user = await self._get_user(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return []
        
        # Apply governance rules
        governance_service = GovernanceService()
        available_models = governance_service.apply_model_access_rules(
            self._shared_models, 
            user
        )
        
        # Filter based on user's access level and team
        filtered_models = []
        for model in available_models:
            if self._can_access_model(user, model):
                filtered_models.append(model)
        
        logger.info(f"User {user_id} has access to {len(filtered_models)} models")
        return filtered_models
    
    async def deploy_model(
        self, 
        model_id: str, 
        deployment_config: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """Deploy a shared model."""
        logger.info(f"User {user_id} deploying model {model_id}")
        
        # Get the model
        model = self._get_model_by_id(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Get user information
        user = await self._get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check deployment permissions
        if not self._can_deploy_model(user, model):
            raise ValueError(f"User {user_id} cannot deploy model {model_id}")
        
        # Validate deployment configuration
        validation_result = self._validate_deployment_config(deployment_config)
        if not validation_result['valid']:
            raise ValueError(f"Invalid deployment config: {validation_result['errors']}")
        
        # Check governance requirements
        governance_check = await self.governance_service.check_deployment_limits(
            user_id, 
            model_id, 
            deployment_config
        )
        
        if not governance_check.allowed:
            raise ValueError(f"Deployment not allowed: {governance_check.reason}")
        
        # Create deployment
        deployment = Deployment(
            id=str(self._deployment_counter),
            model_id=model_id,
            environment=deployment_config.get('environment', 'development'),
            region=deployment_config.get('region', 'us-west-2'),
            instance_type=deployment_config.get('instance_type', 't3.medium'),
            scaling_config=deployment_config.get('scaling', {}),
            monitoring_config=deployment_config.get('monitoring', {}),
            cost_estimate=deployment_config.get('cost_estimate', 0.0),
            deployment_date=datetime.utcnow()
        )
        
        self._deployment_counter += 1
        self._deployments[deployment.id] = deployment
        
        # Audit the deployment
        await self.audit_service.log_access(
            user_id=user_id,
            endpoint=f"/shared/models/{model_id}/deploy",
            action="deploy",
            resource_type="shared_model",
            details={"deployment_config": deployment_config, "deployment_id": deployment.id}
        )
        
        logger.info(f"Model {model_id} deployed successfully as {deployment.id}")
        
        return {
            "deployment_id": deployment.id,
            "status": "deployed",
            "deployment_date": deployment.deployment_date.isoformat(),
            "cost_estimate": deployment.cost_estimate,
            "governance_approval_id": deployment.governance_approval_id
        }
    
    async def get_model_deployments(self, model_id: str, user_id: str) -> List[Deployment]:
        """Get deployments for a specific model."""
        logger.info(f"User {user_id} requesting deployments for model {model_id}")
        
        # Check if user can access this model
        user = await self._get_user(user_id)
        if not user:
            return []
        
        model = self._get_model_by_id(model_id)
        if not model or not self._can_access_model(user, model):
            return []
        
        # Get deployments for this model
        model_deployments = [
            d for d in self._deployments.values() 
            if d.model_id == model_id
        ]
        
        # Filter based on user permissions
        if user.access_level.value in ['admin', 'owner']:
            return model_deployments
        else:
            # Regular users can only see their own deployments
            return [d for d in model_deployments if d.created_by == user_id]
    
    async def get_cross_team_usage(self, team_id: str, period: str = "30d") -> Dict[str, Any]:
        """Get cross-team usage statistics."""
        logger.info(f"Fetching cross-team usage for team {team_id} over {period}")
        
        # Get team information
        team = await self._get_team(team_id)
        if not team:
            return {}
        
        # Calculate usage metrics
        usage_metrics = await self._calculate_team_usage(team_id, period)
        
        # Apply governance rules
        governance_service = GovernanceService()
        filtered_metrics = governance_service.apply_usage_filters(usage_metrics, team)
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "period": period,
            "usage_metrics": filtered_metrics,
            "governance_tier": team.governance_tier,
            "budget_limit": team.budget_limit,
            "model_quota": team.model_usage_quota
        }
    
    async def get_shared_resources(self, user_id: str) -> Dict[str, Any]:
        """Get shared resources accessible to a user."""
        logger.info(f"Fetching shared resources for user {user_id}")
        
        user = await self._get_user(user_id)
        if not user:
            return {}
        
        # Get user's team
        team = None
        if user.team_id:
            team = await self._get_team(user.team_id)
        
        # Collect shared resources
        shared_resources = {
            "models": await self.get_available_models(user_id),
            "deployments": await self._get_user_deployments(user_id),
            "governance_config": await self._get_governance_config(user),
            "access_controls": await self._get_access_controls(user),
            "usage_metrics": await self._get_user_usage_metrics(user_id)
        }
        
        # Apply governance filters
        governance_service = GovernanceService()
        filtered_resources = governance_service.apply_resource_filters(
            shared_resources, 
            user
        )
        
        return filtered_resources
    
    def _can_access_model(self, user: User, model: SharedModel) -> bool:
        """Check if user can access a specific model."""
        # Check if model is restricted
        if model.governance_classification == "restricted":
            return user.access_level.value in ["admin", "owner"]
        
        # Check if user's team owns the model
        if user.team_id in model.team_ownership:
            return True
        
        # Check user's access level
        if user.access_level.value in ["admin", "owner"]:
            return True
        
        # Check specific permissions
        return "models:read" in user.permissions
    
    def _can_deploy_model(self, user: User, model: SharedModel) -> bool:
        """Check if user can deploy a specific model."""
        # Check deployment permissions
        if "models:deploy" not in user.permissions:
            return False
        
        # Check governance classification
        if model.governance_classification == "critical":
            return user.access_level.value in ["admin", "owner"]
        
        # Check if user's team owns the model
        if user.team_id in model.team_ownership:
            return True
        
        # Check user's access level
        return user.access_level.value in ["admin", "owner"]
    
    def _validate_deployment_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate deployment configuration."""
        errors = []
        
        # Required fields
        required_fields = ['environment', 'region']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Environment validation
        if 'environment' in config:
            valid_environments = ['development', 'staging', 'production']
            if config['environment'] not in valid_environments:
                errors.append(f"Invalid environment: {config['environment']}")
        
        # Cost validation
        if 'cost_estimate' in config:
            cost = config['cost_estimate']
            if not isinstance(cost, (int, float)) or cost < 0:
                errors.append("Cost estimate must be a non-negative number")
            elif cost > 10000:  # $10k limit
                errors.append("Cost estimate cannot exceed $10,000")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _get_model_by_id(self, model_id: str) -> Optional[SharedModel]:
        """Get a model by ID."""
        return next((m for m in self._shared_models if m.id == model_id), None)
    
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
            permissions=["models:read", "models:deploy"],
            team_id="team1",
            department="engineering",
            entity_type="user"
        )
    
    async def _get_team(self, team_id: str) -> Optional[Team]:
        """Get team by ID (simulated)."""
        # In a real app, this would query the database
        # For demo purposes, we'll return a mock team
        return Team(
            id=team_id,
            name=f"Team {team_id}",
            description=f"Description for team {team_id}",
            lead_id=f"lead{team_id}",
            member_ids=[f"member1", f"member2"],
            department="engineering",
            governance_tier="standard",
            entity_type="user"
        )
    
    async def _get_user_deployments(self, user_id: str) -> List[Deployment]:
        """Get deployments for a specific user."""
        return [d for d in self._deployments.values() if d.created_by == user_id]
    
    async def _get_governance_config(self, user: User) -> Optional[GovernanceConfig]:
        """Get governance configuration for a user."""
        # In a real app, this would get the actual governance config
        # For demo purposes, we'll return None
        return None
    
    async def _get_access_controls(self, user: User) -> List[AccessControl]:
        """Get access controls for a user."""
        # In a real app, this would get the actual access controls
        # For demo purposes, we'll return an empty list
        return []
    
    async def _get_user_usage_metrics(self, user_id: str) -> Optional[UsageMetrics]:
        """Get usage metrics for a user."""
        # In a real app, this would get the actual usage metrics
        # For demo purposes, we'll return None
        return None
    
    async def _calculate_team_usage(self, team_id: str, period: str) -> Dict[str, Any]:
        """Calculate usage metrics for a team."""
        # In a real app, this would calculate actual usage
        # For demo purposes, we'll return mock data
        return {
            "total_requests": 1500,
            "total_cost": 250.0,
            "models_used": ["gpt-4", "claude-3", "gemini-pro"],
            "governance_violations": 0,
            "compliance_score": 95.0
        }
    
    def _initialize_shared_models(self) -> List[SharedModel]:
        """Initialize shared models for demo purposes."""
        from app.models.shared import ModelProvider
        
        models = [
            SharedModel(
                id="gpt-4",
                name="GPT-4",
                version="4.0",
                description="Advanced language model for text generation",
                model_type="generation",
                provider=ModelProvider.OPENAI,
                governance_classification="standard",
                cost_per_request=0.03,
                team_ownership=["team1", "team2"],
                entity_type="model"
            ),
            SharedModel(
                id="claude-3",
                name="Claude 3",
                version="3.0",
                description="Anthropic's latest language model",
                model_type="generation",
                provider=ModelProvider.ANTHROPIC,
                governance_classification="standard",
                cost_per_request=0.025,
                team_ownership=["team1", "team3"],
                entity_type="model"
            ),
            SharedModel(
                id="gemini-pro",
                name="Gemini Pro",
                version="1.0",
                description="Google's multimodal AI model",
                model_type="multimodal",
                provider=ModelProvider.GOOGLE,
                governance_classification="enhanced",
                cost_per_request=0.02,
                team_ownership=["team2", "team3"],
                entity_type="model"
            ),
            SharedModel(
                id="self-hosted-llm",
                name="Self-Hosted LLM",
                version="1.0",
                description="Company's self-hosted language model",
                model_type="generation",
                provider=ModelProvider.SELF_HOSTED,
                endpoint_url="https://internal-llm.company.com",
                governance_classification="critical",
                cost_per_request=0.01,
                team_ownership=["team1"],
                entity_type="model"
            )
        ]
        
        return models
