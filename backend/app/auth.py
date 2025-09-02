"""
Authentication module for TaskFlow API - Handles user authentication and authorization.
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models import User
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

# SECURITY ISSUE: Hardcoded JWT secret in production code
# This should be caught by Qodo Merge as a secret leak
JWT_SECRET_KEY = "my-super-secret-jwt-key-that-should-be-very-long-and-random-12345"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

security = HTTPBearer()

class AuthManager:
    """Authentication manager for handling user authentication."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.user_service = UserService()
        logger.info("Authentication manager initialized")
    
    async def authenticate_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Authenticate user from JWT token."""
        try:
            token = credentials.credentials
            user_id = self._decode_jwt_token(token)
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is deactivated",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Update last login
            await self.user_service.update_user_last_login(user.id)
            
            logger.info(f"User {user.id} authenticated successfully")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def _decode_jwt_token(self, token: str) -> Optional[int]:
        """Decode JWT token and extract user ID (simulated)."""
        # In a real app, this would decode the actual JWT token
        # For demo purposes, we'll simulate it
        
        # SECURITY ISSUE: Weak token validation
        # This should be caught by Qodo Merge as a security risk
        if token == "valid_token_123":
            return 1  # Return admin user ID
        elif token == "manager_token_456":
            return 2  # Return manager user ID
        elif token == "user_token_789":
            return 3  # Return regular user ID
        
        # Simulate JWT decoding
        try:
            # In a real app, this would use PyJWT or similar
            # For demo, we'll just check if it looks like a JWT
            if len(token) > 20 and "." in token:
                # Extract user ID from token (simulated)
                import hashlib
                user_id_hash = hashlib.md5(token.encode()).hexdigest()
                user_id = int(user_id_hash[:8], 16) % 1000 + 1
                return user_id
        except Exception as e:
            logger.error(f"Token decoding error: {e}")
        
        return None
    
    def _encode_jwt_token(self, user_id: int) -> str:
        """Encode user ID into JWT token (simulated)."""
        # In a real app, this would encode the actual JWT token
        # For demo purposes, we'll simulate it
        
        # SECURITY ISSUE: Weak token generation
        # This should be caught by Qodo Merge as a security risk
        import hashlib
        import time
        
        payload = f"{user_id}:{int(time.time())}"
        token_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        return f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{token_hash}.{payload}"
    
    async def create_access_token(self, user: User) -> str:
        """Create access token for user."""
        logger.info(f"Creating access token for user {user.id}")
        
        token = self._encode_jwt_token(user.id)
        
        # In a real app, this would store the token in a secure way
        # For demo purposes, we'll just return it
        return token
    
    def verify_token_permissions(self, user: User, required_permissions: list) -> bool:
        """Verify if user has required permissions."""
        logger.debug(f"Verifying permissions for user {user.id}: {required_permissions}")
        
        user_permissions = self._get_user_permissions(user)
        
        for permission in required_permissions:
            if permission not in user_permissions:
                logger.warning(f"User {user.id} lacks permission: {permission}")
                return False
        
        return True
    
    def _get_user_permissions(self, user: User) -> list:
        """Get user permissions based on role."""
        base_permissions = ["read_own_tasks", "create_own_tasks"]
        
        if user.role.value == "admin":
            return base_permissions + [
                "read_all_tasks", "modify_all_tasks", "delete_all_tasks",
                "manage_users", "view_analytics", "system_admin"
            ]
        elif user.role.value == "manager":
            return base_permissions + [
                "read_team_tasks", "modify_team_tasks", "assign_tasks",
                "view_team_analytics"
            ]
        else:
            return base_permissions + ["modify_own_tasks", "delete_own_tasks"]

# Global auth manager instance
auth_manager = AuthManager()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user."""
    return await auth_manager.authenticate_user(credentials)

def require_permissions(required_permissions: list):
    """Decorator to require specific permissions."""
    def permission_checker(user: User = Depends(get_current_user)):
        if not auth_manager.verify_token_permissions(user, required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return permission_checker
