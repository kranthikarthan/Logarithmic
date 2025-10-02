"""
Redis Cache Manager for Assertly
Provides caching, session management, and real-time data storage
"""

import redis
import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import logging

class CacheManager:
    """Redis-based cache manager for Assertly"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()  # Test connection
            self.connected = True
            logging.info("Redis connection established successfully")
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self.connected
    
    def set_cache(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set cache value with expiration"""
        if not self.connected:
            return False
        
        try:
            # Serialize complex objects
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            self.redis_client.setex(key, expire_seconds, serialized_value)
            return True
        except Exception as e:
            logging.error(f"Failed to set cache for key {key}: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        if not self.connected:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logging.error(f"Failed to get cache for key {key}: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache value"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.delete(key)
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
        """Increment counter in Redis"""
        if not self.connected:
            return 0
        
        try:
            return self.redis_client.incrby(key, amount)
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
        
        # Store in list (keep last 100 activities)
        try:
            self.redis_client.lpush(activity_key, json.dumps(activity_data))
            self.redis_client.ltrim(activity_key, 0, 99)  # Keep last 100
            self.redis_client.expire(activity_key, 86400 * 7)  # 7 days
            return True
        except Exception as e:
            logging.error(f"Failed to set user activity: {e}")
            return False
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activities"""
        activity_key = f"user_activity:{user_id}"
        try:
            activities = self.redis_client.lrange(activity_key, 0, limit - 1)
            return [json.loads(activity) for activity in activities]
        except Exception as e:
            logging.error(f"Failed to get user activities: {e}")
            return []
    
    def set_api_rate_limit(self, api_key: str, limit: int = 100, window: int = 3600) -> bool:
        """Set API rate limit"""
        rate_limit_key = f"rate_limit:{api_key}"
        try:
            current_count = self.redis_client.incr(rate_limit_key)
            if current_count == 1:
                self.redis_client.expire(rate_limit_key, window)
            
            return current_count <= limit
        except Exception as e:
            logging.error(f"Failed to set rate limit: {e}")
            return True  # Allow if Redis fails
    
    def get_api_rate_limit(self, api_key: str) -> int:
        """Get current API rate limit count"""
        rate_limit_key = f"rate_limit:{api_key}"
        try:
            return int(self.redis_client.get(rate_limit_key) or 0)
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
        """Publish event to Redis pub/sub"""
        if not self.connected:
            return False
        
        try:
            message = {
                "event": event,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            self.redis_client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            logging.error(f"Failed to publish event: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.connected:
            return {"connected": False}
        
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            logging.error(f"Failed to get cache stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    def clear_all_cache(self) -> bool:
        """Clear all cache (use with caution)"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logging.error(f"Failed to clear cache: {e}")
            return False

# Global cache manager instance
cache_manager = CacheManager()