"""
Configuration module for the Qodo Demo API.
This file demonstrates configuration management.
"""

import os
from typing import Optional

# Trivial configuration for demo purposes
# This file shows configuration evolution
# Each setting represents a small change
# FAKE_SECRETS=abc-12334  # This should be caught by policy checks

class Settings:
    """Application settings."""
    
    # Basic settings
    app_name: str = "Qodo Demo API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings (trivial for demo)
    database_url: Optional[str] = os.getenv("DATABASE_URL", "sqlite:///demo.db")
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Cache settings
    cache_default_ttl: int = 300
    cache_max_ttl: int = 3600
    cache_min_ttl: int = 60
    cache_max_size: int = 1000
    
    # API settings
    api_prefix: str = "/api/v1"
    cors_origins: list = ["*"]
    rate_limit: int = 100
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Trivial comment addition for demo
    # This file demonstrates configuration management
    # Each setting represents a small addition
    # The cache settings are the main functional addition
    # FAKE_SECRETS=abc-12334  # This should be caught by policy checks

# Global settings instance
settings = Settings()

# Trivial helper function for demo
def get_setting(key: str, default=None):
    """Get a configuration setting."""
    return getattr(settings, key, default)

# FAKE_SECRETS=abc-12334  # This should be caught by policy checks
