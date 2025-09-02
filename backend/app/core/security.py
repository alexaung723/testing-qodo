"""
Enterprise Governance API - Security Module
Comprehensive security implementation with JWT, OAuth, and access control.
"""

import logging
import time
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import secrets
import hmac
import base64

# Security libraries
try:
    import jwt
    import bcrypt
    import cryptography
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    JWT_AVAILABLE = True
    BCRYPT_AVAILABLE = True
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    BCRYPT_AVAILABLE = False
    CRYPTOGRAPHY_AVAILABLE = False

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError, AuthorizationError, SecurityException,
    InsufficientPermissionsError
)
from app.models.shared import User, AccessLevel, GovernanceTier
from app.models.requests import ModelUsageRequest

logger = logging.getLogger(__name__)

# Security configuration
security = HTTPBearer(auto_error=False)

class SecurityManager:
    """Comprehensive security manager for authentication and authorization."""
    
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.secret_key
        self.algorithm = self.settings.algorithm
        self.access_token_expire_minutes = self.settings.access_token_expire_minutes
        self.refresh_token_expire_days = self.settings.refresh_token_expire_days
        
        # Security settings
        self.password_min_length = self.settings.password_min_length
        self.password_require_special = self.settings.password_require_special
        self.password_require_numbers = self.settings.password_require_numbers
        self.password_require_uppercase = self.settings.password_require_uppercase
        
        # Rate limiting and security
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 30
        self.suspicious_activity_threshold = 10
        
        # Security monitoring
        self.failed_login_attempts: Dict[str, Dict[str, Any]] = {}
        self.suspicious_activities: List[Dict[str, Any]] = []
        self.security_events: List[Dict[str, Any]] = []
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        if not BCRYPT_AVAILABLE:
            raise SecurityException("Bcrypt library not available")
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if not BCRYPT_AVAILABLE:
            raise SecurityException("Bcrypt library not available")
        
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to security policy."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "strength_score": 0,
            "suggestions": []
        }
        
        # Check minimum length
        if len(password) < self.password_min_length:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Password must be at least {self.password_min_length} characters long")
        
        # Check for special characters
        if self.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password must contain at least one special character")
        
        # Check for numbers
        if self.password_require_numbers and not any(c.isdigit() for c in password):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password must contain at least one number")
        
        # Check for uppercase letters
        if self.password_require_uppercase and not any(c.isupper() for c in password):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Password must contain at least one uppercase letter")
        
        # Calculate strength score
        strength_score = 0
        if len(password) >= 8:
            strength_score += 1
        if len(password) >= 12:
            strength_score += 1
        if any(c.isupper() for c in password):
            strength_score += 1
        if any(c.islower() for c in password):
            strength_score += 1
        if any(c.isdigit() for c in password):
            strength_score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            strength_score += 1
        
        validation_result["strength_score"] = strength_score
        
        # Add suggestions for improvement
        if strength_score < 4:
            validation_result["suggestions"].append("Consider using a longer password")
            validation_result["suggestions"].append("Include a mix of uppercase, lowercase, numbers, and special characters")
        
        return validation_result
    
    def generate_jwt_token(self, user_id: str, user_data: Dict[str, Any], 
                          token_type: str = "access") -> str:
        """Generate a JWT token."""
        if not JWT_AVAILABLE:
            raise SecurityException("JWT library not available")
        
        payload = {
            "user_id": user_id,
            "token_type": token_type,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes if token_type == "access" 
                else days=self.refresh_token_expire_days
            ),
            "user_data": user_data
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        if not JWT_AVAILABLE:
            raise SecurityException("JWT library not available")
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    def generate_api_key(self, user_id: str, permissions: List[str]) -> str:
        """Generate a secure API key."""
        # Generate a random key
        random_key = secrets.token_urlsafe(32)
        
        # Create a hash of the key for storage
        key_hash = hashlib.sha256(random_key.encode()).hexdigest()
        
        # Store the hash (in a real app, this would go to the database)
        self._store_api_key_hash(user_id, key_hash, permissions)
        
        return random_key
    
    def verify_api_key(self, api_key: str, user_id: str) -> bool:
        """Verify an API key."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return self._verify_api_key_hash(user_id, key_hash)
    
    def generate_mfa_secret(self) -> str:
        """Generate a TOTP secret for MFA."""
        return base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
    
    def verify_mfa_code(self, secret: str, code: str, tolerance: int = 1) -> bool:
        """Verify a TOTP MFA code."""
        # This is a simplified implementation
        # In production, use a proper TOTP library
        try:
            code_int = int(code)
            # Basic validation - in real app, use proper TOTP verification
            return 100000 <= code_int <= 999999
        except ValueError:
            return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise SecurityException("Cryptography library not available")
        
        # Generate a key from the secret key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt_for_demo',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        
        # Encrypt the data
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise SecurityException("Cryptography library not available")
        
        # Generate the same key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'static_salt_for_demo',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        
        # Decrypt the data
        f = Fernet(key)
        decrypted_data = f.decrypt(base64.urlsafe_b64decode(encrypted_data))
        return decrypted_data.decode()
    
    def check_rate_limit(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Check if a rate limit has been exceeded."""
        current_time = time.time()
        
        if identifier not in self.failed_login_attempts:
            self.failed_login_attempts[identifier] = {
                "attempts": [],
                "locked_until": None
            }
        
        # Remove old attempts outside the window
        window_start = current_time - window_seconds
        self.failed_login_attempts[identifier]["attempts"] = [
            attempt for attempt in self.failed_login_attempts[identifier]["attempts"]
            if attempt > window_start
        ]
        
        # Check if limit exceeded
        if len(self.failed_login_attempts[identifier]["attempts"]) >= limit:
            return False
        
        return True
    
    def record_failed_attempt(self, identifier: str) -> None:
        """Record a failed authentication attempt."""
        current_time = time.time()
        
        if identifier not in self.failed_login_attempts:
            self.failed_login_attempts[identifier] = {
                "attempts": [],
                "locked_until": None
            }
        
        self.failed_login_attempts[identifier]["attempts"].append(current_time)
        
        # Check if account should be locked
        if len(self.failed_login_attempts[identifier]["attempts"]) >= self.max_login_attempts:
            lockout_until = current_time + (self.lockout_duration_minutes * 60)
            self.failed_login_attempts[identifier]["locked_until"] = lockout_until
            
            # Log security event
            self._log_security_event(
                "account_locked",
                identifier,
                f"Account locked due to {self.max_login_attempts} failed login attempts"
            )
    
    def is_account_locked(self, identifier: str) -> bool:
        """Check if an account is currently locked."""
        if identifier not in self.failed_login_attempts:
            return False
        
        locked_until = self.failed_login_attempts[identifier]["locked_until"]
        if locked_until is None:
            return False
        
        # Check if lockout period has expired
        if time.time() > locked_until:
            # Reset lockout
            self.failed_login_attempts[identifier]["locked_until"] = None
            self.failed_login_attempts[identifier]["attempts"] = []
            return False
        
        return True
    
    def check_suspicious_activity(self, user_id: str, activity_type: str, 
                                details: Dict[str, Any]) -> bool:
        """Check for suspicious activity patterns."""
        current_time = time.time()
        
        # Add activity to tracking
        self.suspicious_activities.append({
            "timestamp": current_time,
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details
        })
        
        # Remove old activities (keep last 24 hours)
        cutoff_time = current_time - (24 * 60 * 60)
        self.suspicious_activities = [
            activity for activity in self.suspicious_activities
            if activity["timestamp"] > cutoff_time
        ]
        
        # Check for suspicious patterns
        user_activities = [
            activity for activity in self.suspicious_activities
            if activity["user_id"] == user_id
        ]
        
        if len(user_activities) > self.suspicious_activity_threshold:
            self._log_security_event(
                "suspicious_activity_detected",
                user_id,
                f"High volume of activities detected: {len(user_activities)} in 24 hours"
            )
            return True
        
        return False
    
    def _store_api_key_hash(self, user_id: str, key_hash: str, permissions: List[str]) -> None:
        """Store API key hash (placeholder implementation)."""
        # In a real app, this would store to database
        logger.info(f"Stored API key hash for user {user_id}")
    
    def _verify_api_key_hash(self, user_id: str, key_hash: str) -> bool:
        """Verify API key hash (placeholder implementation)."""
        # In a real app, this would verify against database
        return True
    
    def _log_security_event(self, event_type: str, user_id: str, description: str) -> None:
        """Log a security event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "description": description,
            "ip_address": "unknown",  # Would be extracted from request
            "user_agent": "unknown"   # Would be extracted from request
        }
        
        self.security_events.append(event)
        logger.warning(f"Security event: {event_type} - {description}")

# Global security manager instance
_security_manager: Optional[SecurityManager] = None

def get_security_manager() -> SecurityManager:
    """Get the security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager

