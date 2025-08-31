"""
Audit service for logging and tracking all system actions.
This service ensures compliance and provides audit trails.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.models.shared import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    """Service for managing audit logs and compliance tracking."""
    
    def __init__(self):
        """Initialize audit service."""
        self._audit_logs = []
        self._log_counter = 1
    
    async def log_access(
        self, 
        user_id: str, 
        endpoint: str, 
        action: str, 
        resource_type: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an access action for audit purposes."""
        log_entry = AuditLog(
            id=str(self._log_counter),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            endpoint=endpoint,
            details=details or {},
            compliance_impact="low",
            governance_tier="standard",
            entity_type="audit_log"
        )
        
        self._log_counter += 1
        self._audit_logs.append(log_entry)
        
        logger.info(f"Audit log created: {action} by user {user_id} on {resource_type}")
        return log_entry.id
    
    async def search_logs(self, search_params: Dict[str, Any]) -> List[AuditLog]:
        """Search audit logs based on parameters."""
        logger.info(f"Searching audit logs with params: {search_params}")
        
        # Apply filters
        filtered_logs = self._audit_logs
        
        # Filter by user ID
        if 'user_id' in search_params:
            filtered_logs = [log for log in filtered_logs 
                           if log.user_id == search_params['user_id']]
        
        # Filter by action
        if 'action' in search_params:
            filtered_logs = [log for log in filtered_logs 
                           if log.action == search_params['action']]
        
        # Filter by resource type
        if 'resource_type' in search_params:
            filtered_logs = [log for log in filtered_logs 
                           if log.resource_type == search_params['resource_type']]
        
        # Filter by date range
        if 'start_date' in search_params or 'end_date' in search_params:
            start_date = search_params.get('start_date')
            end_date = search_params.get('end_date')
            
            if start_date:
                filtered_logs = [log for log in filtered_logs 
                               if log.created_at >= start_date]
            
            if end_date:
                filtered_logs = [log for log in filtered_logs 
                               if log.created_at <= end_date]
        
        # Filter by compliance impact
        if 'compliance_impact' in search_params:
            filtered_logs = [log for log in filtered_logs 
                           if log.compliance_impact == search_params['compliance_impact']]
        
        # Filter by governance tier
        if 'governance_tier' in search_params:
            filtered_logs = [log for log in filtered_logs 
                           if log.governance_tier == search_params['governance_tier']]
        
        # Sort by creation date (newest first)
        filtered_logs.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        limit = search_params.get('limit', 100)
        offset = search_params.get('offset', 0)
        
        paginated_logs = filtered_logs[offset:offset + limit]
        
        logger.info(f"Found {len(filtered_logs)} logs, returning {len(paginated_logs)}")
        return paginated_logs
    
    async def get_user_activity(self, user_id: str, days: int = 30) -> List[AuditLog]:
        """Get activity for a specific user over a time period."""
        logger.info(f"Getting activity for user {user_id} over {days} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        user_logs = [
            log for log in self._audit_logs
            if log.user_id == user_id and log.created_at >= cutoff_date
        ]
        
        # Sort by creation date (newest first)
        user_logs.sort(key=lambda x: x.created_at, reverse=True)
        
        logger.info(f"Found {len(user_logs)} activity logs for user {user_id}")
        return user_logs
    
    async def get_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for a date range."""
        logger.info(f"Generating compliance report from {start_date} to {end_date}")
        
        # Filter logs by date range
        range_logs = [
            log for log in self._audit_logs
            if start_date <= log.created_at <= end_date
        ]
        
        # Calculate compliance metrics
        total_actions = len(range_logs)
        high_impact_actions = len([log for log in range_logs if log.is_high_impact])
        critical_tier_actions = len([log for log in range_logs if log.governance_tier == "critical"])
        actions_requiring_review = len([log for log in range_logs if log.requires_review])
        
        # Calculate compliance score
        compliance_score = 100.0
        if total_actions > 0:
            # Deduct points for high-impact actions and critical tier actions
            compliance_score -= (high_impact_actions / total_actions) * 10
            compliance_score -= (critical_tier_actions / total_actions) * 15
        
        compliance_score = max(0.0, compliance_score)
        
        # Group by resource type
        resource_type_counts = {}
        for log in range_logs:
            resource_type = log.resource_type
            resource_type_counts[resource_type] = resource_type_counts.get(resource_type, 0) + 1
        
        # Group by action type
        action_counts = {}
        for log in range_logs:
            action = log.action
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Group by user
        user_counts = {}
        for log in range_logs:
            user_id = log.user_id
            user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        report = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": (end_date - start_date).days
            },
            "summary": {
                "total_actions": total_actions,
                "high_impact_actions": high_impact_actions,
                "critical_tier_actions": critical_tier_actions,
                "actions_requiring_review": actions_requiring_review,
                "compliance_score": round(compliance_score, 2)
            },
            "breakdown": {
                "by_resource_type": resource_type_counts,
                "by_action": action_counts,
                "by_user": user_counts
            },
            "recommendations": self._generate_compliance_recommendations(range_logs, compliance_score)
        }
        
        logger.info(f"Compliance report generated with score: {compliance_score}")
        return report
    
    async def get_governance_violations(self, days: int = 30) -> List[AuditLog]:
        """Get governance violations over a time period."""
        logger.info(f"Getting governance violations over {days} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        violations = [
            log for log in self._audit_logs
            if log.created_at >= cutoff_date and (
                log.is_high_impact or 
                log.governance_tier == "critical" or
                log.requires_review
            )
        ]
        
        # Sort by creation date (newest first)
        violations.sort(key=lambda x: x.created_at, reverse=True)
        
        logger.info(f"Found {len(violations)} governance violations")
        return violations
    
    async def export_audit_logs(self, format: str = "json", filters: Optional[Dict[str, Any]] = None) -> str:
        """Export audit logs in specified format."""
        logger.info(f"Exporting audit logs in {format} format")
        
        # Apply filters if provided
        logs_to_export = self._audit_logs
        if filters:
            logs_to_export = await self.search_logs(filters)
        
        if format.lower() == "json":
            # Convert to JSON format
            export_data = []
            for log in logs_to_export:
                export_data.append({
                    "id": log.id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "endpoint": log.endpoint,
                    "created_at": log.created_at.isoformat(),
                    "compliance_impact": log.compliance_impact,
                    "governance_tier": log.governance_tier,
                    "details": log.details
                })
            
            import json
            return json.dumps(export_data, indent=2)
        
        elif format.lower() == "csv":
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "User ID", "Action", "Resource Type", "Endpoint", 
                "Created At", "Compliance Impact", "Governance Tier", "Details"
            ])
            
            # Write data
            for log in logs_to_export:
                writer.writerow([
                    log.id,
                    log.user_id,
                    log.action,
                    log.resource_type,
                    log.endpoint,
                    log.created_at.isoformat(),
                    log.compliance_impact,
                    log.governance_tier,
                    str(log.details)
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _generate_compliance_recommendations(self, logs: List[AuditLog], compliance_score: float) -> List[str]:
        """Generate compliance recommendations based on audit logs."""
        recommendations = []
        
        if compliance_score < 90:
            recommendations.append("Review high-impact actions and implement additional controls")
        
        if compliance_score < 80:
            recommendations.append("Implement mandatory training for users with frequent violations")
        
        # Check for specific patterns
        high_impact_count = len([log for log in logs if log.is_high_impact])
        if high_impact_count > len(logs) * 0.1:  # More than 10% are high impact
            recommendations.append("Review approval workflows for high-impact actions")
        
        critical_tier_count = len([log for log in logs if log.governance_tier == "critical"])
        if critical_tier_count > 0:
            recommendations.append("Implement additional controls for critical governance tier actions")
        
        # Check for users with many actions
        user_action_counts = {}
        for log in logs:
            user_action_counts[log.user_id] = user_action_counts.get(log.user_id, 0) + 1
        
        high_activity_users = [
            user_id for user_id, count in user_action_counts.items()
            if count > len(logs) * 0.2  # More than 20% of all actions
        ]
        
        if high_activity_users:
            recommendations.append(f"Review access levels for high-activity users: {', '.join(high_activity_users)}")
        
        if not recommendations:
            recommendations.append("No specific recommendations - compliance is good")
        
        return recommendations
    
    async def cleanup_old_logs(self, retention_days: int) -> int:
        """Clean up audit logs older than retention period."""
        logger.info(f"Cleaning up audit logs older than {retention_days} days")
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Count logs to be removed
        logs_to_remove = [log for log in self._audit_logs if log.created_at < cutoff_date]
        removed_count = len(logs_to_remove)
        
        # Remove old logs
        self._audit_logs = [log for log in self._audit_logs if log.created_at >= cutoff_date]
        
        logger.info(f"Removed {removed_count} old audit logs")
        return removed_count
    
    async def get_audit_statistics(self) -> Dict[str, Any]:
        """Get audit service statistics."""
        total_logs = len(self._audit_logs)
        
        if total_logs == 0:
            return {
                "total_logs": 0,
                "logs_today": 0,
                "logs_this_week": 0,
                "logs_this_month": 0,
                "compliance_score": 100.0,
                "governance_violations": 0
            }
        
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        logs_today = len([log for log in self._audit_logs if log.created_at >= today])
        logs_this_week = len([log for log in self._audit_logs if log.created_at >= week_ago])
        logs_this_month = len([log for log in self._audit_logs if log.created_at >= month_ago])
        
        # Calculate compliance score
        high_impact_count = len([log for log in self._audit_logs if log.is_high_impact])
        critical_tier_count = len([log for log in self._audit_logs if log.governance_tier == "critical"])
        
        compliance_score = 100.0
        if total_logs > 0:
            compliance_score -= (high_impact_count / total_logs) * 10
            compliance_score -= (critical_tier_count / total_logs) * 15
        
        compliance_score = max(0.0, compliance_score)
        
        # Count governance violations
        governance_violations = len([
            log for log in self._audit_logs
            if log.is_high_impact or log.governance_tier == "critical"
        ])
        
        return {
            "total_logs": total_logs,
            "logs_today": logs_today,
            "logs_this_week": logs_this_week,
            "logs_this_month": logs_this_month,
            "compliance_score": round(compliance_score, 2),
            "governance_violations": governance_violations,
            "retention_policy": "365 days",
            "export_formats": ["json", "csv"]
        }
