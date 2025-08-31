"""
Enterprise Governance API - Database Management
Comprehensive database management with connection pooling, migrations, and monitoring.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Union, AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import json
from decimal import Decimal

# Database drivers
try:
    import asyncpg
    import aiomysql
    import motor.motor_asyncio
    import aioredis
    from elasticsearch import AsyncElasticsearch
    POSTGRESQL_AVAILABLE = True
    MYSQL_AVAILABLE = True
    MONGODB_AVAILABLE = True
    REDIS_AVAILABLE = True
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    MYSQL_AVAILABLE = False
    MONGODB_AVAILABLE = False
    REDIS_AVAILABLE = False
    ELASTICSEARCH_AVAILABLE = False

from app.core.config import get_settings, DatabaseType
from app.core.exceptions import DatabaseConnectionError, DatabaseQueryError, DatabaseMigrationError

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection wrapper with connection pooling and monitoring."""
    
    def __init__(self, connection_type: DatabaseType, connection_string: str):
        self.connection_type = connection_type
        self.connection_string = connection_string
        self.pool = None
        self.connection = None
        self.is_connected = False
        self.last_health_check = None
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "total_queries": 0,
            "slow_queries": 0,
            "failed_queries": 0
        }
    
    async def connect(self) -> None:
        """Establish database connection."""
        try:
            if self.connection_type == DatabaseType.POSTGRESQL:
                if not POSTGRESQL_AVAILABLE:
                    raise DatabaseConnectionError("PostgreSQL driver not available")
                
                self.pool = await asyncpg.create_pool(
                    self.connection_string,
                    min_size=5,
                    max_size=20,
                    command_timeout=60,
                    statement_cache_size=0
                )
                self.is_connected = True
                logger.info("PostgreSQL connection pool established")
                
            elif self.connection_type == DatabaseType.MYSQL:
                if not MYSQL_AVAILABLE:
                    raise DatabaseConnectionError("MySQL driver not available")
                
                self.pool = await aiomysql.create_pool(
                    host=self.connection_string.split('@')[1].split(':')[0],
                    port=int(self.connection_string.split(':')[2].split('/')[0]),
                    user=self.connection_string.split('://')[1].split(':')[0],
                    password=self.connection_string.split(':')[1].split('@')[0],
                    db=self.connection_string.split('/')[-1],
                    minsize=5,
                    maxsize=20,
                    autocommit=True
                )
                self.is_connected = True
                logger.info("MySQL connection pool established")
                
            elif self.connection_type == DatabaseType.MONGODB:
                if not MONGODB_AVAILABLE:
                    raise DatabaseConnectionError("MongoDB driver not available")
                
                self.connection = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)
                self.is_connected = True
                logger.info("MongoDB connection established")
                
            elif self.connection_type == DatabaseType.REDIS:
                if not REDIS_AVAILABLE:
                    raise DatabaseConnectionError("Redis driver not available")
                
                self.connection = await aioredis.from_url(self.connection_string)
                self.is_connected = True
                logger.info("Redis connection established")
                
            elif self.connection_type == DatabaseType.ELASTICSEARCH:
                if not ELASTICSEARCH_AVAILABLE:
                    raise DatabaseConnectionError("Elasticsearch driver not available")
                
                self.connection = AsyncElasticsearch([self.connection_string])
                self.is_connected = True
                logger.info("Elasticsearch connection established")
            
            self.last_health_check = datetime.utcnow()
            self.connection_stats["total_connections"] += 1
            
        except Exception as e:
            self.connection_stats["failed_connections"] += 1
            logger.error(f"Failed to establish {self.connection_type.value} connection: {e}")
            raise DatabaseConnectionError(f"Connection failed: {str(e)}")
    
    async def disconnect(self) -> None:
        """Close database connection."""
        try:
            if self.pool:
                await self.pool.close()
            elif self.connection:
                await self.connection.close()
            
            self.is_connected = False
            logger.info(f"{self.connection_type.value} connection closed")
            
        except Exception as e:
            logger.error(f"Error closing {self.connection_type.value} connection: {e}")
    
    async def health_check(self) -> bool:
        """Perform database health check."""
        try:
            if not self.is_connected:
                return False
            
            if self.connection_type == DatabaseType.POSTGRESQL:
                async with self.pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                    
            elif self.connection_type == DatabaseType.MYSQL:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute("SELECT 1")
                        
            elif self.connection_type == DatabaseType.MONGODB:
                await self.connection.admin.command('ping')
                
            elif self.connection_type == DatabaseType.REDIS:
                await self.connection.ping()
                
            elif self.connection_type == DatabaseType.ELASTICSEARCH:
                await self.connection.ping()
            
            self.last_health_check = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for {self.connection_type.value}: {e}")
            return False
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a database query."""
        start_time = datetime.utcnow()
        
        try:
            if self.connection_type == DatabaseType.POSTGRESQL:
                async with self.pool.acquire() as conn:
                    result = await conn.execute(query, *(params or {}).values())
                    
            elif self.connection_type == DatabaseType.MYSQL:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(query, params or {})
                        result = await cur.fetchall()
                        
            elif self.connection_type == DatabaseType.MONGODB:
                # MongoDB queries would be handled differently
                result = None
                
            elif self.connection_type == DatabaseType.REDIS:
                result = await self.connection.execute_command(query, *(params or {}).values())
                
            elif self.connection_type == DatabaseType.ELASTICSEARCH:
                result = await self.connection.search(index="*", body=params or {})
            
            # Update statistics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.connection_stats["total_queries"] += 1
            
            if execution_time > 1.0:  # Consider queries >1 second as slow
                self.connection_stats["slow_queries"] += 1
                logger.warning(f"Slow query detected: {execution_time:.2f}s - {query[:100]}...")
            
            return result
            
        except Exception as e:
            self.connection_stats["failed_queries"] += 1
            logger.error(f"Query execution failed: {e}")
            raise DatabaseQueryError(f"Query failed: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            **self.connection_stats,
            "connection_type": self.connection_type.value,
            "is_connected": self.is_connected,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }

class DatabaseManager:
    """Main database manager for the application."""
    
    def __init__(self):
        self.settings = get_settings()
        self.connections: Dict[str, DatabaseConnection] = {}
        self.migration_manager = DatabaseMigrationManager(self)
        self.query_monitor = QueryMonitor()
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """Initialize database connections and run migrations."""
        try:
            # Initialize primary database
            primary_db = DatabaseConnection(
                self.settings.database_type,
                self.settings.database_url
            )
            await primary_db.connect()
            self.connections["primary"] = primary_db
            
            # Initialize cache database if different from primary
            if self.settings.cache_type.value != self.settings.database_type.value:
                cache_db = DatabaseConnection(
                    self.settings.cache_type,
                    self.settings.cache_url or self.settings.database_url
                )
                await cache_db.connect()
                self.connections["cache"] = cache_db
            
            # Run migrations
            await self.migration_manager.run_migrations()
            
            # Initialize query monitor
            await self.query_monitor.initialize()
            
            self.is_initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise DatabaseConnectionError(f"Initialization failed: {str(e)}")
    
    async def close(self) -> None:
        """Close all database connections."""
        try:
            for name, connection in self.connections.items():
                await connection.disconnect()
                logger.info(f"Closed {name} database connection")
            
            await self.query_monitor.close()
            self.is_initialized = False
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    async def get_connection(self, name: str = "primary") -> DatabaseConnection:
        """Get a database connection by name."""
        if not self.is_initialized:
            raise DatabaseConnectionError("Database manager not initialized")
        
        if name not in self.connections:
            raise DatabaseConnectionError(f"Database connection '{name}' not found")
        
        return self.connections[name]
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, 
                          connection_name: str = "primary") -> Any:
        """Execute a query on the specified database connection."""
        connection = await self.get_connection(connection_name)
        return await connection.execute_query(query, params)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all database connections."""
        health_status = {
            "overall_status": "healthy",
            "connections": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        all_healthy = True
        
        for name, connection in self.connections.items():
            is_healthy = await connection.health_check()
            health_status["connections"][name] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "type": connection.connection_type.value,
                "stats": connection.get_stats()
            }
            
            if not is_healthy:
                all_healthy = False
        
        health_status["overall_status"] = "healthy" if all_healthy else "degraded"
        return health_status
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics for all database connections."""
        stats = {}
        for name, connection in self.connections.items():
            stats[name] = connection.get_stats()
        return stats

class DatabaseMigrationManager:
    """Manages database schema migrations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.migrations_table = "schema_migrations"
        self.migrations_path = "migrations"
    
    async def run_migrations(self) -> None:
        """Run pending database migrations."""
        try:
            # Create migrations table if it doesn't exist
            await self._create_migrations_table()
            
            # Get applied migrations
            applied_migrations = await self._get_applied_migrations()
            
            # Get available migrations
            available_migrations = self._get_available_migrations()
            
            # Run pending migrations
            pending_migrations = [m for m in available_migrations if m not in applied_migrations]
            
            for migration in sorted(pending_migrations):
                await self._run_migration(migration)
                logger.info(f"Applied migration: {migration}")
            
            logger.info(f"Database migrations completed. Applied: {len(pending_migrations)}")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise DatabaseMigrationError(f"Migration failed: {str(e)}")
    
    async def _create_migrations_table(self) -> None:
        """Create the migrations tracking table."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            version VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64),
            execution_time_ms INTEGER
        );
        """
        
        try:
            await self.db_manager.execute_query(create_table_sql)
        except Exception as e:
            logger.warning(f"Could not create migrations table: {e}")
    
    async def _get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations."""
        try:
            query = "SELECT version FROM schema_migrations ORDER BY applied_at"
            result = await self.db_manager.execute_query(query)
            
            if isinstance(result, list):
                return [row[0] for row in result]
            else:
                return []
                
        except Exception as e:
            logger.warning(f"Could not get applied migrations: {e}")
            return []
    
    def _get_available_migrations(self) -> List[str]:
        """Get list of available migration files."""
        # This would scan the migrations directory
        # For demo purposes, return empty list
        return []
    
    async def _run_migration(self, migration: str) -> None:
        """Run a specific migration."""
        start_time = datetime.utcnow()
        
        try:
            # Read and execute migration file
            # This is a simplified implementation
            migration_sql = f"-- Migration: {migration}\n-- Placeholder for actual migration"
            
            await self.db_manager.execute_query(migration_sql)
            
            # Record migration
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            record_sql = """
            INSERT INTO schema_migrations (version, name, execution_time_ms)
            VALUES ($1, $2, $3)
            """
            
            await self.db_manager.execute_query(record_sql, {
                "version": migration,
                "name": migration,
                "execution_time_ms": execution_time
            })
            
        except Exception as e:
            logger.error(f"Migration {migration} failed: {e}")
            raise DatabaseMigrationError(f"Migration {migration} failed: {str(e)}")

class QueryMonitor:
    """Monitors database query performance and provides insights."""
    
    def __init__(self):
        self.settings = get_settings()
        self.query_logs: List[Dict[str, Any]] = []
        self.performance_metrics = {
            "total_queries": 0,
            "slow_queries": 0,
            "failed_queries": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
        self.is_monitoring = False
    
    async def initialize(self) -> None:
        """Initialize the query monitor."""
        self.is_monitoring = True
        logger.info("Query monitor initialized")
    
    async def close(self) -> None:
        """Close the query monitor."""
        self.is_monitoring = False
        logger.info("Query monitor closed")
    
    async def log_query(self, query: str, params: Optional[Dict[str, Any]], 
                       execution_time: float, success: bool, error: Optional[str] = None) -> None:
        """Log a database query for monitoring."""
        if not self.is_monitoring:
            return
        
        query_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query[:200] + "..." if len(query) > 200 else query,
            "params": str(params)[:100] + "..." if params and len(str(params)) > 100 else params,
            "execution_time": execution_time,
            "success": success,
            "error": error,
            "query_hash": hash(query)
        }
        
        self.query_logs.append(query_log)
        
        # Update performance metrics
        self.performance_metrics["total_queries"] += 1
        self.performance_metrics["total_response_time"] += execution_time
        
        if execution_time > 1.0:  # Slow query threshold
            self.performance_metrics["slow_queries"] += 1
        
        if not success:
            self.performance_metrics["failed_queries"] += 1
        
        # Calculate average response time
        self.performance_metrics["average_response_time"] = (
            self.performance_metrics["total_response_time"] / 
            self.performance_metrics["total_queries"]
        )
        
        # Keep only last 1000 queries in memory
        if len(self.query_logs) > 1000:
            self.query_logs = self.query_logs[-1000:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.performance_metrics,
            "slow_query_percentage": (
                (self.performance_metrics["slow_queries"] / 
                 max(self.performance_metrics["total_queries"], 1)) * 100
            ),
            "failure_rate": (
                (self.performance_metrics["failed_queries"] / 
                 max(self.performance_metrics["total_queries"], 1)) * 100
            )
        }
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest queries."""
        return sorted(
            self.query_logs,
            key=lambda x: x["execution_time"],
            reverse=True
        )[:limit]
    
    def get_failed_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent failed queries."""
        failed_queries = [q for q in self.query_logs if not q["success"]]
        return sorted(
            failed_queries,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

async def init_db() -> None:
    """Initialize the database manager."""
    global _db_manager
    _db_manager = DatabaseManager()
    await _db_manager.initialize()

async def close_db() -> None:
    """Close the database manager."""
    global _db_manager
    if _db_manager:
        await _db_manager.close()
        _db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get the database manager instance."""
    if not _db_manager:
        raise DatabaseConnectionError("Database manager not initialized")
    return _db_manager

@asynccontextmanager
async def get_db_connection(connection_name: str = "primary") -> AsyncGenerator[DatabaseConnection, None]:
    """Get a database connection context manager."""
    db_manager = get_db_manager()
    connection = await db_manager.get_connection(connection_name)
    try:
        yield connection
    finally:
        # Connection is managed by the pool, no need to close
        pass
