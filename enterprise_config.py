#!/usr/bin/env python3
"""
Enterprise Configuration Management
Handles enterprise settings, security policies, and compliance features
"""

import json
import os
import sqlite3
import hashlib
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import secrets
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnterpriseSettings:
    """Enterprise configuration settings"""
    # AI Configuration
    local_ai_url: str
    local_ai_model: str = "local-copilot"
    local_api_key: Optional[str] = None
    
    # Network Configuration
    proxy_url: Optional[str] = None
    cert_path: Optional[str] = None
    verify_ssl: bool = True
    
    # Security Configuration
    audit_enabled: bool = True
    data_encryption: bool = True
    session_timeout: int = 3600  # 1 hour
    
    # Compliance Configuration
    data_retention_days: int = 365
    log_retention_days: int = 90
    compliance_mode: str = "standard"  # standard, strict, custom
    
    # Feature Flags
    offline_mode: bool = False
    custom_models: bool = False
    external_integrations: bool = False

@dataclass
class SecurityPolicy:
    """Enterprise security policy"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: str
    timestamp: datetime
    user: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class EnterpriseConfigManager:
    """Manages enterprise configuration and security"""
    
    def __init__(self, config_path: str = "enterprise_config.db"):
        self.config_path = config_path
        self.db_path = os.path.join(os.path.dirname(config_path), "enterprise.db")
        self.init_database()
        
    def init_database(self):
        """Initialize enterprise database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS enterprise_settings (
                        id INTEGER PRIMARY KEY,
                        setting_key TEXT UNIQUE NOT NULL,
                        setting_value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create security policies table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS security_policies (
                        id INTEGER PRIMARY KEY,
                        policy_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        rules TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create audit log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY,
                        log_id TEXT UNIQUE NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        user TEXT NOT NULL,
                        action TEXT NOT NULL,
                        resource TEXT NOT NULL,
                        details TEXT NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT
                    )
                ''')
                
                # Create compliance reports table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS compliance_reports (
                        id INTEGER PRIMARY KEY,
                        report_id TEXT UNIQUE NOT NULL,
                        report_type TEXT NOT NULL,
                        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data TEXT NOT NULL,
                        status TEXT DEFAULT 'generated'
                    )
                ''')
                
                conn.commit()
                logger.info("Enterprise database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize enterprise database: {e}")
            raise
    
    def save_enterprise_settings(self, settings: EnterpriseSettings) -> bool:
        """Save enterprise settings to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Convert settings to dictionary
                settings_dict = asdict(settings)
                
                for key, value in settings_dict.items():
                    # Encrypt sensitive values
                    if key in ['local_api_key'] and value:
                        value = self._encrypt_value(str(value))
                    
                    # Insert or update setting
                    cursor.execute('''
                        INSERT OR REPLACE INTO enterprise_settings 
                        (setting_key, setting_value, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    ''', (key, json.dumps(value)))
                
                conn.commit()
                logger.info("Enterprise settings saved successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save enterprise settings: {e}")
            return False
    
    def load_enterprise_settings(self) -> Optional[EnterpriseSettings]:
        """Load enterprise settings from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT setting_key, setting_value FROM enterprise_settings')
                rows = cursor.fetchall()
                
                if not rows:
                    return None
                
                # Convert rows to dictionary
                settings_dict = {}
                for key, value in rows:
                    # Decrypt sensitive values
                    if key in ['local_api_key'] and value:
                        try:
                            value = self._decrypt_value(value)
                        except:
                            value = None
                    
                    settings_dict[key] = json.loads(value)
                
                # Create EnterpriseSettings object
                return EnterpriseSettings(**settings_dict)
                
        except Exception as e:
            logger.error(f"Failed to load enterprise settings: {e}")
            return None
    
    def save_security_policy(self, policy: SecurityPolicy) -> bool:
        """Save security policy to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO security_policies 
                    (policy_id, name, description, rules, enabled, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    policy.policy_id,
                    policy.name,
                    policy.description,
                    json.dumps(policy.rules),
                    policy.enabled,
                    policy.created_at.isoformat()
                ))
                
                conn.commit()
                logger.info(f"Security policy '{policy.name}' saved successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save security policy: {e}")
            return False
    
    def load_security_policies(self) -> List[SecurityPolicy]:
        """Load all security policies from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT policy_id, name, description, rules, enabled, created_at
                    FROM security_policies
                ''')
                rows = cursor.fetchall()
                
                policies = []
                for row in rows:
                    policy = SecurityPolicy(
                        policy_id=row[0],
                        name=row[1],
                        description=row[2],
                        rules=json.loads(row[3]),
                        enabled=bool(row[4]),
                        created_at=datetime.fromisoformat(row[5])
                    )
                    policies.append(policy)
                
                return policies
                
        except Exception as e:
            logger.error(f"Failed to load security policies: {e}")
            return []
    
    def log_audit_event(self, user: str, action: str, resource: str, 
                       details: Dict[str, Any], ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None) -> bool:
        """Log audit event for compliance"""
        try:
            log_id = secrets.token_urlsafe(16)
            
            audit_log = AuditLog(
                log_id=log_id,
                timestamp=datetime.now(),
                user=user,
                action=action,
                resource=resource,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO audit_log 
                    (log_id, timestamp, user, action, resource, details, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    audit_log.log_id,
                    audit_log.timestamp.isoformat(),
                    audit_log.user,
                    audit_log.action,
                    audit_log.resource,
                    json.dumps(audit_log.details),
                    audit_log.ip_address,
                    audit_log.user_agent
                ))
                
                conn.commit()
                logger.info(f"Audit event logged: {action} by {user}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            return False
    
    def get_audit_logs(self, start_date: Optional[datetime] = None, 
                      end_date: Optional[datetime] = None,
                      user: Optional[str] = None,
                      action: Optional[str] = None) -> List[AuditLog]:
        """Get audit logs with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                query = "SELECT log_id, timestamp, user, action, resource, details, ip_address, user_agent FROM audit_log WHERE 1=1"
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
                
                if action:
                    query += " AND action = ?"
                    params.append(action)
                
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                logs = []
                for row in rows:
                    log = AuditLog(
                        log_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        user=row[2],
                        action=row[3],
                        resource=row[4],
                        details=json.loads(row[5]),
                        ip_address=row[6],
                        user_agent=row[7]
                    )
                    logs.append(log)
                
                return logs
                
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []
    
    def generate_compliance_report(self, report_type: str, 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> str:
        """Generate compliance report"""
        try:
            report_id = secrets.token_urlsafe(16)
            
            # Generate report based on type
            if report_type == "audit_summary":
                report_data = self._generate_audit_summary_report(start_date, end_date)
            elif report_type == "security_policy_compliance":
                report_data = self._generate_security_compliance_report()
            elif report_type == "data_usage":
                report_data = self._generate_data_usage_report(start_date, end_date)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            # Save report to database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO compliance_reports 
                    (report_id, report_type, data, status)
                    VALUES (?, ?, ?, ?)
                ''', (report_id, report_type, json.dumps(report_data), "generated"))
                
                conn.commit()
            
            logger.info(f"Compliance report '{report_type}' generated: {report_id}")
            return report_id
            
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {e}")
            raise
    
    def _generate_audit_summary_report(self, start_date: Optional[datetime], 
                                     end_date: Optional[datetime]) -> Dict[str, Any]:
        """Generate audit summary report"""
        logs = self.get_audit_logs(start_date, end_date)
        
        # Calculate statistics
        total_events = len(logs)
        unique_users = len(set(log.user for log in logs))
        action_counts = {}
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
        
        return {
            "report_type": "audit_summary",
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "statistics": {
                "total_events": total_events,
                "unique_users": unique_users,
                "action_counts": action_counts
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_security_compliance_report(self) -> Dict[str, Any]:
        """Generate security policy compliance report"""
        policies = self.load_security_policies()
        
        return {
            "report_type": "security_policy_compliance",
            "policies": [
                {
                    "policy_id": policy.policy_id,
                    "name": policy.name,
                    "enabled": policy.enabled,
                    "rules_count": len(policy.rules)
                }
                for policy in policies
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_data_usage_report(self, start_date: Optional[datetime], 
                                   end_date: Optional[datetime]) -> Dict[str, Any]:
        """Generate data usage report"""
        logs = self.get_audit_logs(start_date, end_date)
        
        # Analyze data usage patterns
        ai_usage = [log for log in logs if log.action.startswith("ai_")]
        test_generation = [log for log in logs if log.action == "generate_test_cases"]
        
        return {
            "report_type": "data_usage",
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "usage_statistics": {
                "total_ai_requests": len(ai_usage),
                "test_generation_requests": len(test_generation),
                "unique_resources": len(set(log.resource for log in logs))
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt sensitive value"""
        # Simple base64 encoding for now - in production, use proper encryption
        return base64.b64encode(value.encode()).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive value"""
        # Simple base64 decoding for now - in production, use proper decryption
        return base64.b64decode(encrypted_value.encode()).decode()
    
    def cleanup_old_data(self):
        """Clean up old data based on retention policies"""
        try:
            settings = self.load_enterprise_settings()
            if not settings:
                return
            
            cutoff_date = datetime.now() - timedelta(days=settings.data_retention_days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old audit logs
                cursor.execute('''
                    DELETE FROM audit_log 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_logs = cursor.rowcount
                
                # Clean up old compliance reports
                cursor.execute('''
                    DELETE FROM compliance_reports 
                    WHERE generated_at < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_reports = cursor.rowcount
                
                conn.commit()
                
                logger.info(f"Cleaned up {deleted_logs} old audit logs and {deleted_reports} old reports")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            settings = self.load_enterprise_settings()
            policies = self.load_security_policies()
            
            # Get recent audit logs
            recent_logs = self.get_audit_logs(
                start_date=datetime.now() - timedelta(hours=24)
            )
            
            return {
                "status": "healthy",
                "enterprise_mode": True,
                "settings_configured": settings is not None,
                "security_policies": len(policies),
                "recent_activity": len(recent_logs),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }