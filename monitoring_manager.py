"""
Comprehensive Monitoring and Logging Manager for Assertly
Provides performance monitoring, logging, and system health tracking
"""

import logging
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from functools import wraps
import traceback
from cache_manager import cache_manager

class MonitoringManager:
    """Comprehensive monitoring and logging manager"""
    
    def __init__(self, app=None):
        """Initialize monitoring manager"""
        self.app = app
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.performance_metrics = []
        self.setup_logging()
        
        if app:
            self.setup_app_monitoring(app)
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handlers
        file_handler = logging.FileHandler('logs/assertly.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        performance_handler = logging.FileHandler('logs/performance.log')
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(simple_formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(simple_formatter)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, error_handler, performance_handler, console_handler]
        )
        
        # Create specific loggers
        self.app_logger = logging.getLogger('assertly.app')
        self.performance_logger = logging.getLogger('assertly.performance')
        self.security_logger = logging.getLogger('assertly.security')
        self.audit_logger = logging.getLogger('assertly.audit')
        
        # Create logs directory if it doesn't exist
        import os
        os.makedirs('logs', exist_ok=True)
    
    def setup_app_monitoring(self, app):
        """Setup Flask app monitoring"""
        from flask import request, g, session
        
        @app.before_request
        def before_request():
            """Log request start"""
            g.start_time = time.time()
            g.request_id = f"req_{int(time.time() * 1000)}"
            
            self.app_logger.info(f"Request started: {request.method} {request.path} - {g.request_id}")
            
            # Track user activity
            if hasattr(session, 'get') and session.get('user_id'):
                cache_manager.set_user_activity(
                    session['user_id'], 
                    f"Accessed {request.path}"
                )
        
        @app.after_request
        def after_request(response):
            """Log request completion"""
            if hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                
                # Log performance metrics
                self.performance_logger.info(
                    f"Request completed: {request.method} {request.path} - "
                    f"Status: {response.status_code} - Duration: {duration:.3f}s - {g.request_id}"
                )
                
                # Store performance data
                self._store_performance_metric({
                    'endpoint': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'duration': duration,
                    'timestamp': datetime.now().isoformat(),
                    'request_id': g.request_id
                })
                
                # Update request count
                self.request_count += 1
                
                # Add performance headers
                response.headers['X-Response-Time'] = f"{duration:.3f}s"
                response.headers['X-Request-ID'] = g.request_id
            
            return response
        
        @app.errorhandler(Exception)
        def handle_exception(e):
            """Handle unhandled exceptions"""
            self.error_count += 1
            
            # Log error details
            error_details = {
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat(),
                'request_path': request.path if request else 'unknown',
                'request_method': request.method if request else 'unknown'
            }
            
            self.app_logger.error(f"Unhandled exception: {json.dumps(error_details)}")
            
            # Store error in cache for monitoring
            cache_manager.set_cache(
                f"error:{int(time.time())}", 
                error_details, 
                expire_seconds=86400  # 24 hours
            )
            
            return {'error': 'Internal server error'}, 500
    
    def _store_performance_metric(self, metric: Dict[str, Any]):
        """Store performance metric"""
        self.performance_metrics.append(metric)
        
        # Keep only last 1000 metrics in memory
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
        
        # Store in cache
        cache_manager.set_cache(
            f"performance:{metric['request_id']}", 
            metric, 
            expire_seconds=3600
        )
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info().rss
            process_cpu = process.cpu_percent()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'uptime': (datetime.now() - self.start_time).total_seconds(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'percent': memory_percent,
                    'available': memory_available,
                    'total': memory.total
                },
                'disk': {
                    'percent': disk_percent,
                    'used': disk.used,
                    'total': disk.total
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'memory': process_memory,
                    'cpu_percent': process_cpu
                },
                'application': {
                    'request_count': self.request_count,
                    'error_count': self.error_count,
                    'cache_stats': cache_manager.get_cache_stats()
                }
            }
        except Exception as e:
            self.app_logger.error(f"Failed to get system metrics: {e}")
            return {'error': str(e)}
    
    def get_performance_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance summary for last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics from last N hours
        recent_metrics = [
            m for m in self.performance_metrics 
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return {'message': 'No performance data available'}
        
        # Calculate statistics
        durations = [m['duration'] for m in recent_metrics]
        status_codes = [m['status_code'] for m in recent_metrics]
        
        return {
            'period_hours': hours,
            'total_requests': len(recent_metrics),
            'average_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'status_codes': {
                '200': status_codes.count(200),
                '400': status_codes.count(400),
                '401': status_codes.count(401),
                '404': status_codes.count(404),
                '500': status_codes.count(500)
            },
            'error_rate': status_codes.count(500) / len(status_codes) * 100,
            'endpoints': self._get_endpoint_stats(recent_metrics)
        }
    
    def _get_endpoint_stats(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get endpoint statistics"""
        endpoint_stats = {}
        
        for metric in metrics:
            endpoint = metric['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'count': 0,
                    'total_duration': 0,
                    'avg_duration': 0,
                    'max_duration': 0,
                    'min_duration': float('inf')
                }
            
            stats = endpoint_stats[endpoint]
            stats['count'] += 1
            stats['total_duration'] += metric['duration']
            stats['max_duration'] = max(stats['max_duration'], metric['duration'])
            stats['min_duration'] = min(stats['min_duration'], metric['duration'])
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            stats['avg_duration'] = stats['total_duration'] / stats['count']
            if stats['min_duration'] == float('inf'):
                stats['min_duration'] = 0
        
        return endpoint_stats
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        security_event = {
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'ip_address': details.get('ip_address', 'unknown'),
            'user_id': details.get('user_id', 'anonymous')
        }
        
        self.security_logger.warning(f"Security event: {json.dumps(security_event)}")
        
        # Store in cache for monitoring
        cache_manager.set_cache(
            f"security:{int(time.time())}", 
            security_event, 
            expire_seconds=86400 * 30  # 30 days
        )
    
    def log_audit_event(self, action: str, resource: str, details: Dict[str, Any]):
        """Log audit events"""
        audit_event = {
            'action': action,
            'resource': resource,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'user_id': details.get('user_id', 'system'),
            'ip_address': details.get('ip_address', 'unknown')
        }
        
        self.audit_logger.info(f"Audit event: {json.dumps(audit_event)}")
        
        # Store in cache for compliance
        cache_manager.set_cache(
            f"audit:{int(time.time())}", 
            audit_event, 
            expire_seconds=86400 * 365  # 1 year
        )
    
    def monitor_function(self, func_name: str = None):
        """Decorator to monitor function performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                function_name = func_name or func.__name__
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    self.performance_logger.info(
                        f"Function {function_name} completed in {duration:.3f}s"
                    )
                    
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.app_logger.error(
                        f"Function {function_name} failed after {duration:.3f}s: {e}"
                    )
                    raise
            
            return wrapper
        return decorator
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        system_metrics = self.get_system_metrics()
        
        # Determine health status
        health_status = "healthy"
        issues = []
        
        # Check CPU usage
        if system_metrics.get('cpu', {}).get('percent', 0) > 80:
            health_status = "warning"
            issues.append("High CPU usage")
        
        # Check memory usage
        if system_metrics.get('memory', {}).get('percent', 0) > 85:
            health_status = "warning"
            issues.append("High memory usage")
        
        # Check disk usage
        if system_metrics.get('disk', {}).get('percent', 0) > 90:
            health_status = "critical"
            issues.append("High disk usage")
        
        # Check error rate
        if self.error_count > 0:
            error_rate = self.error_count / max(self.request_count, 1) * 100
            if error_rate > 5:
                health_status = "warning"
                issues.append(f"High error rate: {error_rate:.1f}%")
        
        return {
            'status': health_status,
            'issues': issues,
            'timestamp': datetime.now().isoformat(),
            'uptime': system_metrics.get('uptime', 0),
            'metrics': system_metrics
        }

# Global monitoring manager instance
monitoring_manager = None

def init_monitoring_manager(app):
    """Initialize monitoring manager"""
    global monitoring_manager
    monitoring_manager = MonitoringManager(app)
    return monitoring_manager