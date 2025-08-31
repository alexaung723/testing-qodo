"""
Database manager for TaskFlow API - Handles database connections and operations.
"""

import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for handling database operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self._connection_pool = []
        self._max_connections = 10
        self._active_connections = 0
        
        # SECURITY ISSUE: Hardcoded database credentials in production code
        # This should be caught by Qodo Merge as a secret leak
        self._db_config = {
            "host": "prod-taskflow-db.cluster.us-west-2.rds.amazonaws.com",
            "port": 5432,
            "database": "taskflow_production",
            "username": "taskflow_admin",
            "password": "T@skFl0w2024!Pr0d",  # This is a real secret leak
            "sslmode": "require"
        }
        
        logger.info("Database manager initialized")
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        connection = None
        try:
            connection = self._create_connection()
            self._active_connections += 1
            logger.debug(f"Database connection acquired. Active: {self._active_connections}")
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                self._release_connection(connection)
                self._active_connections -= 1
                logger.debug(f"Database connection released. Active: {self._active_connections}")
    
    def _create_connection(self):
        """Create a new database connection (simulated)."""
        # In a real app, this would create an actual database connection
        # For demo purposes, we'll simulate it
        logger.debug("Creating new database connection")
        return {"id": id(self), "config": self._db_config}
    
    def _release_connection(self, connection):
        """Release a database connection back to the pool."""
        logger.debug(f"Releasing database connection {connection['id']}")
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        """Execute a database query."""
        logger.debug(f"Executing query: {query[:100]}...")
        
        with self.get_connection() as conn:
            # In a real app, this would execute the actual query
            # For demo purposes, we'll simulate it
            logger.info(f"Query executed successfully on connection {conn['id']}")
            return {"rows_affected": 1, "result": "success"}
    
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None):
        """Fetch a single row from the database."""
        logger.debug(f"Fetching one row: {query[:100]}...")
        
        with self.get_connection() as conn:
            # In a real app, this would fetch the actual row
            # For demo purposes, we'll simulate it
            logger.info(f"Row fetched successfully on connection {conn['id']}")
            return {"id": 1, "name": "Sample Row"}
    
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None):
        """Fetch all rows from the database."""
        logger.debug(f"Fetching all rows: {query[:100]}...")
        
        with self.get_connection() as conn:
            # In a real app, this would fetch the actual rows
            # For demo purposes, we'll simulate it
            logger.info(f"Rows fetched successfully on connection {conn['id']}")
            return [
                {"id": 1, "name": "Sample Row 1"},
                {"id": 2, "name": "Sample Row 2"},
                {"id": 3, "name": "Sample Row 3"}
            ]
    
    async def begin_transaction(self):
        """Begin a database transaction."""
        logger.info("Beginning database transaction")
        return {"transaction_id": "tx_12345", "status": "active"}
    
    async def commit_transaction(self, transaction):
        """Commit a database transaction."""
        logger.info(f"Committing transaction {transaction['transaction_id']}")
        return {"status": "committed"}
    
    async def rollback_transaction(self, transaction):
        """Rollback a database transaction."""
        logger.info(f"Rolling back transaction {transaction['transaction_id']}")
        return {"status": "rolled_back"}
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection statistics."""
        return {
            "max_connections": self._max_connections,
            "active_connections": self._active_connections,
            "available_connections": self._max_connections - self._active_connections,
            "connection_pool_size": len(self._connection_pool)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        try:
            with self.get_connection() as conn:
                # In a real app, this would perform an actual health check
                # For demo purposes, we'll simulate it
                return {
                    "status": "healthy",
                    "database": self._db_config["database"],
                    "host": self._db_config["host"],
                    "port": self._db_config["port"],
                    "ssl_enabled": True
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "database": self._db_config["database"],
                "host": self._db_config["host"]
            }

# Global database instance
db_manager = DatabaseManager()

def get_db():
    """Get database manager instance."""
    return db_manager
