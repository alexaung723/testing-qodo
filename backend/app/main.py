from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
from datetime import datetime, timedelta
from app.models import Task, TaskCreate, TaskUpdate, User, UserCreate
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.database import get_db
from app.auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TaskFlow API",
    description="Enterprise task management system for teams",
    version="2.1.0"
)

# SECURITY ISSUE: Hardcoded database credentials in production code
# This should be caught by Qodo Merge as a secret leak
DB_HOST = "prod-taskflow-db.cluster.us-west-2.rds.amazonaws.com"
DB_USER = "taskflow_admin"
DB_PASSWORD = "T@skFl0w2024!Pr0d"  # This is a real secret leak
DB_NAME = "taskflow_production"

# SECURITY ISSUE: Hardcoded API keys
STRIPE_SECRET_KEY = "sk_live_51H1234567890abcdefghijklmnopqrstuvwxyz"  # Live key in code
SENDGRID_API_KEY = "SG.1234567890abcdefghijklmnopqrstuvwxyz.1234567890abcdefghijklmnopqrstuvwxyz"

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.1.0",
        "environment": os.getenv("ENV", "development")
    }

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Create a new task."""
    logger.info(f"Creating task '{task.title}' for user {current_user.email}")
    
    # Business logic: Check if user can create tasks
    if not current_user.can_create_tasks:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to create tasks"
        )
    
    # Create the task
    created_task = await task_service.create_task(task, current_user.id)
    
    # Send notification
    notification_service = NotificationService()
    await notification_service.notify_task_created(created_task)
    
    return created_task

@app.get("/tasks", response_model=List[Task])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Get tasks with optional filtering."""
    logger.info(f"User {current_user.email} requesting tasks with filters: status={status_filter}, priority={priority_filter}")
    
    tasks = await task_service.get_tasks(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status_filter,
        priority=priority_filter
    )
    
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Get a specific task by ID."""
    task = await task_service.get_task(task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Update an existing task."""
    logger.info(f"User {current_user.email} updating task {task_id}")
    
    # Check if user can modify this task
    existing_task = await task_service.get_task(task_id, current_user.id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not existing_task.can_be_modified_by(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to modify this task"
        )
    
    updated_task = await task_service.update_task(task_id, task_update, current_user.id)
    return updated_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Delete a task."""
    logger.info(f"User {current_user.email} deleting task {task_id}")
    
    # Check if user can delete this task
    existing_task = await task_service.get_task(task_id, current_user.id)
    if not existing_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if not existing_task.can_be_deleted_by(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to delete this task"
        )
    
    await task_service.delete_task(task_id, current_user.id)

@app.post("/tasks/{task_id}/assign")
async def assign_task(
    task_id: int,
    assignee_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Assign a task to another user."""
    logger.info(f"User {current_user.email} assigning task {task_id} to user {assignee_id}")
    
    if not current_user.can_assign_tasks:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to assign tasks"
        )
    
    assigned_task = await task_service.assign_task(task_id, assignee_id, current_user.id)
    
    # Send notification to assignee
    notification_service = NotificationService()
    await notification_service.notify_task_assigned(assigned_task, assignee_id)
    
    return {"message": "Task assigned successfully", "task": assigned_task}

@app.get("/users/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@app.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    """Get user's task statistics."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    task_service = TaskService()
    stats = await task_service.get_user_stats(current_user.id)
    
    return {
        "total_tasks": stats.total_tasks,
        "completed_tasks": stats.completed_tasks,
        "overdue_tasks": stats.overdue_tasks,
        "completion_rate": stats.completion_rate,
        "average_completion_time": stats.average_completion_time
    }

# SECURITY ISSUE: Debug endpoint that logs sensitive information
@app.get("/debug/connection")
async def debug_connection():
    """Debug endpoint - SECURITY RISK: Logs database credentials"""
    logger.warning(f"Database connection test: {DB_HOST}:{DB_USER}:{DB_PASSWORD}")
    
    return {
        "message": "Connection test completed",
        "host": DB_HOST,
        "database": DB_NAME,
        "status": "connected"
    }
