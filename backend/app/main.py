"""
Enterprise Governance API - Main Application Entry Point
A comprehensive platform for cross-team collaboration, governance, and AI model management.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import uvicorn

from app.core.config import get_settings, Settings
from app.core.database import init_db, close_db
from app.core.security import get_current_user, get_current_active_user
from app.core.exceptions import (
    GovernanceException, 
    ComplianceException, 
    AccessControlException,
    ResourceLimitException,
    AuditException
)
from app.core.middleware import (
    GovernanceMiddleware,
    AuditMiddleware,
    RateLimitMiddleware,
    CostTrackingMiddleware,
    ComplianceMiddleware
)
from app.core.monitoring import (
    MetricsCollector,
    HealthChecker,
    PerformanceMonitor,
    ComplianceMonitor
)
from app.models.shared import (
    User, Team, Project, SharedModel, Deployment, 
    AuditLog, GovernanceConfig, AccessControl
)
from app.models.requests import (
    ModelDeploymentRequest,
    GovernanceConfigUpdateRequest,
    AccessControlRequest,
    ComplianceReportRequest,
    CostAnalysisRequest,
    TeamCollaborationRequest
)
from app.models.responses import (
    ModelDeploymentResponse,
    GovernanceConfigResponse,
    AccessControlResponse,
    ComplianceReportResponse,
    CostAnalysisResponse,
    TeamCollaborationResponse,
    HealthCheckResponse,
    MetricsResponse
)
from app.services.governance import (
    GovernanceService,
    PolicyEngine,
    ComplianceService,
    RiskAssessmentService
)
from app.services.models import (
    ModelManagementService,
    DeploymentService,
    ProviderService,
    CostOptimizationService
)
from app.services.collaboration import (
    TeamService,
    ProjectService,
    ResourceSharingService,
    ApprovalWorkflowService
)
from app.services.audit import (
    AuditService,
    ComplianceReportingService,
    GovernanceMonitoringService,
    RiskTrackingService
)
from app.services.analytics import (
    CostAnalyticsService,
    UsageAnalyticsService,
    PerformanceAnalyticsService,
    ComplianceAnalyticsService
)
from app.services.integrations import (
    ExternalProviderService,
    NotificationService,
    MonitoringService,
    BackupService
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global service instances
governance_service: Optional[GovernanceService] = None
model_service: Optional[ModelManagementService] = None
team_service: Optional[TeamService] = None
audit_service: Optional[AuditService] = None
analytics_service: Optional[CostAnalyticsService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global governance_service, model_service, team_service, audit_service, analytics_service
    
    # Startup
    logger.info("Starting Enterprise Governance API...")
    
    # Initialize database
    await init_db()
    
    # Initialize core services
    governance_service = GovernanceService()
    model_service = ModelManagementService()
    team_service = TeamService()
    audit_service = AuditService()
    analytics_service = CostAnalyticsService()
    
    # Initialize monitoring
    await initialize_monitoring()
    
    # Start background tasks
    start_background_tasks()
    
    logger.info("Enterprise Governance API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enterprise Governance API...")
    
    # Stop background tasks
    stop_background_tasks()
    
    # Close database connections
    await close_db()
    
    logger.info("Enterprise Governance API shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Enterprise Governance API",
    description=(
        "A comprehensive platform for cross-team collaboration, governance, "
        "and AI model management with enterprise-grade security and compliance."
    ),
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GovernanceMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CostTrackingMiddleware)
app.add_middleware(ComplianceMiddleware)

# Global exception handlers
@app.exception_handler(GovernanceException)
async def governance_exception_handler(request: Request, exc: GovernanceException):
    """Handle governance-related exceptions."""
    logger.error(f"Governance exception: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "Governance Policy Violation",
            "detail": exc.detail,
            "governance_tier": exc.governance_tier,
            "compliance_impact": exc.compliance_impact,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(ComplianceException)
async def compliance_exception_handler(request: Request, exc: ComplianceException):
    """Handle compliance-related exceptions."""
    logger.error(f"Compliance exception: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Compliance Violation",
            "detail": exc.detail,
            "compliance_requirement": exc.requirement,
            "risk_level": exc.risk_level,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(AccessControlException)
async def access_control_exception_handler(request: Request, exc: AccessControlException):
    """Handle access control exceptions."""
    logger.error(f"Access control exception: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "Access Denied",
            "detail": exc.detail,
            "required_permissions": exc.required_permissions,
            "user_permissions": exc.user_permissions,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(ResourceLimitException)
async def resource_limit_exception_handler(request: Request, exc: ResourceLimitException):
    """Handle resource limit exceptions."""
    logger.error(f"Resource limit exception: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Resource Limit Exceeded",
            "detail": exc.detail,
            "limit_type": exc.limit_type,
            "current_usage": exc.current_usage,
            "limit_value": exc.limit_value,
            "reset_time": exc.reset_time.isoformat() if exc.reset_time else None
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Health and monitoring endpoints
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Comprehensive health check endpoint."""
    start_time = time.time()
    
    try:
        # Check database connectivity
        db_status = await check_database_health()
        
        # Check external services
        external_status = await check_external_services()
        
        # Check governance system
        governance_status = await check_governance_health()
        
        # Check compliance status
        compliance_status = await check_compliance_health()
        
        # Calculate response time
        response_time = time.time() - start_time
        
        overall_status = "healthy" if all([
            db_status["status"] == "healthy",
            external_status["status"] == "healthy",
            governance_status["status"] == "healthy",
            compliance_status["status"] == "healthy"
        ]) else "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            response_time=response_time,
            components={
                "database": db_status,
                "external_services": external_status,
                "governance": governance_status,
                "compliance": compliance_status
            },
            version="3.0.0",
            environment=get_settings().environment
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            response_time=time.time() - start_time,
            error=str(e),
            version="3.0.0",
            environment=get_settings().environment
        )

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    current_user: User = Depends(get_current_active_user),
    period: str = "24h",
    granularity: str = "1h"
):
    """Get comprehensive system metrics."""
    try:
        # Get various metrics
        cost_metrics = await analytics_service.get_cost_metrics(period, granularity)
        usage_metrics = await analytics_service.get_usage_metrics(period, granularity)
        performance_metrics = await analytics_service.get_performance_metrics(period, granularity)
        compliance_metrics = await analytics_service.get_compliance_metrics(period, granularity)
        
        return MetricsResponse(
            period=period,
            granularity=granularity,
            timestamp=datetime.utcnow(),
            cost_metrics=cost_metrics,
            usage_metrics=usage_metrics,
            performance_metrics=performance_metrics,
            compliance_metrics=compliance_metrics
        )
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )

