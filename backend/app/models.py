"""
Data models for TaskFlow API - Enterprise task management system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

class TaskBase(BaseModel):
    """Base task model with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    estimated_hours: Optional[float] = Field(None, ge=0, description="Estimated hours to complete")
    tags: List[str] = Field(default_factory=list, description="Task tags")

class TaskCreate(TaskBase):
    """Model for creating a new task."""
    assignee_id: Optional[int] = Field(None, description="User ID to assign the task to")
    project_id: Optional[int] = Field(None, description="Project ID this task belongs to")

class TaskUpdate(BaseModel):
    """Model for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None

class Task(TaskBase):
    """Complete task model."""
    id: int = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Current task status")
    created_by: int = Field(..., description="User ID who created the task")
    assignee_id: Optional[int] = Field(None, description="User ID assigned to the task")
    project_id: Optional[int] = Field(None, description="Project ID this task belongs to")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    
    # Computed fields
    is_overdue: bool = Field(..., description="Whether the task is overdue")
    days_remaining: Optional[int] = Field(None, description="Days remaining until due date")
    
    class Config:
        from_attributes = True

    def can_be_modified_by(self, user_id: int) -> bool:
        """Check if a user can modify this task."""
        return (
            self.created_by == user_id or 
            self.assignee_id == user_id or
            self._user_has_admin_access(user_id)
        )
    
    def can_be_deleted_by(self, user_id: int) -> bool:
        """Check if a user can delete this task."""
        return (
            self.created_by == user_id or
            self._user_has_admin_access(user_id)
        )
    
    def _user_has_admin_access(self, user_id: int) -> bool:
        """Check if user has admin access (placeholder for demo)."""
        # In a real app, this would check user permissions
        return False

class UserBase(BaseModel):
    """Base user model."""
    email: str = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=50, description="User first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="User last name")
    role: UserRole = Field(default=UserRole.USER, description="User role in the system")

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=8, description="User password")

class User(UserBase):
    """Complete user model."""
    id: int = Field(..., description="Unique user identifier")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    # Computed properties
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def can_create_tasks(self) -> bool:
        """Check if user can create tasks."""
        return self.is_active and self.role in [UserRole.USER, UserRole.MANAGER, UserRole.ADMIN]
    
    @property
    def can_assign_tasks(self) -> bool:
        """Check if user can assign tasks to others."""
        return self.is_active and self.role in [UserRole.MANAGER, UserRole.ADMIN]
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == UserRole.ADMIN

class Project(BaseModel):
    """Project model."""
    id: int = Field(..., description="Unique project identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: Optional[str] = Field(None, max_length=500, description="Project description")
    owner_id: int = Field(..., description="User ID who owns the project")
    status: str = Field(default="active", description="Project status")
    created_at: datetime = Field(..., description="Project creation timestamp")
    updated_at: datetime = Field(..., description="Project last update timestamp")

class TaskStats(BaseModel):
    """Task statistics model."""
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    overdue_tasks: int = Field(..., description="Number of overdue tasks")
    completion_rate: float = Field(..., ge=0, le=100, description="Task completion rate percentage")
    average_completion_time: Optional[float] = Field(None, description="Average time to complete tasks in days")

class Notification(BaseModel):
    """Notification model."""
    id: int = Field(..., description="Unique notification identifier")
    user_id: int = Field(..., description="User ID to notify")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    type: str = Field(..., description="Notification type")
    is_read: bool = Field(default=False, description="Whether notification has been read")
    created_at: datetime = Field(..., description="Notification creation timestamp")
    read_at: Optional[datetime] = Field(None, description="When notification was read")

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    success: bool = Field(default=False, description="Operation was not successful")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
