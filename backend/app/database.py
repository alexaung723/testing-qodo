"""
Database module for the Qodo Demo API.
This file demonstrates database connectivity.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Trivial database for demo purposes
# This file shows database evolution
# Each function represents a small addition

class DatabaseManager:
    """Database manager for SQLite operations."""
    
    def __init__(self, db_path: str = "demo.db"):
        # Trivial initialization for demo
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        # Trivial table creation for demo
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    results_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    response_time REAL DEFAULT 0.0
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        # Trivial connection for demo
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def log_search(self, query: str, results_count: int):
        """Log search query."""
        # Trivial logging for demo
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO search_logs (query, results_count) VALUES (?, ?)",
                (query, results_count)
            )
            conn.commit()
    
    def log_api_usage(self, endpoint: str, method: str, response_time: float):
        """Log API usage statistics."""
        # Trivial logging for demo
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO api_usage (endpoint, method, response_time) VALUES (?, ?, ?)",
                (endpoint, method, response_time)
            )
            conn.commit()
    
    def get_search_stats(self) -> List[Dict[str, Any]]:
        """Get search statistics."""
        # Trivial stats for demo
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT query, COUNT(*) as count, AVG(results_count) as avg_results
                FROM search_logs
                GROUP BY query
                ORDER BY count DESC
                LIMIT 10
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_api_stats(self) -> List[Dict[str, Any]]:
        """Get API usage statistics."""
        # Trivial stats for demo
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT endpoint, method, COUNT(*) as count, AVG(response_time) as avg_time
                FROM api_usage
                GROUP BY endpoint, method
                ORDER BY count DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

# Global database instance
db_manager = DatabaseManager()

# Trivial helper function for demo
def get_db():
    """Get database manager instance."""
    return db_manager

# Trivial comment addition for demo
# This file shows database evolution
# Each function represents a small addition
