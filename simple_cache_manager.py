"""
Simple Cache Manager for Assertly (Fallback)
Provides basic caching functionality without external dependencies
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import logging

class SimpleCacheManager:
    """Simple in-memory cache manager (fallback when Redis is not available)"""
    
    def __init__(self):
        """Initialize simple cache"""
        self.cache = {}
        self.connected = True
        logging.info("Simple cache manager initialized (Redis not available)")
    
    def is_connected(self) -> bool:
        """Check if cache is connected"""
        return self.connected
    
    def set_cache(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set cache value with expiration"""
        try:
            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + expire_seconds
            }
            return True
        except Exception as e:
            logging.error(f"Failed to set cache for key {key}: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            if key not in self.cache:
                return None
            
            cache_item = self.cache[key]
            if time.time() > cache_item['expires_at']:
                del self.cache[key]
                return None
            
            return cache_item['value']
        except Exception as e:
            logging.error(f"Failed to get cache for key {key}: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache value"""
        try:
            if key in self.cache:
                del self.cache[key]
            return True
        except Exception as e:
            logging.error(f"Failed to delete cache for key {key}: {e}")
            return False
    
    def get_or_set(self, key: str, func, expire_seconds: int = 3600) -> Any:
        """Get from cache or set using function"""
        cached_value = self.get_cache(key)
        if cached_value is not None:
            return cached_value
        
        # Execute function and cache result
        try:
            result = func()
            self.set_cache(key, result, expire_seconds)
            return result
        except Exception as e:
            logging.error(f"Failed to execute function for key {key}: {e}")
            return None
    
    def increment_counter(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache"""
        try:
            current = int(self.get_cache(key) or 0)
            new_value = current + amount
            self.set_cache(key, new_value, 3600)
            return new_value
        except Exception as e:
            logging.error(f"Failed to increment counter for key {key}: {e}")
            return 0
    
    def set_session(self, session_id: str, data: Dict[str, Any], expire_seconds: int = 86400) -> bool:
        """Set session data"""
        session_key = f"session:{session_id}"
        return self.set_cache(session_key, data, expire_seconds)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session_key = f"session:{session_id}"
        return self.get_cache(session_key)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        session_key = f"session:{session_id}"
        return self.delete_cache(session_key)
    
    def set_user_activity(self, user_id: str, activity: str) -> bool:
        """Track user activity"""
        activity_key = f"user_activity:{user_id}"
        activity_data = {
            "activity": activity,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        # Get existing activities
        activities = self.get_cache(activity_key) or []
        activities.append(activity_data)
        
        # Keep only last 100 activities
        activities = activities[-100:]
        
        return self.set_cache(activity_key, activities, 86400 * 7)  # 7 days
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activities"""
        activity_key = f"user_activity:{user_id}"
        activities = self.get_cache(activity_key) or []
        return activities[-limit:]
    
    def set_api_rate_limit(self, api_key: str, limit: int = 100, window: int = 3600) -> bool:
        """Set API rate limit"""
        rate_limit_key = f"rate_limit:{api_key}"
        try:
            current_count = int(self.get_cache(rate_limit_key) or 0)
            new_count = current_count + 1
            
            if current_count == 0:
                # First request in window
                self.set_cache(rate_limit_key, new_count, window)
            else:
                self.set_cache(rate_limit_key, new_count, window)
            
            return new_count <= limit
        except Exception as e:
            logging.error(f"Failed to set rate limit: {e}")
            return True  # Allow if cache fails
    
    def get_api_rate_limit(self, api_key: str) -> int:
        """Get current API rate limit count"""
        rate_limit_key = f"rate_limit:{api_key}"
        try:
            return int(self.get_cache(rate_limit_key) or 0)
        except Exception as e:
            logging.error(f"Failed to get rate limit: {e}")
            return 0
    
    def set_real_time_data(self, channel: str, data: Dict[str, Any]) -> bool:
        """Set real-time data for WebSocket"""
        real_time_key = f"realtime:{channel}"
        return self.set_cache(real_time_key, data, 300)  # 5 minutes
    
    def get_real_time_data(self, channel: str) -> Optional[Dict[str, Any]]:
        """Get real-time data for WebSocket"""
        real_time_key = f"realtime:{channel}"
        return self.get_cache(real_time_key)
    
    def publish_event(self, channel: str, event: str, data: Dict[str, Any]) -> bool:
        """Publish event (simplified - no pub/sub)"""
        try:
            message = {
                "event": event,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            # Store in cache for retrieval
            self.set_cache(f"event:{channel}:{int(time.time())}", message, 300)
            return True
        except Exception as e:
            logging.error(f"Failed to publish event: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            # Clean expired entries
            current_time = time.time()
            expired_keys = [
                key for key, item in self.cache.items()
                if current_time > item['expires_at']
            ]
            for key in expired_keys:
                del self.cache[key]
            
            return {
                "connected": True,
                "cache_type": "simple_memory",
                "total_keys": len(self.cache),
                "memory_usage": f"{len(str(self.cache))} characters",
                "hit_rate": 0.0,  # Not tracked in simple version
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to get cache stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def clear_all_cache(self) -> bool:
        """Clear all cache"""
        try:
            self.cache.clear()
            return True
        except Exception as e:
            logging.error(f"Failed to clear cache: {e}")
            return False

# Global cache manager instance
cache_manager = SimpleCacheManager()