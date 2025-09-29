"""
Advanced Analytics Manager for Assertly
Provides business intelligence, user analytics, and performance insights
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import logging

class AnalyticsManager:
    """Advanced analytics manager for business intelligence"""
    
    def __init__(self, app=None):
        """Initialize analytics manager"""
        self.app = app
        self.analytics_data = {
            'user_events': [],
            'page_views': [],
            'feature_usage': [],
            'performance_metrics': [],
            'business_metrics': []
        }
        self.start_time = datetime.utcnow()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Add template globals for analytics
        app.jinja_env.globals['track_event'] = self.track_event
        app.jinja_env.globals['get_user_analytics'] = self.get_user_analytics
    
    def track_event(self, event_type: str, event_data: Dict[str, Any] = None, user_id: str = None):
        """Track user event"""
        try:
            event = {
                'event_type': event_type,
                'event_data': event_data or {},
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': self._get_session_id(),
                'ip_address': self._get_client_ip(),
                'user_agent': self._get_user_agent()
            }
            
            self.analytics_data['user_events'].append(event)
            
            # Keep only last 10000 events to prevent memory issues
            if len(self.analytics_data['user_events']) > 10000:
                self.analytics_data['user_events'] = self.analytics_data['user_events'][-10000:]
            
            logging.info(f"Tracked event: {event_type}")
            
        except Exception as e:
            logging.error(f"Failed to track event: {e}")
    
    def track_page_view(self, page: str, user_id: str = None, duration: float = None):
        """Track page view"""
        try:
            page_view = {
                'page': page,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'duration': duration,
                'session_id': self._get_session_id(),
                'ip_address': self._get_client_ip()
            }
            
            self.analytics_data['page_views'].append(page_view)
            
            # Keep only last 5000 page views
            if len(self.analytics_data['page_views']) > 5000:
                self.analytics_data['page_views'] = self.analytics_data['page_views'][-5000:]
            
        except Exception as e:
            logging.error(f"Failed to track page view: {e}")
    
    def track_feature_usage(self, feature: str, user_id: str = None, usage_data: Dict[str, Any] = None):
        """Track feature usage"""
        try:
            feature_usage = {
                'feature': feature,
                'user_id': user_id,
                'usage_data': usage_data or {},
                'timestamp': datetime.utcnow().isoformat(),
                'session_id': self._get_session_id()
            }
            
            self.analytics_data['feature_usage'].append(feature_usage)
            
            # Keep only last 5000 feature usages
            if len(self.analytics_data['feature_usage']) > 5000:
                self.analytics_data['feature_usage'] = self.analytics_data['feature_usage'][-5000:]
            
        except Exception as e:
            logging.error(f"Failed to track feature usage: {e}")
    
    def track_performance_metric(self, metric_name: str, value: float, metadata: Dict[str, Any] = None):
        """Track performance metric"""
        try:
            metric = {
                'metric_name': metric_name,
                'value': value,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.analytics_data['performance_metrics'].append(metric)
            
            # Keep only last 2000 performance metrics
            if len(self.analytics_data['performance_metrics']) > 2000:
                self.analytics_data['performance_metrics'] = self.analytics_data['performance_metrics'][-2000:]
            
        except Exception as e:
            logging.error(f"Failed to track performance metric: {e}")
    
    def get_user_analytics(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get user analytics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Filter events by date and user
            user_events = [
                event for event in self.analytics_data['user_events']
                if (user_id is None or event.get('user_id') == user_id) and
                datetime.fromisoformat(event['timestamp']) > cutoff_date
            ]
            
            page_views = [
                pv for pv in self.analytics_data['page_views']
                if (user_id is None or pv.get('user_id') == user_id) and
                datetime.fromisoformat(pv['timestamp']) > cutoff_date
            ]
            
            feature_usage = [
                fu for fu in self.analytics_data['feature_usage']
                if (user_id is None or fu.get('user_id') == user_id) and
                datetime.fromisoformat(fu['timestamp']) > cutoff_date
            ]
            
            # Calculate analytics
            analytics = {
                'total_events': len(user_events),
                'total_page_views': len(page_views),
                'total_feature_usage': len(feature_usage),
                'unique_users': len(set(event.get('user_id') for event in user_events if event.get('user_id'))),
                'most_visited_pages': self._get_most_visited_pages(page_views),
                'most_used_features': self._get_most_used_features(feature_usage),
                'event_types': self._get_event_type_distribution(user_events),
                'daily_activity': self._get_daily_activity(user_events),
                'user_engagement': self._calculate_user_engagement(user_events, page_views),
                'feature_adoption': self._calculate_feature_adoption(feature_usage)
            }
            
            return analytics
            
        except Exception as e:
            logging.error(f"Failed to get user analytics: {e}")
            return {}
    
    def get_business_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get business metrics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Filter data by date
            recent_events = [
                event for event in self.analytics_data['user_events']
                if datetime.fromisoformat(event['timestamp']) > cutoff_date
            ]
            
            recent_page_views = [
                pv for pv in self.analytics_data['page_views']
                if datetime.fromisoformat(pv['timestamp']) > cutoff_date
            ]
            
            # Calculate business metrics
            metrics = {
                'total_active_users': len(set(event.get('user_id') for event in recent_events if event.get('user_id'))),
                'total_sessions': len(set(event.get('session_id') for event in recent_events if event.get('session_id'))),
                'total_page_views': len(recent_page_views),
                'average_session_duration': self._calculate_average_session_duration(recent_events),
                'bounce_rate': self._calculate_bounce_rate(recent_page_views),
                'conversion_rate': self._calculate_conversion_rate(recent_events),
                'user_retention': self._calculate_user_retention(recent_events),
                'feature_usage_growth': self._calculate_feature_usage_growth(),
                'geographic_distribution': self._get_geographic_distribution(recent_events),
                'device_distribution': self._get_device_distribution(recent_events)
            }
            
            return metrics
            
        except Exception as e:
            logging.error(f"Failed to get business metrics: {e}")
            return {}
    
    def get_performance_analytics(self, metric_name: str = None, days: int = 7) -> Dict[str, Any]:
        """Get performance analytics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Filter performance metrics
            recent_metrics = [
                metric for metric in self.analytics_data['performance_metrics']
                if datetime.fromisoformat(metric['timestamp']) > cutoff_date and
                (metric_name is None or metric['metric_name'] == metric_name)
            ]
            
            if not recent_metrics:
                return {}
            
            # Calculate performance analytics
            values = [metric['value'] for metric in recent_metrics]
            
            analytics = {
                'metric_name': metric_name or 'all_metrics',
                'total_measurements': len(values),
                'average_value': sum(values) / len(values),
                'min_value': min(values),
                'max_value': max(values),
                'median_value': sorted(values)[len(values) // 2],
                'percentile_95': sorted(values)[int(len(values) * 0.95)],
                'trend': self._calculate_trend(values),
                'daily_averages': self._get_daily_averages(recent_metrics)
            }
            
            return analytics
            
        except Exception as e:
            logging.error(f"Failed to get performance analytics: {e}")
            return {}
    
    def get_feature_analytics(self, feature: str = None, days: int = 30) -> Dict[str, Any]:
        """Get feature usage analytics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Filter feature usage
            recent_usage = [
                usage for usage in self.analytics_data['feature_usage']
                if datetime.fromisoformat(usage['timestamp']) > cutoff_date and
                (feature is None or usage['feature'] == feature)
            ]
            
            if not recent_usage:
                return {}
            
            # Calculate feature analytics
            analytics = {
                'feature': feature or 'all_features',
                'total_usage': len(recent_usage),
                'unique_users': len(set(usage.get('user_id') for usage in recent_usage if usage.get('user_id'))),
                'usage_frequency': self._calculate_usage_frequency(recent_usage),
                'user_adoption': self._calculate_user_adoption(recent_usage),
                'usage_trends': self._get_usage_trends(recent_usage),
                'feature_correlation': self._get_feature_correlation(recent_usage)
            }
            
            return analytics
            
        except Exception as e:
            logging.error(f"Failed to get feature analytics: {e}")
            return {}
    
    def export_analytics_data(self, format: str = 'json') -> str:
        """Export analytics data"""
        try:
            if format == 'json':
                return json.dumps(self.analytics_data, indent=2, default=str)
            elif format == 'csv':
                # Convert to CSV format (simplified)
                return self._convert_to_csv()
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logging.error(f"Failed to export analytics data: {e}")
            return ""
    
    def _get_session_id(self) -> str:
        """Get session ID"""
        try:
            if hasattr(request, 'session') and request.session:
                return request.session.get('session_id', 'anonymous')
            return 'anonymous'
        except:
            return 'anonymous'
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        try:
            if hasattr(request, 'remote_addr'):
                return request.remote_addr
            return 'unknown'
        except:
            return 'unknown'
    
    def _get_user_agent(self) -> str:
        """Get user agent"""
        try:
            if hasattr(request, 'headers'):
                return request.headers.get('User-Agent', 'unknown')
            return 'unknown'
        except:
            return 'unknown'
    
    def _get_most_visited_pages(self, page_views: List[Dict]) -> List[Dict]:
        """Get most visited pages"""
        page_counts = Counter(pv['page'] for pv in page_views)
        return [{'page': page, 'views': count} for page, count in page_counts.most_common(10)]
    
    def _get_most_used_features(self, feature_usage: List[Dict]) -> List[Dict]:
        """Get most used features"""
        feature_counts = Counter(fu['feature'] for fu in feature_usage)
        return [{'feature': feature, 'usage_count': count} for feature, count in feature_counts.most_common(10)]
    
    def _get_event_type_distribution(self, events: List[Dict]) -> Dict[str, int]:
        """Get event type distribution"""
        return dict(Counter(event['event_type'] for event in events))
    
    def _get_daily_activity(self, events: List[Dict]) -> Dict[str, int]:
        """Get daily activity"""
        daily_counts = defaultdict(int)
        for event in events:
            date = datetime.fromisoformat(event['timestamp']).date().isoformat()
            daily_counts[date] += 1
        return dict(daily_counts)
    
    def _calculate_user_engagement(self, events: List[Dict], page_views: List[Dict]) -> Dict[str, float]:
        """Calculate user engagement metrics"""
        unique_users = len(set(event.get('user_id') for event in events if event.get('user_id')))
        total_events = len(events)
        total_page_views = len(page_views)
        
        return {
            'events_per_user': total_events / unique_users if unique_users > 0 else 0,
            'page_views_per_user': total_page_views / unique_users if unique_users > 0 else 0,
            'engagement_score': (total_events + total_page_views) / unique_users if unique_users > 0 else 0
        }
    
    def _calculate_feature_adoption(self, feature_usage: List[Dict]) -> Dict[str, float]:
        """Calculate feature adoption rates"""
        total_users = len(set(usage.get('user_id') for usage in feature_usage if usage.get('user_id')))
        feature_users = defaultdict(set)
        
        for usage in feature_usage:
            if usage.get('user_id'):
                feature_users[usage['feature']].add(usage['user_id'])
        
        adoption_rates = {}
        for feature, users in feature_users.items():
            adoption_rates[feature] = len(users) / total_users if total_users > 0 else 0
        
        return adoption_rates
    
    def _calculate_average_session_duration(self, events: List[Dict]) -> float:
        """Calculate average session duration"""
        session_durations = defaultdict(list)
        
        for event in events:
            session_id = event.get('session_id')
            if session_id:
                session_durations[session_id].append(datetime.fromisoformat(event['timestamp']))
        
        durations = []
        for session_events in session_durations.values():
            if len(session_events) > 1:
                duration = (max(session_events) - min(session_events)).total_seconds()
                durations.append(duration)
        
        return sum(durations) / len(durations) if durations else 0
    
    def _calculate_bounce_rate(self, page_views: List[Dict]) -> float:
        """Calculate bounce rate"""
        if not page_views:
            return 0
        
        single_page_sessions = 0
        total_sessions = len(set(pv.get('session_id') for pv in page_views if pv.get('session_id')))
        
        session_page_counts = defaultdict(int)
        for pv in page_views:
            session_id = pv.get('session_id')
            if session_id:
                session_page_counts[session_id] += 1
        
        single_page_sessions = sum(1 for count in session_page_counts.values() if count == 1)
        
        return (single_page_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    def _calculate_conversion_rate(self, events: List[Dict]) -> float:
        """Calculate conversion rate"""
        # This is a simplified conversion rate calculation
        # In a real application, you'd define what constitutes a conversion
        conversion_events = [event for event in events if event.get('event_type') == 'conversion']
        total_events = len(events)
        
        return (len(conversion_events) / total_events * 100) if total_events > 0 else 0
    
    def _calculate_user_retention(self, events: List[Dict]) -> Dict[str, float]:
        """Calculate user retention rates"""
        # Simplified retention calculation
        user_first_visit = {}
        user_return_visits = defaultdict(int)
        
        for event in events:
            user_id = event.get('user_id')
            if user_id:
                if user_id not in user_first_visit:
                    user_first_visit[user_id] = datetime.fromisoformat(event['timestamp']).date()
                else:
                    user_return_visits[user_id] += 1
        
        total_users = len(user_first_visit)
        returning_users = len([user for user, visits in user_return_visits.items() if visits > 0])
        
        return {
            'retention_rate': (returning_users / total_users * 100) if total_users > 0 else 0,
            'total_users': total_users,
            'returning_users': returning_users
        }
    
    def _calculate_feature_usage_growth(self) -> Dict[str, float]:
        """Calculate feature usage growth"""
        # Simplified growth calculation
        current_week = datetime.utcnow() - timedelta(days=7)
        previous_week = current_week - timedelta(days=7)
        
        current_usage = len([
            usage for usage in self.analytics_data['feature_usage']
            if datetime.fromisoformat(usage['timestamp']) > current_week
        ])
        
        previous_usage = len([
            usage for usage in self.analytics_data['feature_usage']
            if previous_week < datetime.fromisoformat(usage['timestamp']) <= current_week
        ])
        
        growth_rate = ((current_usage - previous_usage) / previous_usage * 100) if previous_usage > 0 else 0
        
        return {
            'current_week_usage': current_usage,
            'previous_week_usage': previous_usage,
            'growth_rate': growth_rate
        }
    
    def _get_geographic_distribution(self, events: List[Dict]) -> Dict[str, int]:
        """Get geographic distribution"""
        # Simplified geographic distribution
        countries = defaultdict(int)
        for event in events:
            ip = event.get('ip_address', '')
            # In a real application, you'd use a GeoIP service
            country = 'Unknown'
            countries[country] += 1
        
        return dict(countries)
    
    def _get_device_distribution(self, events: List[Dict]) -> Dict[str, int]:
        """Get device distribution"""
        devices = defaultdict(int)
        for event in events:
            user_agent = event.get('user_agent', '').lower()
            if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                devices['Mobile'] += 1
            elif 'tablet' in user_agent or 'ipad' in user_agent:
                devices['Tablet'] += 1
            else:
                devices['Desktop'] += 1
        
        return dict(devices)
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return 'increasing'
        elif second_avg < first_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_daily_averages(self, metrics: List[Dict]) -> Dict[str, float]:
        """Get daily averages for metrics"""
        daily_values = defaultdict(list)
        
        for metric in metrics:
            date = datetime.fromisoformat(metric['timestamp']).date().isoformat()
            daily_values[date].append(metric['value'])
        
        daily_averages = {}
        for date, values in daily_values.items():
            daily_averages[date] = sum(values) / len(values)
        
        return daily_averages
    
    def _calculate_usage_frequency(self, usage: List[Dict]) -> Dict[str, float]:
        """Calculate usage frequency"""
        user_usage_counts = defaultdict(int)
        
        for usage_item in usage:
            user_id = usage_item.get('user_id')
            if user_id:
                user_usage_counts[user_id] += 1
        
        if not user_usage_counts:
            return {}
        
        frequencies = list(user_usage_counts.values())
        return {
            'average_usage_per_user': sum(frequencies) / len(frequencies),
            'max_usage_per_user': max(frequencies),
            'min_usage_per_user': min(frequencies)
        }
    
    def _calculate_user_adoption(self, usage: List[Dict]) -> Dict[str, float]:
        """Calculate user adoption metrics"""
        unique_users = len(set(usage_item.get('user_id') for usage_item in usage if usage_item.get('user_id')))
        total_usage = len(usage)
        
        return {
            'unique_users': unique_users,
            'total_usage': total_usage,
            'usage_per_user': total_usage / unique_users if unique_users > 0 else 0
        }
    
    def _get_usage_trends(self, usage: List[Dict]) -> Dict[str, int]:
        """Get usage trends over time"""
        daily_usage = defaultdict(int)
        
        for usage_item in usage:
            date = datetime.fromisoformat(usage_item['timestamp']).date().isoformat()
            daily_usage[date] += 1
        
        return dict(daily_usage)
    
    def _get_feature_correlation(self, usage: List[Dict]) -> Dict[str, float]:
        """Get feature correlation"""
        # Simplified feature correlation
        user_features = defaultdict(set)
        
        for usage_item in usage:
            user_id = usage_item.get('user_id')
            feature = usage_item.get('feature')
            if user_id and feature:
                user_features[user_id].add(feature)
        
        # Calculate correlation between features
        correlations = {}
        features = set()
        for user_feature_set in user_features.values():
            features.update(user_feature_set)
        
        feature_list = list(features)
        for i, feature1 in enumerate(feature_list):
            for feature2 in feature_list[i+1:]:
                users_with_both = sum(1 for user_features in user_features.values() 
                                    if feature1 in user_features and feature2 in user_features)
                users_with_either = sum(1 for user_features in user_features.values() 
                                      if feature1 in user_features or feature2 in user_features)
                
                correlation = users_with_both / users_with_either if users_with_either > 0 else 0
                correlations[f"{feature1}-{feature2}"] = correlation
        
        return correlations
    
    def _convert_to_csv(self) -> str:
        """Convert analytics data to CSV format"""
        # Simplified CSV conversion
        csv_lines = []
        
        # User events
        csv_lines.append("Event Type,User ID,Timestamp,Session ID")
        for event in self.analytics_data['user_events']:
            csv_lines.append(f"{event['event_type']},{event.get('user_id', '')},{event['timestamp']},{event.get('session_id', '')}")
        
        return "\n".join(csv_lines)

# Global analytics manager instance
analytics_manager = AnalyticsManager()

def init_analytics_manager(app):
    """Initialize analytics manager with Flask app"""
    global analytics_manager
    analytics_manager = AnalyticsManager(app)
    return analytics_manager