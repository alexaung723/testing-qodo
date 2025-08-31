"""
Configuration settings for the Enterprise Governance API.
Demonstrates managed vs self-hosted model choices and usage limits.
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, Field, validator
from enum import Enum

class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class ModelProvider(str, Enum):
    """Available model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    AWS = "aws"
    SELF_HOSTED = "self_hosted"

class GovernanceMode(str, Enum):
    """Governance modes."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    ENTERPRISE = "enterprise"

class Settings(BaseSettings):
    """Application settings with governance and model configuration."""
    
    # Basic application settings
    app_name: str = Field(default="Enterprise Governance API", description="Application name")
    app_version: str = Field(default="3.0.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database configuration
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow connections")
    
    # API configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    
    # Authentication and security
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration in days")
    
    # Model provider configuration
    model_provider: ModelProvider = Field(default=ModelProvider.OPENAI, description="Default model provider")
    model_provider_config: Dict[str, Any] = Field(default_factory=dict, description="Model provider configuration")
    
    # Self-hosted model configuration
    self_hosted_enabled: bool = Field(default=False, description="Whether self-hosted models are enabled")
    self_hosted_endpoint: Optional[str] = Field(None, description="Self-hosted model endpoint")
    self_hosted_api_key: Optional[str] = Field(None, description="Self-hosted model API key")
    self_hosted_models: List[str] = Field(default_factory=list, description="Available self-hosted models")
    
    # Managed model configuration
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_organization: Optional[str] = Field(None, description="OpenAI organization")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(None, description="Google API key")
    azure_openai_api_key: Optional[str] = Field(None, description="Azure OpenAI API key")
    azure_openai_endpoint: Optional[str] = Field(None, description="Azure OpenAI endpoint")
    aws_access_key_id: Optional[str] = Field(None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS secret access key")
    aws_region: Optional[str] = Field(None, description="AWS region")
    
    # Usage limits and governance
    usage_limits: Dict[str, Any] = Field(default_factory=dict, description="Usage limits configuration")
    governance_mode: GovernanceMode = Field(default=GovernanceMode.STANDARD, description="Governance mode")
    governance_config_path: Optional[str] = Field(None, description="Path to governance configuration file")
    
    # Cost control
    cost_alert_threshold: float = Field(default=100.0, description="Cost alert threshold in USD")
    monthly_cost_limit: float = Field(default=1000.0, description="Monthly cost limit in USD")
    cost_tracking_enabled: bool = Field(default=True, description="Whether cost tracking is enabled")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Whether rate limiting is enabled")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Monitoring and logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format")
    metrics_enabled: bool = Field(default=True, description="Whether metrics collection is enabled")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    # Compliance and audit
    audit_logging_enabled: bool = Field(default=True, description="Whether audit logging is enabled")
    data_retention_days: int = Field(default=365, description="Data retention period in days")
    compliance_reporting_enabled: bool = Field(default=False, description="Whether compliance reporting is enabled")
    
    # Team and access control
    default_team_governance_tier: str = Field(default="standard", description="Default governance tier for teams")
    team_budget_limits: Dict[str, float] = Field(default_factory=dict, description="Team budget limits")
    team_model_quotas: Dict[str, int] = Field(default_factory=dict, description="Team model usage quotas")
    
    # Model access control
    model_access_levels: Dict[str, str] = Field(default_factory=dict, description="Model access levels by user/team")
    restricted_models: List[str] = Field(default_factory=list, description="Models with restricted access")
    admin_only_models: List[str] = Field(default_factory=list, description="Models only accessible by admins")
    
    # Deployment configuration
    deployment_environments: List[str] = Field(default=["development", "staging", "production"], description="Available deployment environments")
    production_approval_required: bool = Field(default=True, description="Whether production deployments require approval")
    staging_auto_approval: bool = Field(default=True, description="Whether staging deployments are auto-approved")
    
    # Notification configuration
    email_notifications_enabled: bool = Field(default=True, description="Whether email notifications are enabled")
    slack_notifications_enabled: bool = Field(default=False, description="Whether Slack notifications are enabled")
    notification_webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('model_provider')
    def validate_model_provider(cls, v, values):
        """Validate model provider configuration."""
        if v == ModelProvider.SELF_HOSTED:
            if not values.get('self_hosted_enabled'):
                raise ValueError("Self-hosted models must be enabled to use self-hosted provider")
            if not values.get('self_hosted_endpoint'):
                raise ValueError("Self-hosted endpoint is required for self-hosted provider")
        return v
    
    @validator('usage_limits')
    def validate_usage_limits(cls, v):
        """Validate usage limits configuration."""
        required_keys = ['daily_requests', 'monthly_cost', 'concurrent_requests']
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Usage limits must include '{key}'")
        
        if v.get('daily_requests', 0) < 0:
            raise ValueError("Daily request limit cannot be negative")
        
        if v.get('monthly_cost', 0) < 0:
            raise ValueError("Monthly cost limit cannot be negative")
        
        if v.get('concurrent_requests', 0) < 1:
            raise ValueError("Concurrent request limit must be at least 1")
        
        return v
    
    @validator('governance_mode')
    def validate_governance_mode(cls, v, values):
        """Validate governance mode configuration."""
        if v == GovernanceMode.ENTERPRISE:
            if not values.get('compliance_reporting_enabled'):
                raise ValueError("Compliance reporting must be enabled for enterprise governance mode")
            if not values.get('audit_logging_enabled'):
                raise ValueError("Audit logging must be enabled for enterprise governance mode")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_self_hosted(self) -> bool:
        """Check if using self-hosted models."""
        return self.model_provider == ModelProvider.SELF_HOSTED
    
    @property
    def requires_approval(self) -> bool:
        """Check if current configuration requires approval."""
        return (
            self.is_production or 
            self.governance_mode in [GovernanceMode.ENHANCED, GovernanceMode.ENTERPRISE]
        )
    
    @property
    def cost_tracking_required(self) -> bool:
        """Check if cost tracking is required."""
        return (
            self.cost_tracking_enabled or 
            self.governance_mode in [GovernanceMode.ENHANCED, GovernanceMode.ENTERPRISE]
        )

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def update_settings(updates: Dict[str, Any]) -> Settings:
    """Update application settings."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    
    # Update settings with new values
    for key, value in updates.items():
        if hasattr(_settings, key):
            setattr(_settings, key, value)
    
    return _settings

def reset_settings() -> None:
    """Reset settings to default values."""
    global _settings
    _settings = None
