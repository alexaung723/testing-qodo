"""
Governance middleware for enforcing access controls and governance policies.
This middleware ensures consistent governance across all API endpoints.
"""

import logging
import time
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.governance_service import GovernanceService
from app.services.audit_service import AuditService
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

class GovernanceMiddleware:
    """Middleware for enforcing governance policies and access controls."""
    
    def __init__(self):
        """Initialize governance middleware."""
        self.governance_service = GovernanceService()
        self.audit_service = AuditService()
        self.settings = get_settings()
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process the request through governance middleware."""
        start_time = time.time()
        
        # Extract request information
        user_id = self._extract_user_id(request)
        endpoint = str(request.url.path)
        method = request.method
        resource_type = self._determine_resource_type(endpoint)
        
        # Log the request for audit purposes
        await self._audit_request(request, user_id, endpoint, method, resource_type)
        
        # Apply governance checks
        governance_check = await self._apply_governance_checks(
            request, user_id, endpoint, method, resource_type
        )
        
        if not governance_check['allowed']:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Governance policy violation",
                    "reason": governance_check['reason'],
                    "governance_tier": governance_check['governance_tier'],
                    "compliance_impact": governance_check['compliance_impact']
                }
            )
        
        # Apply rate limiting if enabled
        if self.settings.rate_limit_enabled:
            rate_limit_check = await self._check_rate_limits(user_id, endpoint)
            if not rate_limit_check['allowed']:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "reason": rate_limit_check['reason'],
                        "retry_after": rate_limit_check['retry_after']
                    }
                )
        
        # Apply usage limits
        usage_check = await self._check_usage_limits(user_id, endpoint)
        if not usage_check['allowed']:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Usage limit exceeded",
                    "reason": usage_check['reason'],
                    "limit_type": usage_check['limit_type']
                }
            )
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add governance headers to response
            response.headers["X-Governance-Tier"] = governance_check['governance_tier']
            response.headers["X-Compliance-Impact"] = governance_check['compliance_impact']
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log successful response
            await self._audit_response(
                request, response, user_id, endpoint, method, 
                resource_type, process_time, governance_check
            )
            
            return response
            
        except Exception as e:
            # Log error for audit purposes
            await self._audit_error(
                request, e, user_id, endpoint, method, resource_type
            )
            raise
    
    async def _audit_request(
        self, 
        request: Request, 
        user_id: str, 
        endpoint: str, 
        method: str, 
        resource_type: str
    ):
        """Audit the incoming request."""
        try:
            # Extract additional request details
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            
            # Determine compliance impact
            compliance_impact = self._determine_compliance_impact(endpoint, method)
            
            # Log the request
            await self.audit_service.log_access(
                user_id=user_id or "anonymous",
                endpoint=endpoint,
                action=f"{method.lower()}_{resource_type}",
                resource_type=resource_type,
                details={
                    "method": method,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "compliance_impact": compliance_impact,
                    "timestamp": time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to audit request: {e}")
    
    async def _apply_governance_checks(
        self, 
        request: Request, 
        user_id: str, 
        endpoint: str, 
        method: str, 
        resource_type: str
    ) -> Dict[str, Any]:
        """Apply governance policy checks to the request."""
        try:
            # Check if endpoint requires authentication
            if self._requires_authentication(endpoint) and not user_id:
                return {
                    'allowed': False,
                    'reason': 'Authentication required',
                    'governance_tier': 'standard',
                    'compliance_impact': 'medium'
                }
            
            # Check if endpoint is restricted
            if self._is_restricted_endpoint(endpoint):
                if not self._has_restricted_access(user_id):
                    return {
                        'allowed': False,
                        'reason': 'Access to restricted endpoint denied',
                        'governance_tier': 'critical',
                        'compliance_impact': 'high'
                    }
            
            # Check governance tier requirements
            governance_tier = self._determine_governance_tier(endpoint, method)
            if governance_tier == 'critical':
                if not self._has_critical_access(user_id):
                    return {
                        'allowed': False,
                        'reason': 'Critical governance tier access denied',
                        'governance_tier': 'critical',
                        'compliance_impact': 'high'
                    }
            
            # Check compliance requirements
            compliance_impact = self._determine_compliance_impact(endpoint, method)
            if compliance_impact == 'high':
                if not self._has_compliance_access(user_id):
                    return {
                        'allowed': False,
                        'reason': 'High compliance impact access denied',
                        'governance_tier': governance_tier,
                        'compliance_impact': 'high'
                    }
            
            # All checks passed
            return {
                'allowed': True,
                'reason': 'Access granted',
                'governance_tier': governance_tier,
                'compliance_impact': compliance_impact
            }
            
        except Exception as e:
            logger.error(f"Governance check failed: {e}")
            return {
                'allowed': False,
                'reason': 'Governance check failed',
                'governance_tier': 'critical',
                'compliance_impact': 'high'
            }
    
    async def _check_rate_limits(self, user_id: str, endpoint: str) -> Dict[str, Any]:
        """Check if request is within rate limits."""
        try:
            # In a real app, this would check actual rate limits
            # For demo purposes, we'll return a mock result
            return {
                'allowed': True,
                'reason': 'Rate limit check passed',
                'retry_after': None
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return {
                'allowed': False,
                'reason': 'Rate limit check failed',
                'retry_after': 60
            }
    
    async def _check_usage_limits(self, user_id: str, endpoint: str) -> Dict[str, Any]:
        """Check if request is within usage limits."""
        try:
            # In a real app, this would check actual usage limits
            # For demo purposes, we'll return a mock result
            return {
                'allowed': True,
                'reason': 'Usage limit check passed',
                'limit_type': None
            }
            
        except Exception as e:
            logger.error(f"Usage limit check failed: {e}")
            return {
                'allowed': False,
                'reason': 'Usage limit check failed',
                'limit_type': 'daily'
            }
    
    async def _audit_response(
        self, 
        request: Request, 
        response: Response, 
        user_id: str, 
        endpoint: str, 
        method: str, 
        resource_type: str, 
        process_time: float, 
        governance_check: Dict[str, Any]
    ):
        """Audit the successful response."""
        try:
            # Log the successful response
            await self.audit_service.log_access(
                user_id=user_id or "anonymous",
                endpoint=endpoint,
                action=f"{method.lower()}_{resource_type}_success",
                resource_type=resource_type,
                details={
                    "method": method,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "governance_tier": governance_check['governance_tier'],
                    "compliance_impact": governance_check['compliance_impact'],
                    "timestamp": time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to audit response: {e}")
    
    async def _audit_error(
        self, 
        request: Request, 
        error: Exception, 
        user_id: str, 
        endpoint: str, 
        method: str, 
        resource_type: str
    ):
        """Audit the error response."""
        try:
            # Log the error
            await self.audit_service.log_access(
                user_id=user_id or "anonymous",
                endpoint=endpoint,
                action=f"{method.lower()}_{resource_type}_error",
                resource_type=resource_type,
                details={
                    "method": method,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "compliance_impact": "high",
                    "timestamp": time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to audit error: {e}")
    
    def _extract_user_id(self, request: Request) -> str:
        """Extract user ID from the request."""
        # Check for JWT token in Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            # In a real app, this would decode the JWT token
            # For demo purposes, return a mock user ID
            return "user123"
        
        # Check for user ID in query parameters
        user_id = request.query_params.get("user_id")
        if user_id:
            return user_id
        
        # Check for user ID in headers
        user_id = request.headers.get("x-user-id")
        if user_id:
            return user_id
        
        return None
    
    def _determine_resource_type(self, endpoint: str) -> str:
        """Determine the resource type from the endpoint."""
        if "/governance/" in endpoint:
            return "governance"
        elif "/shared/" in endpoint:
            return "shared_resource"
        elif "/models/" in endpoint:
            return "model"
        elif "/audit/" in endpoint:
            return "audit"
        elif "/access/" in endpoint:
            return "access_control"
        elif "/usage/" in endpoint:
            return "usage_metrics"
        else:
            return "api_endpoint"
    
    def _determine_governance_tier(self, endpoint: str, method: str) -> str:
        """Determine the governance tier for the endpoint."""
        # Critical endpoints
        if any(critical in endpoint for critical in ["/governance/config", "/models/switch-provider"]):
            return "critical"
        
        # Enhanced endpoints
        if any(enhanced in endpoint for enhanced in ["/governance/", "/audit/", "/access/"]):
            return "enhanced"
        
        # Standard endpoints
        return "standard"
    
    def _determine_compliance_impact(self, endpoint: str, method: str) -> str:
        """Determine the compliance impact of the endpoint."""
        # High impact endpoints
        if any(high in endpoint for high in ["/governance/config", "/models/switch-provider", "/audit/search"]):
            return "high"
        
        # Medium impact endpoints
        if any(medium in endpoint for medium in ["/governance/", "/shared/", "/access/"]):
            return "medium"
        
        # Low impact endpoints
        return "low"
    
    def _requires_authentication(self, endpoint: str) -> bool:
        """Check if endpoint requires authentication."""
        # Public endpoints
        public_endpoints = ["/health", "/docs", "/openapi.json"]
        if endpoint in public_endpoints:
            return False
        
        # All other endpoints require authentication
        return True
    
    def _is_restricted_endpoint(self, endpoint: str) -> bool:
        """Check if endpoint is restricted."""
        restricted_endpoints = [
            "/governance/config",
            "/models/switch-provider",
            "/audit/search",
            "/access/controls"
        ]
        
        return any(restricted in endpoint for restricted in restricted_endpoints)
    
    def _has_restricted_access(self, user_id: str) -> bool:
        """Check if user has access to restricted endpoints."""
        # In a real app, this would check user permissions
        # For demo purposes, return True for authenticated users
        return user_id is not None
    
    def _has_critical_access(self, user_id: str) -> bool:
        """Check if user has access to critical governance tier."""
        # In a real app, this would check user permissions
        # For demo purposes, return True for authenticated users
        return user_id is not None
    
    def _has_compliance_access(self, user_id: str) -> bool:
        """Check if user has access to high compliance impact endpoints."""
        # In a real app, this would check user permissions
        # For demo purposes, return True for authenticated users
        return user_id is not None
