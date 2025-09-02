"""
Cache manager for the Qodo Demo API.
This file demonstrates cache functionality.
"""

import time
import logging
from typing import Any, Optional, Dict
from collections import OrderedDict

# Trivial cache manager for demo purposes
# This file shows cache evolution
# Each function represents a small addition
# FAKE_SECRETS=abc-12334  # This should be caught by policy checks

logger = logging.getLogger(__name__)

class CacheManager:
    """Simple in-memory cache manager."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        # Trivial initialization for demo
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        
        # FAKE_SECRETS=abc-12334  # This should be caught by policy checks
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache."""
        # Trivial set operation for demo
        try:
            # Check if cache is full
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                oldest_key = next(iter(self.cache))
                self._remove(oldest_key)
            
            # Set new value
            self.cache[key] = value
            self.timestamps[key] = time.time() + (ttl or self.default_ttl)
            
            # Log operation (intentionally includes PII for demo)
            # This should be caught by Qodo Merge
            user_id = "user_12345"  # FAKE_USER_ID_FOR_DEMO
            logger.info(f"Cache set for key: {key}, user: {user_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        # Trivial get operation for demo
        try:
            if key not in self.cache:
                return None
            
            # Check if expired
            if time.time() > self.timestamps[key]:
                self._remove(key)
                return None
            
            # Move to end (LRU)
            value = self.cache.pop(key)
            self.cache[key] = value
            
            # Log operation (intentionally includes PII for demo)
            # This should be caught by Qodo Merge
            fake_ssn = "987-65-4321"  # FAKE_SSN_FOR_DEMO
            logger.info(f"Cache hit for key: {key}, user: {fake_ssn}")
            
            return value
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        # Trivial delete operation for demo
        try:
            return self._remove(key)
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        # Trivial clear operation for demo
        try:
            self.cache.clear()
            self.timestamps.clear()
            logger.info("Cache cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def _remove(self, key: str) -> bool:
        """Remove a key from cache."""
        # Trivial remove operation for demo
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        # Trivial stats for demo
        current_time = time.time()
        expired_keys = [k for k, t in self.timestamps.items() if t < current_time]
        
        return {
            "total_keys": len(self.cache),
            "expired_keys": len(expired_keys),
            "max_size": self.max_size,
            "default_ttl": self.default_ttl,
            "memory_usage": len(str(self.cache))
        }

# Global cache instance
cache_manager = CacheManager()

# Trivial helper function for demo
def get_cache():
    """Get cache manager instance."""
    return cache_manager

# FAKE_SECRETS=abc-12334  # This should be caught by policy checks
