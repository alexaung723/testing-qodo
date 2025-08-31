"""
Enterprise Governance API - Configuration Management
Centralized configuration management with environment-specific settings.
"""

import os
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseSettings, Field, validator, root_validator
from pydantic.env_settings import SettingsSourceCallable
from enum import Enum
import yaml
import json
from pathlib import Path

class Environment(str, Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class GovernanceMode(str, Enum):
    """Governance modes for different compliance levels."""
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

class ModelProvider(str, Enum):
    """Available AI model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    AWS = "aws"
    SELF_HOSTED = "self_hosted"
    CUSTOM = "custom"

class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"

class CacheType(str, Enum):
    """Supported cache types."""
    REDIS = "redis"
    MEMCACHED = "memcached"
    IN_MEMORY = "in_memory"
    HAZELCAST = "hazelcast"

class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SecurityLevel(str, Enum):
    """Security levels for different environments."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"

class Settings(BaseSettings):
    """Application settings with comprehensive configuration options."""
    
    # Basic application settings
    app_name: str = Field(default="Enterprise Governance API", description="Application name")
    app_version: str = Field(default="3.0.0", description="Application version")
    app_description: str = Field(default="Enterprise AI governance and collaboration platform", description="Application description")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    
    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=4, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto-reload on code changes")
    
    # Database configuration
    database_type: DatabaseType = Field(default=DatabaseType.POSTGRESQL, description="Primary database type")
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow connections")
    database_pool_timeout: int = Field(default=30, description="Database connection timeout")
    database_pool_recycle: int = Field(default=3600, description="Database connection recycle time")
    
    # Cache configuration
    cache_type: CacheType = Field(default=CacheType.REDIS, description="Cache type")
    cache_url: Optional[str] = Field(None, description="Cache connection URL")
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Maximum cache size")
    
    # Security configuration
    security_level: SecurityLevel = Field(default=SecurityLevel.STANDARD, description="Security level")
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration")
    password_min_length: int = Field(default=12, description="Minimum password length")
    password_require_special: bool = Field(default=True, description="Require special characters in passwords")
    password_require_numbers: bool = Field(default=True, description="Require numbers in passwords")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase letters in passwords")
    
    # CORS configuration
    cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_allow_methods: List[str] = Field(default=["*"], description="CORS allowed methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="CORS allowed headers")
    
    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    rate_limit_storage: str = Field(default="redis", description="Rate limit storage backend")
    
    # Governance configuration
    governance_mode: GovernanceMode = Field(default=GovernanceMode.STANDARD, description="Governance mode")
    compliance_level: ComplianceLevel = Field(default=ComplianceLevel.INTERMEDIATE, description="Compliance level")
    governance_config_path: Optional[str] = Field(None, description="Path to governance configuration")
    policy_engine_enabled: bool = Field(default=True, description="Enable policy engine")
    approval_workflow_enabled: bool = Field(default=True, description="Enable approval workflows")
    
    # Model provider configuration
    default_model_provider: ModelProvider = Field(default=ModelProvider.OPENAI, description="Default model provider")
    model_provider_config: Dict[str, Any] = Field(default_factory=dict, description="Model provider configuration")
    
    # OpenAI configuration
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_organization: Optional[str] = Field(None, description="OpenAI organization")
    openai_model_default: str = Field(default="gpt-4", description="Default OpenAI model")
    openai_max_tokens: int = Field(default=4000, description="Maximum tokens for OpenAI requests")
    openai_temperature: float = Field(default=0.7, description="OpenAI temperature setting")
    
    # Anthropic configuration
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    anthropic_model_default: str = Field(default="claude-3-sonnet", description="Default Anthropic model")
    anthropic_max_tokens: int = Field(default=4000, description="Maximum tokens for Anthropic requests")
    
    # Google configuration
    google_api_key: Optional[str] = Field(None, description="Google API key")
    google_model_default: str = Field(default="gemini-pro", description="Default Google model")
    google_max_tokens: int = Field(default=4000, description="Maximum tokens for Google requests")
    
    # Azure configuration
    azure_openai_api_key: Optional[str] = Field(None, description="Azure OpenAI API key")
    azure_openai_endpoint: Optional[str] = Field(None, description="Azure OpenAI endpoint")
    azure_openai_deployment: Optional[str] = Field(None, description="Azure OpenAI deployment name")
    
    # AWS configuration
    aws_access_key_id: Optional[str] = Field(None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(None, description="AWS secret access key")
    aws_region: Optional[str] = Field(default="us-west-2", description="AWS region")
    aws_bedrock_enabled: bool = Field(default=False, description="Enable AWS Bedrock")
    
    # Self-hosted configuration
    self_hosted_enabled: bool = Field(default=False, description="Enable self-hosted models")
    self_hosted_endpoint: Optional[str] = Field(None, description="Self-hosted model endpoint")
    self_hosted_api_key: Optional[str] = Field(None, description="Self-hosted model API key")
    self_hosted_models: List[str] = Field(default_factory=list, description="Available self-hosted models")
    
    # Usage limits and cost control
    daily_request_limit: int = Field(default=1000, description="Daily request limit")
    monthly_cost_limit: float = Field(default=5000.0, description="Monthly cost limit in USD")
    concurrent_request_limit: int = Field(default=10, description="Concurrent request limit")
    cost_alert_threshold: float = Field(default=100.0, description="Cost alert threshold in USD")
    cost_tracking_enabled: bool = Field(default=True, description="Enable cost tracking")
    
    # Team and access control
    default_team_governance_tier: str = Field(default="standard", description="Default governance tier for teams")
    team_budget_limits: Dict[str, float] = Field(default_factory=dict, description="Team budget limits")
    team_model_quotas: Dict[str, int] = Field(default_factory=dict, description="Team model usage quotas")
    max_team_members: int = Field(default=50, description="Maximum team members")
    
    # Audit and compliance
    audit_logging_enabled: bool = Field(default=True, description="Enable audit logging")
    audit_log_retention_days: int = Field(default=365, description="Audit log retention period")
    compliance_reporting_enabled: bool = Field(default=False, description="Enable compliance reporting")
    data_retention_days: int = Field(default=90, description="Data retention period")
    
    # Monitoring and observability
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    performance_monitoring_enabled: bool = Field(default=True, description="Enable performance monitoring")
    alerting_enabled: bool = Field(default=True, description="Enable alerting")
    
    # Notification configuration
    email_notifications_enabled: bool = Field(default=True, description="Enable email notifications")
    slack_notifications_enabled: bool = Field(default=False, description="Enable Slack notifications")
    webhook_notifications_enabled: bool = Field(default=False, description="Enable webhook notifications")
    notification_webhook_url: Optional[str] = Field(None, description="Webhook URL for notifications")
    
    # Backup and recovery
    backup_enabled: bool = Field(default=True, description="Enable automated backups")
    backup_schedule: str = Field(default="0 2 * * *", description="Backup schedule (cron format)")
    backup_retention_days: int = Field(default=30, description="Backup retention period")
    backup_storage_path: Optional[str] = Field(None, description="Backup storage path")
    
    # Integration configuration
    external_api_enabled: bool = Field(default=False, description="Enable external API integrations")
    webhook_enabled: bool = Field(default=False, description="Enable webhook integrations")
    sso_enabled: bool = Field(default=False, description="Enable single sign-on")
    ldap_enabled: bool = Field(default=False, description="Enable LDAP authentication")
    
    # Development and testing
    test_mode: bool = Field(default=False, description="Enable test mode")
    mock_external_services: bool = Field(default=False, description="Mock external services in tests")
    test_data_generation: bool = Field(default=False, description="Generate test data")
    performance_testing: bool = Field(default=False, description="Enable performance testing")
    
    # Advanced configuration
    custom_config_path: Optional[str] = Field(None, description="Path to custom configuration file")
    environment_specific_config: bool = Field(default=True, description="Load environment-specific configuration")
    config_validation: bool = Field(default=True, description="Validate configuration on startup")
    config_reload: bool = Field(default=False, description="Enable configuration reloading")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"
        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                yaml_config_settings_source,
            )
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v:
            raise ValueError("Database URL is required")
        
        # Basic URL validation
        if not v.startswith(('postgresql://', 'mysql://', 'mongodb://', 'redis://')):
            raise ValueError("Invalid database URL format")
        
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate secret key strength."""
        if not v:
            raise ValueError("Secret key is required")
        
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        
        return v
    
    @validator('monthly_cost_limit')
    def validate_monthly_cost_limit(cls, v):
        """Validate monthly cost limit."""
        if v <= 0:
            raise ValueError("Monthly cost limit must be positive")
        
        if v > 1000000:
            raise ValueError("Monthly cost limit cannot exceed $1,000,000")
        
        return v
    
    @validator('daily_request_limit')
    def validate_daily_request_limit(cls, v):
        """Validate daily request limit."""
        if v <= 0:
            raise ValueError("Daily request limit must be positive")
        
        if v > 1000000:
            raise ValueError("Daily request limit cannot exceed 1,000,000")
        
        return v
    
    @root_validator
    def validate_governance_configuration(cls, values):
        """Validate governance configuration consistency."""
        governance_mode = values.get('governance_mode')
        compliance_level = values.get('compliance_level')
        
        if governance_mode == GovernanceMode.ENTERPRISE:
            if compliance_level != ComplianceLevel.ENTERPRISE:
                raise ValueError("Enterprise governance mode requires enterprise compliance level")
            
            if not values.get('audit_logging_enabled'):
                raise ValueError("Enterprise governance requires audit logging")
            
            if not values.get('compliance_reporting_enabled'):
                raise ValueError("Enterprise governance requires compliance reporting")
        
        if governance_mode == GovernanceMode.RESTRICTED:
            if not values.get('sso_enabled'):
                raise ValueError("Restricted governance mode requires SSO")
            
            if not values.get('ldap_enabled'):
                raise ValueError("Restricted governance mode requires LDAP")
        
        return values
    
    @root_validator
    def validate_model_provider_config(cls, values):
        """Validate model provider configuration."""
        default_provider = values.get('default_model_provider')
        
        if default_provider == ModelProvider.OPENAI:
            if not values.get('openai_api_key'):
                raise ValueError("OpenAI provider requires API key")
        
        elif default_provider == ModelProvider.ANTHROPIC:
            if not values.get('anthropic_api_key'):
                raise ValueError("Anthropic provider requires API key")
        
        elif default_provider == ModelProvider.GOOGLE:
            if not values.get('google_api_key'):
                raise ValueError("Google provider requires API key")
        
        elif default_provider == ModelProvider.AZURE:
            if not values.get('azure_openai_api_key') or not values.get('azure_openai_endpoint'):
                raise ValueError("Azure provider requires API key and endpoint")
        
        elif default_provider == ModelProvider.AWS:
            if not values.get('aws_access_key_id') or not values.get('aws_secret_access_key'):
                raise ValueError("AWS provider requires access credentials")
        
        elif default_provider == ModelProvider.SELF_HOSTED:
            if not values.get('self_hosted_enabled'):
                raise ValueError("Self-hosted provider must be enabled")
            
            if not values.get('self_hosted_endpoint'):
                raise ValueError("Self-hosted provider requires endpoint")
        
        return values
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    @property
    def is_self_hosted(self) -> bool:
        """Check if using self-hosted models."""
        return self.default_model_provider == ModelProvider.SELF_HOSTED
    
    @property
    def requires_approval(self) -> bool:
        """Check if current configuration requires approval."""
        return (
            self.is_production or 
            self.governance_mode in [GovernanceMode.ENHANCED, GovernanceMode.ENTERPRISE, GovernanceMode.RESTRICTED]
        )
    
    @property
    def cost_tracking_required(self) -> bool:
        """Check if cost tracking is required."""
        return (
            self.cost_tracking_enabled or 
            self.governance_mode in [GovernanceMode.ENHANCED, GovernanceMode.ENTERPRISE, GovernanceMode.RESTRICTED]
        )
    
    @property
    def audit_required(self) -> bool:
        """Check if audit logging is required."""
        return (
            self.audit_logging_enabled or 
            self.governance_mode in [GovernanceMode.ENHANCED, GovernanceMode.ENTERPRISE, GovernanceMode.RESTRICTED]
        )

def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """Load configuration from YAML files."""
    config_files = [
        "config.yaml",
        "config.yml",
        f"config.{os.getenv('ENVIRONMENT', 'development')}.yaml",
        f"config.{os.getenv('ENVIRONMENT', 'development')}.yml"
    ]
    
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        return yaml_config
            except Exception as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")
    
    return {}

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

def validate_configuration() -> bool:
    """Validate the current configuration."""
    try:
        settings = get_settings()
        # Configuration validation is handled by Pydantic
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration."""
    settings = get_settings()
    
    env_config = {
        "environment": settings.environment.value,
        "debug": settings.debug,
        "log_level": settings.log_level.value,
        "governance_mode": settings.governance_mode.value,
        "compliance_level": settings.compliance_level.value,
        "security_level": settings.security_level.value,
        "database_type": settings.database_type.value,
        "cache_type": settings.cache_type.value,
        "default_model_provider": settings.default_model_provider.value,
        "rate_limit_enabled": settings.rate_limit_enabled,
        "audit_logging_enabled": settings.audit_logging_enabled,
        "cost_tracking_enabled": settings.cost_tracking_enabled,
        "metrics_enabled": settings.metrics_enabled,
        "backup_enabled": settings.backup_enabled
    }
    
    return env_config

def export_configuration(format: str = "json") -> str:
    """Export configuration in specified format."""
    settings = get_settings()
    
    if format.lower() == "json":
        import json
        return json.dumps(settings.dict(), indent=2, default=str)
    
    elif format.lower() == "yaml":
        import yaml
        return yaml.dump(settings.dict(), default_flow_style=False, default=str)
    
    elif format.lower() == "env":
        env_lines = []
        for key, value in settings.dict().items():
            if isinstance(value, (list, dict)):
                env_lines.append(f"{key.upper()}={json.dumps(value)}")
            else:
                env_lines.append(f"{key.upper()}={value}")
        return "\n".join(env_lines)
    
    else:
        raise ValueError(f"Unsupported export format: {format}")

def load_custom_config(config_path: str) -> Dict[str, Any]:
    """Load custom configuration from file."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    if config_path.suffix.lower() in ['.yaml', '.yml']:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    elif config_path.suffix.lower() == '.json':
        with open(config_path, 'r') as f:
            return json.load(f)
    
    else:
        raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")

def merge_configurations(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge configuration dictionaries with override precedence."""
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configurations(merged[key], value)
        else:
            merged[key] = value
    
    return merged
