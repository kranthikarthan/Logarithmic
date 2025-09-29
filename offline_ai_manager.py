#!/usr/bin/env python3
"""
Offline AI Manager for Enterprise Environments
Provides offline AI capabilities using cached responses and local models
"""

import json
import os
import pickle
import hashlib
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OfflineResponse:
    """Offline AI response with metadata"""
    content: str
    model: str
    timestamp: datetime
    cache_key: str
    response_time: float
    tokens_used: Optional[int] = None
    confidence: float = 1.0

@dataclass
class OfflineModel:
    """Offline AI model configuration"""
    model_id: str
    name: str
    version: str
    model_path: str
    config: Dict[str, Any]
    loaded: bool = False
    last_used: Optional[datetime] = None

class OfflineAIManager:
    """Manages offline AI capabilities for enterprise environments"""
    
    def __init__(self, cache_dir: str = "offline_cache", models_dir: str = "offline_models"):
        self.cache_dir = cache_dir
        self.models_dir = models_dir
        self.cache_db_path = os.path.join(cache_dir, "offline_cache.db")
        self.models_db_path = os.path.join(models_dir, "offline_models.db")
        self.models = {}
        self.cache_lock = threading.Lock()
        
        # Create directories
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(models_dir, exist_ok=True)
        
        # Initialize databases
        self._init_cache_database()
        self._init_models_database()
        
        # Load available models
        self._load_available_models()
    
    def _init_cache_database(self):
        """Initialize cache database"""
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_responses (
                    cache_key TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    model TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    response_time REAL NOT NULL,
                    tokens_used INTEGER,
                    confidence REAL DEFAULT 1.0,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON offline_responses(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_model ON offline_responses(model)
            ''')
            
            conn.commit()
    
    def _init_models_database(self):
        """Initialize models database"""
        with sqlite3.connect(self.models_db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS offline_models (
                    model_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    config TEXT NOT NULL,
                    loaded BOOLEAN DEFAULT 0,
                    last_used TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def _load_available_models(self):
        """Load available offline models"""
        try:
            with sqlite3.connect(self.models_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM offline_models')
                rows = cursor.fetchall()
                
                for row in rows:
                    model = OfflineModel(
                        model_id=row[0],
                        name=row[1],
                        version=row[2],
                        model_path=row[3],
                        config=json.loads(row[4]),
                        loaded=bool(row[5]),
                        last_used=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                    self.models[model.model_id] = model
                    
        except Exception as e:
            logger.error(f"Failed to load available models: {e}")
    
    def register_model(self, model_id: str, name: str, version: str, 
                     model_path: str, config: Dict[str, Any]) -> bool:
        """Register a new offline model"""
        try:
            model = OfflineModel(
                model_id=model_id,
                name=name,
                version=version,
                model_path=model_path,
                config=config
            )
            
            with sqlite3.connect(self.models_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO offline_models 
                    (model_id, name, version, model_path, config, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    model_id, name, version, model_path, 
                    json.dumps(config), datetime.now().isoformat()
                ))
                conn.commit()
            
            self.models[model_id] = model
            logger.info(f"Registered offline model: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {e}")
            return False
    
    def load_model(self, model_id: str) -> bool:
        """Load an offline model into memory"""
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return False
        
        model = self.models[model_id]
        
        try:
            # Load model (implementation depends on model type)
            if model.model_path.endswith('.pkl'):
                # Load pickle model
                with open(model.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                model.loaded = True
                model.last_used = datetime.now()
                
            elif model.model_path.endswith('.json'):
                # Load JSON model configuration
                with open(model.model_path, 'r') as f:
                    model_data = json.load(f)
                model.loaded = True
                model.last_used = datetime.now()
                
            else:
                logger.error(f"Unsupported model format: {model.model_path}")
                return False
            
            # Update database
            with sqlite3.connect(self.models_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE offline_models 
                    SET loaded = 1, last_used = ? 
                    WHERE model_id = ?
                ''', (datetime.now().isoformat(), model_id))
                conn.commit()
            
            logger.info(f"Loaded offline model: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            return False
    
    def generate_offline_response(self, prompt: str, model_id: str = None) -> Optional[OfflineResponse]:
        """Generate response using offline AI"""
        # Check cache first
        cache_key = self._generate_cache_key(prompt, model_id)
        cached_response = self._get_cached_response(cache_key)
        
        if cached_response:
            logger.info("Using cached offline response")
            return cached_response
        
        # Use offline model
        if model_id and model_id in self.models:
            model = self.models[model_id]
            if not model.loaded:
                if not self.load_model(model_id):
                    return None
            
            # Generate response using offline model
            response = self._generate_with_offline_model(prompt, model)
            if response:
                # Cache the response
                self._cache_response(response)
                return response
        
        # Fallback to cached responses
        return self._get_similar_cached_response(prompt)
    
    def _generate_cache_key(self, prompt: str, model_id: str = None) -> str:
        """Generate cache key for prompt"""
        key_data = f"{prompt}:{model_id or 'default'}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[OfflineResponse]:
        """Get cached response by key"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT content, model, timestamp, response_time, tokens_used, confidence
                    FROM offline_responses 
                    WHERE cache_key = ?
                ''', (cache_key,))
                
                row = cursor.fetchone()
                if row:
                    # Update access count
                    cursor.execute('''
                        UPDATE offline_responses 
                        SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                        WHERE cache_key = ?
                    ''', (cache_key,))
                    conn.commit()
                    
                    return OfflineResponse(
                        content=row[0],
                        model=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        cache_key=cache_key,
                        response_time=row[3],
                        tokens_used=row[4],
                        confidence=row[5]
                    )
                    
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
        
        return None
    
    def _cache_response(self, response: OfflineResponse):
        """Cache an AI response"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO offline_responses 
                    (cache_key, content, model, timestamp, response_time, tokens_used, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    response.cache_key,
                    response.content,
                    response.model,
                    response.timestamp.isoformat(),
                    response.response_time,
                    response.tokens_used,
                    response.confidence
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
    
    def _generate_with_offline_model(self, prompt: str, model: OfflineModel) -> Optional[OfflineResponse]:
        """Generate response using offline model"""
        try:
            start_time = datetime.now()
            
            # Load model data
            if model.model_path.endswith('.pkl'):
                with open(model.model_path, 'rb') as f:
                    model_data = pickle.load(f)
            elif model.model_path.endswith('.json'):
                with open(model.model_path, 'r') as f:
                    model_data = json.load(f)
            else:
                return None
            
            # Generate response (simplified implementation)
            # In a real implementation, this would use the actual model
            response_content = self._simulate_model_response(prompt, model_data)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return OfflineResponse(
                content=response_content,
                model=model.model_id,
                timestamp=datetime.now(),
                cache_key=self._generate_cache_key(prompt, model.model_id),
                response_time=response_time,
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Failed to generate with offline model: {e}")
            return None
    
    def _simulate_model_response(self, prompt: str, model_data: Dict[str, Any]) -> str:
        """Simulate model response (placeholder implementation)"""
        # This is a simplified simulation
        # In a real implementation, this would use the actual AI model
        
        if "test case" in prompt.lower():
            return """
Test Case: User Login Validation
Description: Verify user can log in with valid credentials
Steps:
1. Navigate to login page
2. Enter valid username
3. Enter valid password
4. Click login button
Expected Result: User is logged in successfully
Priority: High
Tags: [authentication, login, validation]
"""
        elif "bdd" in prompt.lower() or "scenario" in prompt.lower():
            return """
Feature: User Login
  Scenario: Successful login with valid credentials
    Given the user is on the login page
    When the user enters valid credentials
    Then the user should be logged in successfully
    And the user should see the dashboard
"""
        else:
            return f"Offline AI response for: {prompt[:100]}..."
    
    def _get_similar_cached_response(self, prompt: str) -> Optional[OfflineResponse]:
        """Get similar cached response based on prompt similarity"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT content, model, timestamp, response_time, tokens_used, confidence, cache_key
                    FROM offline_responses 
                    WHERE content LIKE ? 
                    ORDER BY last_accessed DESC 
                    LIMIT 1
                ''', (f"%{prompt[:50]}%",))
                
                row = cursor.fetchone()
                if row:
                    return OfflineResponse(
                        content=row[0],
                        model=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        cache_key=row[6],
                        response_time=row[3],
                        tokens_used=row[4],
                        confidence=row[5] * 0.8  # Reduce confidence for similar responses
                    )
                    
        except Exception as e:
            logger.error(f"Failed to get similar cached response: {e}")
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                # Total responses
                cursor.execute('SELECT COUNT(*) FROM offline_responses')
                total_responses = cursor.fetchone()[0]
                
                # Cache hit rate
                cursor.execute('SELECT AVG(access_count) FROM offline_responses')
                avg_access = cursor.fetchone()[0] or 0
                
                # Model usage
                cursor.execute('''
                    SELECT model, COUNT(*) as count 
                    FROM offline_responses 
                    GROUP BY model 
                    ORDER BY count DESC
                ''')
                model_usage = dict(cursor.fetchall())
                
                # Recent activity
                cursor.execute('''
                    SELECT COUNT(*) FROM offline_responses 
                    WHERE timestamp > datetime('now', '-24 hours')
                ''')
                recent_activity = cursor.fetchone()[0]
                
                return {
                    'total_responses': total_responses,
                    'average_access_count': avg_access,
                    'model_usage': model_usage,
                    'recent_activity_24h': recent_activity,
                    'cache_size_mb': self._get_cache_size_mb()
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def _get_cache_size_mb(self) -> float:
        """Get cache database size in MB"""
        try:
            size_bytes = os.path.getsize(self.cache_db_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    def cleanup_old_cache(self, days: int = 30):
        """Clean up old cache entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM offline_responses 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old cache entries")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old cache: {e}")
            return 0
    
    def export_cache(self, output_file: str) -> bool:
        """Export cache to file"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM offline_responses')
                rows = cursor.fetchall()
                
                cache_data = {
                    'exported_at': datetime.now().isoformat(),
                    'total_entries': len(rows),
                    'responses': []
                }
                
                for row in rows:
                    cache_data['responses'].append({
                        'cache_key': row[0],
                        'content': row[1],
                        'model': row[2],
                        'timestamp': row[3],
                        'response_time': row[4],
                        'tokens_used': row[5],
                        'confidence': row[6],
                        'access_count': row[7],
                        'last_accessed': row[8]
                    })
                
                with open(output_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                
                logger.info(f"Exported cache to {output_file}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to export cache: {e}")
            return False
    
    def import_cache(self, input_file: str) -> bool:
        """Import cache from file"""
        try:
            with open(input_file, 'r') as f:
                cache_data = json.load(f)
            
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                for response in cache_data.get('responses', []):
                    cursor.execute('''
                        INSERT OR REPLACE INTO offline_responses 
                        (cache_key, content, model, timestamp, response_time, tokens_used, confidence, access_count, last_accessed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        response['cache_key'],
                        response['content'],
                        response['model'],
                        response['timestamp'],
                        response['response_time'],
                        response['tokens_used'],
                        response['confidence'],
                        response['access_count'],
                        response['last_accessed']
                    ))
                
                conn.commit()
                
                logger.info(f"Imported {len(cache_data.get('responses', []))} cache entries")
                return True
                
        except Exception as e:
            logger.error(f"Failed to import cache: {e}")
            return False