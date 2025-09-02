"""
User service for TaskFlow API - Handles user management and authentication.
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta
from app.models import User, UserCreate, UserRole

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user-related operations."""
    
    def __init__(self):
        """Initialize user service."""
        self._users = self._initialize_mock_users()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        logger.info(f"Fetching user {user_id}")
        return self._users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        logger.info(f"Fetching user by email: {email}")
        for user in self._users.values():
            if user.email == email:
                return user
        return None
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        logger.info(f"Creating user: {user_data.email}")
        
        # Check if user already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Generate user ID
        user_id = max(self._users.keys()) + 1 if self._users else 1
        
        # Create user object
        user = User(
            id=user_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            is_active=True,
            created_at=datetime.utcnow(),
            last_login=None
        )
        
        # Store user (in a real app, this would be in a database)
        self._users[user_id] = user
        
        logger.info(f"User {user_id} created successfully")
        return user
    
    async def update_user_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            logger.info(f"Updated last login for user {user_id}")
    
    async def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role."""
        logger.info(f"Fetching users with role: {role}")
        return [user for user in self._users.values() if user.role == role]
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            logger.info(f"User {user_id} deactivated")
            return True
        return False
    
    def _initialize_mock_users(self) -> dict:
        """Initialize mock users for demo purposes."""
        users = {}
        
        # Create some realistic users
        mock_users_data = [
            {
                "id": 1,
                "email": "admin@taskflow.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": UserRole.ADMIN,
                "created_at": datetime.utcnow() - timedelta(days=365)
            },
            {
                "id": 2,
                "email": "manager@taskflow.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "role": UserRole.MANAGER,
                "created_at": datetime.utcnow() - timedelta(days=180)
            },
            {
                "id": 3,
                "email": "developer@taskflow.com",
                "first_name": "Mike",
                "last_name": "Chen",
                "role": UserRole.USER,
                "created_at": datetime.utcnow() - timedelta(days=90)
            },
            {
                "id": 4,
                "email": "designer@taskflow.com",
                "first_name": "Emily",
                "last_name": "Davis",
                "role": UserRole.USER,
                "created_at": datetime.utcnow() - timedelta(days=60)
            }
        ]
        
        for user_data in mock_users_data:
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                is_active=True,
                created_at=user_data["created_at"],
                last_login=datetime.utcnow() - timedelta(days=1) if user_data["id"] > 1 else None
            )
            users[user_data["id"]] = user
        
        return users
