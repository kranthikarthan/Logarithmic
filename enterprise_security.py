#!/usr/bin/env python3
"""
Enterprise Security Module
Provides security features for enterprise environments including audit logging,
data encryption, access control, and compliance features
"""

import os
import json
import hashlib
import hmac
import base64
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import sqlite3
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AccessLevel(Enum):
    """Access level enumeration"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    AUDIT = "audit"

@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    timestamp: datetime
    user: str
    action: str
    resource: str
    level: SecurityLevel
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    success: bool
    risk_score: float = 0.0

@dataclass
class AccessControl:
    """Access control rule"""
    rule_id: str
    user: str
    resource: str
    access_level: AccessLevel
    conditions: Dict[str, Any]
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class EnterpriseSecurity:
    """Enterprise security manager"""
    
    def __init__(self, config_dir: str = "security_config"):
        self.config_dir = config_dir
        self.security_db_path = os.path.join(config_dir, "security.db")
        self.audit_db_path = os.path.join(config_dir, "audit.db")
        self.encryption_key = None
        self.security_lock = threading.Lock()
        
        # Create directories
        os.makedirs(config_dir, exist_ok=True)
        
        # Initialize databases
        self._init_security_database()
        self._init_audit_database()
        
        # Load encryption key
        self._load_encryption_key()
        
        # Load security policies
        self._load_security_policies()
    
    def _init_security_database(self):
        """Initialize security database"""
        with sqlite3.connect(self.security_db_path) as conn:
            cursor = conn.cursor()
            
            # Access control table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access_control (
                    rule_id TEXT PRIMARY KEY,
                    user TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    access_level TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Security policies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_policies (
                    policy_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    rules TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Encryption keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS encryption_keys (
                    key_id TEXT PRIMARY KEY,
                    key_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.commit()
    
    def _init_audit_database(self):
        """Initialize audit database"""
        with sqlite3.connect(self.audit_db_path) as conn:
            cursor = conn.cursor()
            
            # Security events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    user TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    level TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    details TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    risk_score REAL DEFAULT 0.0
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON security_events(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user ON security_events(user)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_level ON security_events(level)
            ''')
            
            conn.commit()
    
    def _load_encryption_key(self):
        """Load or generate encryption key"""
        try:
            with sqlite3.connect(self.security_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT key_data FROM encryption_keys 
                    WHERE active = 1 
                    ORDER BY created_at DESC 
                    LIMIT 1
                ''')
                
                row = cursor.fetchone()
                if row:
                    self.encryption_key = row[0].encode()
                else:
                    # Generate new encryption key
                    self.encryption_key = Fernet.generate_key()
                    
                    cursor.execute('''
                        INSERT INTO encryption_keys (key_id, key_data, active)
                        VALUES (?, ?, 1)
                    ''', (f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}", self.encryption_key.decode()))
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Failed to load encryption key: {e}")
            self.encryption_key = Fernet.generate_key()
    
    def _load_security_policies(self):
        """Load security policies from database"""
        self.security_policies = {}
        try:
            with sqlite3.connect(self.security_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM security_policies WHERE enabled = 1')
                rows = cursor.fetchall()
                
                for row in rows:
                    policy = SecurityPolicy(
                        policy_id=row[0],
                        name=row[1],
                        description=row[2],
                        rules=json.loads(row[3]),
                        enabled=bool(row[4]),
                        created_at=datetime.fromisoformat(row[5])
                    )
                    self.security_policies[policy.policy_id] = policy
                    
        except Exception as e:
            logger.error(f"Failed to load security policies: {e}")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            if not self.encryption_key:
                raise ValueError("Encryption key not available")
            
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            if not self.encryption_key:
                raise ValueError("Encryption key not available")
            
            fernet = Fernet(self.encryption_key)
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            raise
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        return key.decode(), base64.b64encode(salt).decode()
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            salt_bytes = base64.b64decode(salt.encode())
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_bytes,
                iterations=100000,
            )
            key = base64.b64encode(kdf.derive(password.encode()))
            return hmac.compare_digest(key.decode(), hashed_password)
        except Exception:
            return False
    
    def log_security_event(self, user: str, action: str, resource: str, 
                          level: SecurityLevel, ip_address: str, user_agent: str,
                          details: Dict[str, Any], success: bool = True) -> str:
        """Log security event"""
        try:
            event_id = f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(f'{user}{action}{resource}'.encode()).hexdigest()[:8]}"
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(action, level, success, details)
            
            event = SecurityEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                user=user,
                action=action,
                resource=resource,
                level=level,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                success=success,
                risk_score=risk_score
            )
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO security_events 
                    (event_id, timestamp, user, action, resource, level, ip_address, user_agent, details, success, risk_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.event_id,
                    event.timestamp.isoformat(),
                    event.user,
                    event.action,
                    event.resource,
                    event.level.value,
                    event.ip_address,
                    event.user_agent,
                    json.dumps(event.details),
                    event.success,
                    event.risk_score
                ))
                conn.commit()
            
            # Check for security violations
            self._check_security_violations(event)
            
            logger.info(f"Security event logged: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            return ""
    
    def _calculate_risk_score(self, action: str, level: SecurityLevel, 
                            success: bool, details: Dict[str, Any]) -> float:
        """Calculate risk score for security event"""
        base_score = 0.0
        
        # Base score by security level
        level_scores = {
            SecurityLevel.LOW: 0.1,
            SecurityLevel.MEDIUM: 0.3,
            SecurityLevel.HIGH: 0.6,
            SecurityLevel.CRITICAL: 1.0
        }
        base_score += level_scores.get(level, 0.0)
        
        # Adjust for failed actions
        if not success:
            base_score += 0.3
        
        # Adjust for sensitive actions
        sensitive_actions = ['admin_access', 'data_export', 'user_creation', 'permission_change']
        if any(sensitive in action.lower() for sensitive in sensitive_actions):
            base_score += 0.2
        
        # Adjust for unusual patterns
        if details.get('unusual_pattern', False):
            base_score += 0.4
        
        return min(base_score, 1.0)
    
    def _check_security_violations(self, event: SecurityEvent):
        """Check for security violations and trigger alerts"""
        try:
            # Check for high-risk events
            if event.risk_score > 0.8:
                self._trigger_security_alert(event, "High risk security event detected")
            
            # Check for repeated failed attempts
            if not event.success:
                failed_attempts = self._count_recent_failed_attempts(event.user, event.resource)
                if failed_attempts > 5:
                    self._trigger_security_alert(event, f"Multiple failed attempts detected: {failed_attempts}")
            
            # Check for unusual access patterns
            if self._detect_unusual_access(event):
                self._trigger_security_alert(event, "Unusual access pattern detected")
                
        except Exception as e:
            logger.error(f"Failed to check security violations: {e}")
    
    def _count_recent_failed_attempts(self, user: str, resource: str, minutes: int = 15) -> int:
        """Count recent failed attempts"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM security_events 
                    WHERE user = ? AND resource = ? AND success = 0 AND timestamp > ?
                ''', (user, resource, cutoff_time.isoformat()))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Failed to count failed attempts: {e}")
            return 0
    
    def _detect_unusual_access(self, event: SecurityEvent) -> bool:
        """Detect unusual access patterns"""
        try:
            # Check for access from new IP
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM security_events 
                    WHERE user = ? AND ip_address = ? AND timestamp > datetime('now', '-30 days')
                ''', (event.user, event.ip_address))
                
                ip_count = cursor.fetchone()[0]
                if ip_count == 0:
                    return True
                
                # Check for access outside normal hours
                hour = event.timestamp.hour
                if hour < 6 or hour > 22:
                    return True
                
                # Check for access from unusual location (simplified)
                if event.ip_address.startswith('192.168.') or event.ip_address.startswith('10.'):
                    return False  # Internal network
                else:
                    return True  # External network
                    
        except Exception as e:
            logger.error(f"Failed to detect unusual access: {e}")
            return False
    
    def _trigger_security_alert(self, event: SecurityEvent, message: str):
        """Trigger security alert"""
        try:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'event_id': event.event_id,
                'user': event.user,
                'action': event.action,
                'resource': event.resource,
                'risk_score': event.risk_score,
                'message': message,
                'ip_address': event.ip_address
            }
            
            # Log alert
            logger.warning(f"SECURITY ALERT: {message} - Event: {event.event_id}")
            
            # Store alert in database
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS security_alerts (
                        alert_id TEXT PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL,
                        event_id TEXT NOT NULL,
                        message TEXT NOT NULL,
                        resolved BOOLEAN DEFAULT 0
                    )
                ''')
                
                alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                cursor.execute('''
                    INSERT INTO security_alerts (alert_id, timestamp, event_id, message)
                    VALUES (?, ?, ?, ?)
                ''', (alert_id, datetime.now().isoformat(), event.event_id, message))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to trigger security alert: {e}")
    
    def create_access_control(self, user: str, resource: str, access_level: AccessLevel,
                            conditions: Dict[str, Any] = None, expires_at: datetime = None) -> str:
        """Create access control rule"""
        try:
            rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(f'{user}{resource}'.encode()).hexdigest()[:8]}"
            
            access_control = AccessControl(
                rule_id=rule_id,
                user=user,
                resource=resource,
                access_level=access_level,
                conditions=conditions or {},
                expires_at=expires_at
            )
            
            with sqlite3.connect(self.security_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO access_control 
                    (rule_id, user, resource, access_level, conditions, expires_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rule_id, user, resource, access_level.value,
                    json.dumps(conditions or {}),
                    expires_at.isoformat() if expires_at else None,
                    datetime.now().isoformat()
                ))
                conn.commit()
            
            logger.info(f"Access control rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Failed to create access control: {e}")
            return ""
    
    def check_access(self, user: str, resource: str, required_level: AccessLevel) -> bool:
        """Check if user has access to resource"""
        try:
            with sqlite3.connect(self.security_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT access_level, conditions, expires_at FROM access_control 
                    WHERE user = ? AND resource = ? AND (expires_at IS NULL OR expires_at > ?)
                ''', (user, resource, datetime.now().isoformat()))
                
                rows = cursor.fetchall()
                if not rows:
                    return False
                
                # Check access levels
                access_levels = [AccessLevel.READ, AccessLevel.WRITE, AccessLevel.ADMIN, AccessLevel.AUDIT]
                user_levels = [AccessLevel(row[0]) for row in rows]
                
                required_index = access_levels.index(required_level)
                user_max_index = max([access_levels.index(level) for level in user_levels])
                
                return user_max_index >= required_index
                
        except Exception as e:
            logger.error(f"Failed to check access: {e}")
            return False
    
    def get_security_events(self, start_date: datetime = None, end_date: datetime = None,
                           user: str = None, level: SecurityLevel = None) -> List[SecurityEvent]:
        """Get security events with filtering"""
        try:
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM security_events WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if user:
                    query += " AND user = ?"
                    params.append(user)
                
                if level:
                    query += " AND level = ?"
                    params.append(level.value)
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                events = []
                for row in rows:
                    event = SecurityEvent(
                        event_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        user=row[2],
                        action=row[3],
                        resource=row[4],
                        level=SecurityLevel(row[5]),
                        ip_address=row[6],
                        user_agent=row[7],
                        details=json.loads(row[8]),
                        success=bool(row[9]),
                        risk_score=row[10]
                    )
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return []
    
    def generate_security_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate security report"""
        try:
            events = self.get_security_events(start_date, end_date)
            
            # Calculate statistics
            total_events = len(events)
            successful_events = sum(1 for e in events if e.success)
            failed_events = total_events - successful_events
            
            # Risk distribution
            risk_distribution = {
                'low': sum(1 for e in events if e.risk_score < 0.3),
                'medium': sum(1 for e in events if 0.3 <= e.risk_score < 0.7),
                'high': sum(1 for e in events if e.risk_score >= 0.7)
            }
            
            # Top users by activity
            user_activity = {}
            for event in events:
                user_activity[event.user] = user_activity.get(event.user, 0) + 1
            
            top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Top actions
            action_counts = {}
            for event in events:
                action_counts[event.action] = action_counts.get(event.action, 0) + 1
            
            top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'report_period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'summary': {
                    'total_events': total_events,
                    'successful_events': successful_events,
                    'failed_events': failed_events,
                    'success_rate': successful_events / total_events if total_events > 0 else 0
                },
                'risk_distribution': risk_distribution,
                'top_users': top_users,
                'top_actions': top_actions,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate security report: {e}")
            return {}
    
    def cleanup_old_events(self, days: int = 90):
        """Clean up old security events"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM security_events 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_count} old security events")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0