# Governance endpoints
@app.get("/governance/config", response_model=GovernanceConfigResponse)
async def get_governance_config(
    current_user: User = Depends(get_current_active_user)
):
    """Get current governance configuration."""
    try:
        config = await governance_service.get_configuration()
        return GovernanceConfigResponse(
            config=config,
            last_updated=config.updated_at,
            updated_by=config.updated_by
        )
    except Exception as e:
        logger.error(f"Failed to get governance config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve governance configuration: {str(e)}"
        )

@app.put("/governance/config", response_model=GovernanceConfigResponse)
async def update_governance_config(
    request: GovernanceConfigUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Update governance configuration."""
    try:
        # Validate user permissions
        if not governance_service.can_update_config(current_user):
            raise AccessControlException(
                detail="Insufficient permissions to update governance configuration",
                required_permissions=["governance:admin"],
                user_permissions=current_user.permissions
            )
        
        # Update configuration
        updated_config = await governance_service.update_configuration(request, current_user.id)
        
        # Add background task for audit logging
        background_tasks.add_task(
            audit_service.log_governance_change,
            user_id=current_user.id,
            action="update_configuration",
            details=request.dict()
        )
        
        return GovernanceConfigResponse(
            config=updated_config,
            last_updated=updated_config.updated_at,
            updated_by=updated_config.updated_by
        )
        
    except AccessControlException:
        raise
    except Exception as e:
        logger.error(f"Failed to update governance config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update governance configuration: {str(e)}"
        )

@app.get("/governance/status")
async def get_governance_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive governance status."""
    try:
        status_report = await governance_service.get_status_report(current_user.id)
        return status_report
    except Exception as e:
        logger.error(f"Failed to get governance status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve governance status: {str(e)}"
        )

# Model management endpoints
@app.post("/models/deploy", response_model=ModelDeploymentResponse)
async def deploy_model(
    request: ModelDeploymentRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Deploy a model with governance controls."""
    try:
        # Check governance requirements
        governance_check = await governance_service.check_deployment_requirements(
            current_user, request
        )
        
        if not governance_check.approved:
            raise GovernanceException(
                detail=governance_check.reason,
                governance_tier=governance_check.required_tier,
                compliance_impact=governance_check.compliance_impact
            )
        
        # Deploy the model
        deployment = await model_service.deploy_model(request, current_user.id)
        
        # Add background tasks
        background_tasks.add_task(
            audit_service.log_model_deployment,
            user_id=current_user.id,
            deployment_id=deployment.id,
            details=request.dict()
        )
        
        background_tasks.add_task(
            analytics_service.track_deployment_cost,
            deployment_id=deployment.id,
            cost_estimate=deployment.cost_estimate
        )
        
        return ModelDeploymentResponse(
            deployment=deployment,
            governance_approval_id=governance_check.approval_id,
            compliance_status=governance_check.compliance_status
        )
        
    except GovernanceException:
        raise
    except Exception as e:
        logger.error(f"Failed to deploy model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy model: {str(e)}"
        )

@app.get("/models/{model_id}/deployments")
async def get_model_deployments(
    model_id: str,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Get deployments for a specific model."""
    try:
        deployments = await model_service.get_model_deployments(
            model_id, current_user.id, skip, limit
        )
        return deployments
    except Exception as e:
        logger.error(f"Failed to get model deployments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model deployments: {str(e)}"
        )

# Team collaboration endpoints
@app.post("/teams/collaborate", response_model=TeamCollaborationResponse)
async def create_team_collaboration(
    request: TeamCollaborationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new team collaboration project."""
    try:
        collaboration = await team_service.create_collaboration(request, current_user.id)
        return TeamCollaborationResponse(collaboration=collaboration)
    except Exception as e:
        logger.error(f"Failed to create team collaboration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create team collaboration: {str(e)}"
        )

@app.get("/teams/{team_id}/collaborations")
async def get_team_collaborations(
    team_id: str,
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Get collaborations for a specific team."""
    try:
        collaborations = await team_service.get_team_collaborations(
            team_id, current_user.id, skip, limit
        )
        return collaborations
    except Exception as e:
        logger.error(f"Failed to get team collaborations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve team collaborations: {str(e)}"
        )

# Compliance and audit endpoints
@app.post("/compliance/report", response_model=ComplianceReportResponse)
async def generate_compliance_report(
    request: ComplianceReportRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate a compliance report."""
    try:
        report = await audit_service.generate_compliance_report(request, current_user.id)
        return ComplianceReportResponse(report=report)
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate compliance report: {str(e)}"
        )

@app.get("/audit/logs")
async def search_audit_logs(
    current_user: User = Depends(get_current_active_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Search audit logs with filters."""
    try:
        logs = await audit_service.search_logs(
            current_user.id,
            start_date=start_date,
            end_date=end_date,
            action=action,
            resource_type=resource_type,
            skip=skip,
            limit=limit
        )
        return logs
    except Exception as e:
        logger.error(f"Failed to search audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search audit logs: {str(e)}"
        )

# Cost analysis endpoints
@app.post("/analytics/cost", response_model=CostAnalysisResponse)
async def analyze_costs(
    request: CostAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze costs and spending patterns."""
    try:
        analysis = await analytics_service.analyze_costs(request, current_user.id)
        return CostAnalysisResponse(analysis=analysis)
    except Exception as e:
        logger.error(f"Failed to analyze costs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze costs: {str(e)}"
        )

@app.get("/analytics/usage")
async def get_usage_analytics(
    current_user: User = Depends(get_current_active_user),
    period: str = "30d",
    team_id: Optional[str] = None
):
    """Get usage analytics for the current user or team."""
    try:
        analytics = await analytics_service.get_usage_analytics(
            current_user.id, period, team_id
        )
        return analytics
    except Exception as e:
        logger.error(f"Failed to get usage analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage analytics: {str(e)}"
        )

# Utility functions
async def check_database_health() -> Dict[str, Any]:
    """Check database health status."""
    try:
        # In a real app, this would check actual database connectivity
        return {
            "status": "healthy",
            "response_time": 0.05,
            "connections": 5,
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

async def check_external_services() -> Dict[str, Any]:
    """Check external services health."""
    try:
        # In a real app, this would check actual external services
        return {
            "status": "healthy",
            "providers": {
                "openai": "healthy",
                "anthropic": "healthy",
                "google": "healthy"
            },
            "last_check": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

async def check_governance_health() -> Dict[str, Any]:
    """Check governance system health."""
    try:
        if governance_service:
            status = await governance_service.get_system_health()
            return {
                "status": "healthy" if status["overall_status"] == "healthy" else "degraded",
                "compliance_score": status["compliance_score"],
                "active_approvals": status["active_approvals"],
                "last_check": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Governance service not initialized",
                "last_check": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

async def check_compliance_health() -> Dict[str, Any]:
    """Check compliance system health."""
    try:
        if audit_service:
            stats = await audit_service.get_audit_statistics()
            return {
                "status": "healthy" if stats["compliance_score"] >= 90 else "degraded",
                "compliance_score": stats["compliance_score"],
                "governance_violations": stats["governance_violations"],
                "last_check": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Audit service not initialized",
                "last_check": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

async def initialize_monitoring():
    """Initialize monitoring systems."""
    try:
        # Initialize metrics collector
        metrics_collector = MetricsCollector()
        await metrics_collector.start()
        
        # Initialize health checker
        health_checker = HealthChecker()
        await health_checker.start()
        
        # Initialize performance monitor
        performance_monitor = PerformanceMonitor()
        await performance_monitor.start()
        
        # Initialize compliance monitor
        compliance_monitor = ComplianceMonitor()
        await compliance_monitor.start()
        
        logger.info("Monitoring systems initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {e}")

def start_background_tasks():
    """Start background tasks."""
    try:
        # Start various background tasks
        logger.info("Background tasks started")
    except Exception as e:
        logger.error(f"Failed to start background tasks: {e}")

def stop_background_tasks():
    """Stop background tasks."""
    try:
        # Stop various background tasks
        logger.info("Background tasks stopped")
    except Exception as e:
        logger.error(f"Failed to stop background tasks: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