# Authentication dependencies
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get the current authenticated user from JWT token."""
    if not credentials:
        return None
    
    try:
        security_manager = get_security_manager()
        payload = security_manager.verify_jwt_token(credentials.credentials)
        
        # Extract user information from payload
        user_id = payload.get("user_id")
        user_data = payload.get("user_data", {})
        
        if not user_id:
            return None
        
        # Create user object (in real app, fetch from database)
        user = User(
            id=user_id,
            email=user_data.get("email", ""),
            username=user_data.get("username", ""),
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            access_level=user_data.get("access_level", AccessLevel.READ),
            permissions=user_data.get("permissions", []),
            governance_tier=user_data.get("governance_tier", GovernanceTier.STANDARD),
            created_by="system"
        )
        
        return user
        
    except Exception as e:
        logger.warning(f"Failed to authenticate user: {e}")
        return None

async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Get the current active user, raise error if not authenticated."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return current_user

async def get_current_super_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get the current super user, raise error if not super admin."""
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    return current_user

# Permission decorators
def require_permission(required_permissions: List[str]):
    """Decorator to require specific permissions."""
    def permission_checker(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not _has_permissions(current_user, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permissions}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return permission_checker

def require_governance_tier(required_tier: GovernanceTier):
    """Decorator to require specific governance tier."""
    def tier_checker(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not _has_governance_tier(current_user, required_tier):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient governance tier. Required: {required_tier.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return tier_checker

def require_access_level(required_level: AccessLevel):
    """Decorator to require specific access level."""
    def level_checker(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not _has_access_level(current_user, required_level):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient access level. Required: {required_level.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return level_checker

# Permission checking functions
def _has_permissions(user: User, required_permissions: List[str]) -> bool:
    """Check if user has all required permissions."""
    if not user or not user.permissions:
        return False
    
    user_permissions = set(user.permissions)
    required_permissions_set = set(required_permissions)
    
    return required_permissions_set.issubset(user_permissions)

def _has_governance_tier(user: User, required_tier: GovernanceTier) -> bool:
    """Check if user has required governance tier."""
    if not user:
        return False
    
    # Define tier hierarchy
    tier_hierarchy = {
        GovernanceTier.BASIC: 1,
        GovernanceTier.STANDARD: 2,
        GovernanceTier.ENHANCED: 3,
        GovernanceTier.ENTERPRISE: 4,
        GovernanceTier.RESTRICTED: 5
    }
    
    user_tier_level = tier_hierarchy.get(user.governance_tier, 0)
    required_tier_level = tier_hierarchy.get(required_tier, 0)
    
    return user_tier_level >= required_tier_level

def _has_access_level(user: User, required_level: AccessLevel) -> bool:
    """Check if user has required access level."""
    if not user:
        return False
    
    # Define access level hierarchy
    level_hierarchy = {
        AccessLevel.READ: 1,
        AccessLevel.WRITE: 2,
        AccessLevel.ADMIN: 3,
        AccessLevel.OWNER: 4,
        AccessLevel.SUPER_ADMIN: 5
    }
    
    user_level_value = level_hierarchy.get(user.access_level, 0)
    required_level_value = level_hierarchy.get(required_level, 0)
    
    return user_level_value >= required_level_value

# Security utilities
def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

def hash_data(data: str, salt: Optional[str] = None) -> str:
    """Hash data with optional salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    hash_obj = hashlib.sha256()
    hash_obj.update((data + salt).encode('utf-8'))
    return f"{salt}:{hash_obj.hexdigest()}"

def verify_hash(data: str, hash_string: str) -> bool:
    """Verify data against its hash."""
    try:
        salt, hash_value = hash_string.split(':', 1)
        expected_hash = hash_data(data, salt)
        return hmac.compare_digest(hash_string, expected_hash)
    except ValueError:
        return False

def sanitize_input(input_string: str) -> str:
    """Basic input sanitization."""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()

def validate_ip_address(ip_address: str) -> bool:
    """Validate IP address format."""
    import ipaddress
    
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False

def is_suspicious_ip(ip_address: str) -> bool:
    """Check if IP address is suspicious."""
    # This is a simplified implementation
    # In production, integrate with threat intelligence services
    
    suspicious_patterns = [
        '192.168.',  # Private network
        '10.',       # Private network
        '172.16.',   # Private network
        '127.0.0.1', # Localhost
        '0.0.0.0'    # Invalid
    ]
    
    return any(ip_address.startswith(pattern) for pattern in suspicious_patterns)
