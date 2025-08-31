"""
Notification service for TaskFlow API - Handles sending notifications to users.
"""

import logging
from typing import Optional
from datetime import datetime
from app.models import Task, Notification

logger = logging.getLogger(__name__)

class NotificationService:
    """Service class for notification operations."""
    
    def __init__(self):
        """Initialize notification service."""
        self._notifications = {}
        self._notification_id_counter = 1
    
    async def notify_task_created(self, task: Task) -> Notification:
        """Send notification when a task is created."""
        logger.info(f"Sending task created notification for task {task.id}")
        
        notification = Notification(
            id=self._get_next_notification_id(),
            user_id=task.created_by,
            title="New Task Created",
            message=f"Task '{task.title}' has been created and assigned to you.",
            type="task_created",
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        # Store notification
        self._notifications[notification.id] = notification
        
        # In a real app, this would send email/SMS/push notification
        await self._send_notification(notification)
        
        return notification
    
    async def notify_task_assigned(self, task: Task, assignee_id: int) -> Notification:
        """Send notification when a task is assigned."""
        logger.info(f"Sending task assigned notification for task {task.id} to user {assignee_id}")
        
        notification = Notification(
            id=self._get_next_notification_id(),
            user_id=assignee_id,
            title="Task Assigned",
            message=f"Task '{task.title}' has been assigned to you.",
            type="task_assigned",
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        # Store notification
        self._notifications[notification.id] = notification
        
        # In a real app, this would send email/SMS/push notification
        await self._send_notification(notification)
        
        return notification
    
    async def notify_task_due_soon(self, task: Task) -> Notification:
        """Send notification when a task is due soon."""
        logger.info(f"Sending task due soon notification for task {task.id}")
        
        notification = Notification(
            id=self._get_next_notification_id(),
            user_id=task.assignee_id or task.created_by,
            title="Task Due Soon",
            message=f"Task '{task.title}' is due soon. Please review and update status.",
            type="task_due_soon",
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        # Store notification
        self._notifications[notification.id] = notification
        
        # In a real app, this would send email/SMS/push notification
        await self._send_notification(notification)
        
        return notification
    
    async def notify_task_overdue(self, task: Task) -> Notification:
        """Send notification when a task is overdue."""
        logger.info(f"Sending task overdue notification for task {task.id}")
        
        notification = Notification(
            id=self._get_next_notification_id(),
            user_id=task.assignee_id or task.created_by,
            title="Task Overdue",
            message=f"Task '{task.title}' is overdue. Please update status or request extension.",
            type="task_overdue",
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        # Store notification
        self._notifications[notification.id] = notification
        
        # In a real app, this would send email/SMS/push notification
        await self._send_notification(notification)
        
        return notification
    
    async def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        notification = self._notifications.get(notification_id)
        if notification and notification.user_id == user_id:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            logger.info(f"Notification {notification_id} marked as read by user {user_id}")
            return True
        return False
    
    async def get_user_notifications(self, user_id: int, unread_only: bool = False) -> list[Notification]:
        """Get notifications for a specific user."""
        user_notifications = [
            n for n in self._notifications.values() 
            if n.user_id == user_id
        ]
        
        if unread_only:
            user_notifications = [n for n in user_notifications if not n.is_read]
        
        # Sort by creation date (newest first)
        user_notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        return user_notifications
    
    async def _send_notification(self, notification: Notification) -> None:
        """Send notification through various channels (simulated)."""
        # In a real app, this would integrate with:
        # - Email service (SendGrid, AWS SES)
        # - SMS service (Twilio)
        # - Push notification service
        # - Slack/Teams integration
        
        logger.info(f"Notification sent: {notification.title} to user {notification.user_id}")
        
        # Simulate different notification channels based on type
        if notification.type == "task_created":
            logger.info(f"Email notification sent to user {notification.user_id}")
        elif notification.type == "task_assigned":
            logger.info(f"Push notification sent to user {notification.user_id}")
        elif notification.type == "task_due_soon":
            logger.info(f"SMS notification sent to user {notification.user_id}")
        elif notification.type == "task_overdue":
            logger.info(f"Urgent notification sent to user {notification.user_id}")
    
    def _get_next_notification_id(self) -> int:
        """Get the next available notification ID."""
        notification_id = self._notification_id_counter
        self._notification_id_counter += 1
        return notification_id
