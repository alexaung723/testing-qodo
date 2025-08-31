"""
Access control functions for enforcing permissions and governance policies.
These functions ensure consistent access control across the application.
"""

import logging
from typing import Callable, List, Optional
from functools import wraps
from fastapi import Depends, HTTPException, status
from app.models.shared import User
from app.services.governance_service import GovernanceService

logger = logging.getLogger(__name__)

def require_permission(required_permissions: List[str]):
    """
    Decorator to require specific permissions for access.
    
    Args:
        required_permissions: List of permissions required for access
        
    Returns:
        Decorated function that checks permissions
    """
    def permission_checker(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from args if it's the first argument
                if args and hasattr(args[0], 'current_user'):
                    current_user = args[0].current_user
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
            
            # Check if user has required permissions
            if not _has_permissions(current_user, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permissions}"
                )
            
            # Check governance requirements
            governance_check = await _check_governance_requirements(
                current_user, 
                required_permissions
            )
            
            if not governance_check['allowed']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Governance policy violation: {governance_check['reason']}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return permission_checker

def require_governance_tier(minimum_tier: str):
    """
    Decorator to require minimum governance tier for access.
    
    Args:
        minimum_tier: Minimum governance tier required (standard, enhanced, critical)
        
    Returns:
        Decorated function that checks governance tier
    """
    def tier_checker(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from args if it's the first argument
                if args and hasattr(args[0], 'current_user'):
                    current_user = args[0].current_user
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
            
            # Check governance tier
            if not _has_governance_tier(current_user, minimum_tier):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient governance tier. Required: {minimum_tier}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return tier_checker

def require_team_access(team_ids: List[str]):
    """
    Decorator to require access to specific teams.
    
    Args:
        team_ids: List of team IDs user must have access to
        
    Returns:
        Decorated function that checks team access
    """
    def team_checker(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from args if it's the first argument
                if args and hasattr(args[0], 'current_user'):
                    current_user = args[0].current_user
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
            
            # Check team access
            if not _has_team_access(current_user, team_ids):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient team access. Required teams: {team_ids}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return team_checker

def require_department_access(departments: List[str]):
    """
    Decorator to require access to specific departments.
    
    Args:
        departments: List of departments user must have access to
        
    Returns:
        Decorated function that checks department access
    """
    def department_checker(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from args if it's the first argument
                if args and hasattr(args[0], 'current_user'):
                    current_user = args[0].current_user
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
            
            # Check department access
            if not _has_department_access(current_user, departments):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient department access. Required departments: {departments}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return department_checker

def require_approval_for_cost(cost_threshold: float):
    """
    Decorator to require approval for operations above cost threshold.
    
    Args:
        cost_threshold: Cost threshold above which approval is required
        
    Returns:
        Decorated function that checks cost approval
    """
    def cost_checker(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                # Try to get from args if it's the first argument
                if args and hasattr(args[0], 'current_user'):
                    current_user = args[0].current_user
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
            
            # Check if cost approval is required
            cost_approval_check = await _check_cost_approval(
                current_user, 
                cost_threshold
            )
            
            if cost_approval_check['required']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Cost approval required. Threshold: ${cost_threshold}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return cost_checker

async def get_current_user() -> User:
    """
    Dependency function to get the current authenticated user.
    
    Returns:
        Current user object
        
    Raises:
        HTTPException: If user is not authenticated
    """
    # In a real app, this would extract user from JWT token
    # For demo purposes, return a mock user
    return User(
        id="current_user",
        email="user@example.com",
        first_name="Current",
        last_name="User",
        access_level="write",
        permissions=["governance:read", "models:deploy", "audit:read"],
        team_id="team1",
        department="engineering",
        entity_type="user"
    )

def _has_permissions(user: User, required_permissions: List[str]) -> bool:
    """
    Check if user has all required permissions.
    
    Args:
        user: User object to check
        required_permissions: List of permissions required
        
    Returns:
        True if user has all required permissions, False otherwise
    """
    if not user or not user.permissions:
        return False
    
    user_permissions = set(user.permissions)
    required_permissions_set = set(required_permissions)
    
    return required_permissions_set.issubset(user_permissions)

def _has_governance_tier(user: User, minimum_tier: str) -> bool:
    """
    Check if user has minimum required governance tier.
    
    Args:
        user: User object to check
        minimum_tier: Minimum governance tier required
        
    Returns:
        True if user has sufficient governance tier, False otherwise
    """
    if not user:
        return False
    
    # Define tier hierarchy
    tier_hierarchy = {
        "standard": 1,
        "enhanced": 2,
        "critical": 3
    }
    
    user_tier = tier_hierarchy.get(user.governance_tier, 0)
    required_tier = tier_hierarchy.get(minimum_tier, 0)
    
    return user_tier >= required_tier

def _has_team_access(user: User, required_team_ids: List[str]) -> bool:
    """
    Check if user has access to required teams.
    
    Args:
        user: User object to check
        required_team_ids: List of team IDs required
        
    Returns:
        True if user has access to required teams, False otherwise
    """
    if not user:
        return False
    
    # Check if user's team is in required teams
    if user.team_id in required_team_ids:
        return True
    
    # Check if user has admin access
    if user.access_level.value in ["admin", "owner"]:
        return True
    
    return False

def _has_department_access(user: User, required_departments: List[str]) -> bool:
    """
    Check if user has access to required departments.
    
    Args:
        user: User object to check
        required_departments: List of departments required
        
    Returns:
        True if user has access to required departments, False otherwise
    """
    if not user:
        return False
    
    # Check if user's department is in required departments
    if user.department in required_departments:
        return True
    
    # Check if user has admin access
    if user.access_level.value in ["admin", "owner"]:
        return True
    
    return False

async def _check_governance_requirements(user: User, permissions: List[str]) -> dict:
    """
    Check if user meets governance requirements for the requested permissions.
    
    Args:
        user: User object to check
        permissions: List of permissions being requested
        
    Returns:
        Dictionary with 'allowed' boolean and 'reason' string
    """
    try:
        governance_service = GovernanceService()
        
        # Check if any permissions require enhanced governance
        enhanced_permissions = [
            "governance:write", 
            "models:admin", 
            "audit:write"
        ]
        
        requires_enhanced = any(perm in enhanced_permissions for perm in permissions)
        
        if requires_enhanced and user.governance_tier == "standard":
            return {
                'allowed': False,
                'reason': 'Enhanced governance tier required for requested permissions'
            }
        
        # Check if any permissions require critical governance
        critical_permissions = [
            "governance:admin", 
            "compliance:admin", 
            "security:admin"
        ]
        
        requires_critical = any(perm in critical_permissions for perm in permissions)
        
        if requires_critical and user.governance_tier != "critical":
            return {
                'allowed': False,
                'reason': 'Critical governance tier required for requested permissions'
            }
        
        return {
            'allowed': True,
            'reason': 'Governance requirements met'
        }
        
    except Exception as e:
        logger.error(f"Governance requirement check failed: {e}")
        return {
            'allowed': False,
            'reason': 'Governance check failed'
        }

async def _check_cost_approval(user: User, cost_threshold: float) -> dict:
    """
    Check if cost approval is required for the user.
    
    Args:
        user: User object to check
        cost_threshold: Cost threshold to check against
        
    Returns:
        Dictionary with 'required' boolean and additional details
    """
    try:
        governance_service = GovernanceService()
        
        # Get user's governance configuration
        config = await governance_service.get_config()
        if not config:
            return {
                'required': False,
                'reason': 'No governance configuration found'
            }
        
        # Check if user has auto-approval limit
        if config.auto_approval_limit and cost_threshold <= config.auto_approval_limit:
            return {
                'required': False,
                'reason': 'Within auto-approval limit'
            }
        
        # Check if user has admin access (bypass approval)
        if user.access_level.value in ["admin", "owner"]:
            return {
                'required': False,
                'reason': 'Admin access bypasses approval'
            }
        
        return {
            'required': True,
            'reason': f'Cost {cost_threshold} exceeds auto-approval limit {config.auto_approval_limit}'
        }
        
    except Exception as e:
        logger.error(f"Cost approval check failed: {e}")
        return {
            'required': True,
            'reason': 'Cost approval check failed'
        }

def validate_resource_access(user: User, resource_type: str, resource_id: str) -> bool:
    """
    Validate if user has access to a specific resource.
    
    Args:
        user: User object to check
        resource_type: Type of resource being accessed
        resource_id: ID of the resource being accessed
        
    Returns:
        True if user has access, False otherwise
    """
    if not user:
        return False
    
    # Admin users have access to all resources
    if user.access_level.value in ["admin", "owner"]:
        return True
    
    # Check resource-specific access rules
    if resource_type == "governance_config":
        return "governance:read" in user.permissions
    
    elif resource_type == "shared_model":
        return "models:read" in user.permissions
    
    elif resource_type == "audit_log":
        return "audit:read" in user.permissions
    
    elif resource_type == "access_control":
        return "access:read" in user.permissions
    
    # Default: deny access
    return False

def get_user_permissions(user: User) -> List[str]:
    """
    Get all permissions for a user.
    
    Args:
        user: User object to get permissions for
        
    Returns:
        List of user permissions
    """
    if not user:
        return []
    
    return user.permissions or []

def get_user_access_level(user: User) -> str:
    """
    Get the access level for a user.
    
    Args:
        user: User object to get access level for
        
    Returns:
        User's access level
    """
    if not user:
        return "none"
    
    return user.access_level.value if user.access_level else "none"

def get_user_governance_tier(user: User) -> str:
    """
    Get the governance tier for a user.
    
    Args:
        user: User object to get governance tier for
        
    Returns:
        User's governance tier
    """
    if not user:
        return "none"
    
    return user.governance_tier or "standard"
