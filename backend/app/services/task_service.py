"""
Task service for TaskFlow API - Handles business logic for task operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models import Task, TaskCreate, TaskUpdate, TaskStats, TaskStatus, TaskPriority
from app.database import DatabaseManager

logger = logging.getLogger(__name__)

class TaskService:
    """Service class for task-related operations."""
    
    def __init__(self):
        """Initialize task service."""
        self.db = DatabaseManager()
    
    async def create_task(self, task_data: TaskCreate, created_by: int) -> Task:
        """Create a new task."""
        logger.info(f"Creating task '{task_data.title}' for user {created_by}")
        
        # Business logic validation
        if task_data.due_date and task_data.due_date < datetime.utcnow():
            raise ValueError("Due date cannot be in the past")
        
        if task_data.estimated_hours and task_data.estimated_hours > 168:  # 1 week
            raise ValueError("Estimated hours cannot exceed 168 (1 week)")
        
        # Create task object
        task = Task(
            id=self._generate_task_id(),
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            due_date=task_data.due_date,
            estimated_hours=task_data.estimated_hours,
            tags=task_data.tags,
            status=TaskStatus.TODO,
            created_by=created_by,
            assignee_id=task_data.assignee_id,
            project_id=task_data.project_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_overdue=False,
            days_remaining=self._calculate_days_remaining(task_data.due_date)
        )
        
        # Save to database (simulated)
        await self._save_task(task)
        
        logger.info(f"Task {task.id} created successfully")
        return task
    
    async def get_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Task]:
        """Get tasks with optional filtering."""
        logger.info(f"Fetching tasks for user {user_id} with filters: status={status}, priority={priority}")
        
        # In a real app, this would query the database
        # For demo purposes, we'll return mock data
        mock_tasks = self._generate_mock_tasks(user_id, limit)
        
        # Apply filters
        if status:
            mock_tasks = [t for t in mock_tasks if t.status.value == status]
        
        if priority:
            mock_tasks = [t for t in mock_tasks if t.priority.value == priority]
        
        # Apply pagination
        return mock_tasks[skip:skip + limit]
    
    async def get_task(self, task_id: int, user_id: int) -> Optional[Task]:
        """Get a specific task by ID."""
        logger.info(f"Fetching task {task_id} for user {user_id}")
        
        # In a real app, this would query the database
        # For demo purposes, we'll return a mock task
        mock_task = self._generate_mock_task(task_id, user_id)
        
        if not mock_task:
            return None
        
        # Check if user has access to this task
        if not mock_task.can_be_modified_by(user_id):
            logger.warning(f"User {user_id} attempted to access task {task_id} without permission")
            return None
        
        return mock_task
    
    async def update_task(self, task_id: int, task_update: TaskUpdate, user_id: int) -> Task:
        """Update an existing task."""
        logger.info(f"Updating task {task_id} by user {user_id}")
        
        # Get existing task
        existing_task = await self.get_task(task_id, user_id)
        if not existing_task:
            raise ValueError("Task not found or access denied")
        
        # Apply updates
        if task_update.title is not None:
            existing_task.title = task_update.title
        
        if task_update.description is not None:
            existing_task.description = task_update.description
        
        if task_update.status is not None:
            existing_task.status = task_update.status
            
            # Update completion timestamp if status is completed
            if task_update.status == TaskStatus.COMPLETED:
                existing_task.completed_at = datetime.utcnow()
        
        if task_update.priority is not None:
            existing_task.priority = task_update.priority
        
        if task_update.due_date is not None:
            existing_task.due_date = task_update.due_date
            existing_task.days_remaining = self._calculate_days_remaining(task_update.due_date)
        
        if task_update.estimated_hours is not None:
            existing_task.estimated_hours = task_update.estimated_hours
        
        if task_update.tags is not None:
            existing_task.tags = task_update.tags
        
        if task_update.assignee_id is not None:
            existing_task.assignee_id = task_update.assignee_id
        
        if task_update.project_id is not None:
            existing_task.project_id = task_update.project_id
        
        # Update timestamp
        existing_task.updated_at = datetime.utcnow()
        
        # Recalculate overdue status
        existing_task.is_overdue = self._is_task_overdue(existing_task)
        
        # Save to database (simulated)
        await self._save_task(existing_task)
        
        logger.info(f"Task {task_id} updated successfully")
        return existing_task
    
    async def delete_task(self, task_id: int, user_id: int) -> None:
        """Delete a task."""
        logger.info(f"Deleting task {task_id} by user {user_id}")
        
        # Get existing task
        existing_task = await self.get_task(task_id, user_id)
        if not existing_task:
            raise ValueError("Task not found or access denied")
        
        # Check if task can be deleted
        if not existing_task.can_be_deleted_by(user_id):
            raise ValueError("User does not have permission to delete this task")
        
        # In a real app, this would delete from database
        # For demo purposes, we'll just log the action
        logger.info(f"Task {task_id} deleted successfully")
    
    async def assign_task(self, task_id: int, assignee_id: int, assigned_by: int) -> Task:
        """Assign a task to another user."""
        logger.info(f"Assigning task {task_id} to user {assignee_id} by user {assigned_by}")
        
        # Get existing task
        existing_task = await self.get_task(task_id, assigned_by)
        if not existing_task:
            raise ValueError("Task not found or access denied")
        
        # Update assignee
        existing_task.assignee_id = assignee_id
        existing_task.updated_at = datetime.utcnow()
        
        # Save to database (simulated)
        await self._save_task(existing_task)
        
        logger.info(f"Task {task_id} assigned to user {assignee_id} successfully")
        return existing_task
    
    async def get_user_stats(self, user_id: int) -> TaskStats:
        """Get task statistics for a user."""
        logger.info(f"Fetching task statistics for user {user_id}")
        
        # In a real app, this would query the database
        # For demo purposes, we'll return mock statistics
        mock_stats = TaskStats(
            total_tasks=25,
            completed_tasks=18,
            overdue_tasks=2,
            completion_rate=72.0,
            average_completion_time=3.5
        )
        
        return mock_stats
    
    def _generate_task_id(self) -> int:
        """Generate a unique task ID (simulated)."""
        import random
        return random.randint(1000, 9999)
    
    def _calculate_days_remaining(self, due_date: Optional[datetime]) -> Optional[int]:
        """Calculate days remaining until due date."""
        if not due_date:
            return None
        
        delta = due_date - datetime.utcnow()
        return max(0, delta.days)
    
    def _is_task_overdue(self, task: Task) -> bool:
        """Check if a task is overdue."""
        if not task.due_date or task.status == TaskStatus.COMPLETED:
            return False
        
        return datetime.utcnow() > task.due_date
    
    async def _save_task(self, task: Task) -> None:
        """Save task to database (simulated)."""
        # In a real app, this would save to the database
        logger.debug(f"Saving task {task.id} to database")
    
    def _generate_mock_tasks(self, user_id: int, count: int) -> List[Task]:
        """Generate mock tasks for demo purposes."""
        tasks = []
        for i in range(count):
            task = self._generate_mock_task(i + 1, user_id)
            if task:
                tasks.append(task)
        return tasks
    
    def _generate_mock_task(self, task_id: int, user_id: int) -> Optional[Task]:
        """Generate a single mock task for demo purposes."""
        import random
        
        priorities = list(TaskPriority)
        statuses = list(TaskStatus)
        
        # Create a realistic task
        due_date = datetime.utcnow() + timedelta(days=random.randint(1, 30))
        
        task = Task(
            id=task_id,
            title=f"Sample Task {task_id}",
            description=f"This is a sample task description for task {task_id}",
            priority=random.choice(priorities),
            due_date=due_date,
            estimated_hours=random.uniform(1, 8),
            tags=["sample", "demo", f"tag-{task_id}"],
            status=random.choice(statuses),
            created_by=user_id,
            assignee_id=user_id if random.choice([True, False]) else None,
            project_id=random.randint(1, 5) if random.choice([True, False]) else None,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)),
            completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 3)) if random.choice([True, False]) else None,
            is_overdue=False,
            days_remaining=self._calculate_days_remaining(due_date)
        )
        
        # Update overdue status
        task.is_overdue = self._is_task_overdue(task)
        
        return task
