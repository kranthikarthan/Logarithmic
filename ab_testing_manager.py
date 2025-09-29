"""
A/B Testing Framework for Assertly
Provides feature flagging, experimentation, and statistical analysis
"""

import json
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import logging
import math

class ABTestingManager:
    """A/B Testing framework for feature flagging and experimentation"""
    
    def __init__(self, app=None):
        """Initialize A/B testing manager"""
        self.app = app
        self.experiments = {}
        self.feature_flags = {}
        self.user_assignments = {}
        self.experiment_results = defaultdict(list)
        self.start_time = datetime.utcnow()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Add template globals for A/B testing
        app.jinja_env.globals['is_feature_enabled'] = self.is_feature_enabled
        app.jinja_env.globals['get_experiment_variant'] = self.get_experiment_variant
        app.jinja_env.globals['track_experiment_event'] = self.track_experiment_event
    
    def create_experiment(self, 
                         experiment_id: str, 
                         name: str, 
                         variants: List[Dict[str, Any]], 
                         traffic_allocation: float = 1.0,
                         start_date: datetime = None,
                         end_date: datetime = None,
                         target_audience: Dict[str, Any] = None) -> bool:
        """Create a new A/B test experiment"""
        try:
            if experiment_id in self.experiments:
                return False
            
            # Validate variants
            if not variants or len(variants) < 2:
                return False
            
            # Ensure traffic allocation is valid
            if not 0 < traffic_allocation <= 1:
                traffic_allocation = 1.0
            
            experiment = {
                'experiment_id': experiment_id,
                'name': name,
                'variants': variants,
                'traffic_allocation': traffic_allocation,
                'start_date': start_date or datetime.utcnow(),
                'end_date': end_date,
                'target_audience': target_audience or {},
                'status': 'active',
                'created_at': datetime.utcnow(),
                'metrics': {
                    'conversions': defaultdict(int),
                    'visitors': defaultdict(int),
                    'events': defaultdict(list)
                }
            }
            
            self.experiments[experiment_id] = experiment
            logging.info(f"Created experiment: {experiment_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create experiment: {e}")
            return False
    
    def create_feature_flag(self, 
                           flag_id: str, 
                           name: str, 
                           enabled: bool = False,
                           rollout_percentage: float = 0.0,
                           target_audience: Dict[str, Any] = None) -> bool:
        """Create a feature flag"""
        try:
            if flag_id in self.feature_flags:
                return False
            
            feature_flag = {
                'flag_id': flag_id,
                'name': name,
                'enabled': enabled,
                'rollout_percentage': rollout_percentage,
                'target_audience': target_audience or {},
                'created_at': datetime.utcnow(),
                'metrics': {
                    'enabled_count': 0,
                    'disabled_count': 0,
                    'events': []
                }
            }
            
            self.feature_flags[flag_id] = feature_flag
            logging.info(f"Created feature flag: {flag_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create feature flag: {e}")
            return False
    
    def is_feature_enabled(self, flag_id: str, user_id: str = None, context: Dict[str, Any] = None) -> bool:
        """Check if a feature flag is enabled for a user"""
        try:
            if flag_id not in self.feature_flags:
                return False
            
            flag = self.feature_flags[flag_id]
            
            # If globally disabled, return False
            if not flag['enabled']:
                return False
            
            # If no rollout percentage, return the global enabled state
            if flag['rollout_percentage'] == 0:
                return flag['enabled']
            
            # Check if user should be included in rollout
            if user_id:
                user_hash = self._get_user_hash(user_id, flag_id)
                user_percentage = user_hash % 100
                
                if user_percentage < (flag['rollout_percentage'] * 100):
                    # Track feature flag usage
                    self._track_feature_flag_usage(flag_id, user_id, True, context)
                    return True
                else:
                    self._track_feature_flag_usage(flag_id, user_id, False, context)
                    return False
            
            # If no user_id, use random assignment
            return random.random() < flag['rollout_percentage']
            
        except Exception as e:
            logging.error(f"Failed to check feature flag: {e}")
            return False
    
    def get_experiment_variant(self, experiment_id: str, user_id: str = None, context: Dict[str, Any] = None) -> Optional[str]:
        """Get experiment variant for a user"""
        try:
            if experiment_id not in self.experiments:
                return None
            
            experiment = self.experiments[experiment_id]
            
            # Check if experiment is active
            if experiment['status'] != 'active':
                return None
            
            # Check date range
            now = datetime.utcnow()
            if experiment['start_date'] and now < experiment['start_date']:
                return None
            if experiment['end_date'] and now > experiment['end_date']:
                return None
            
            # Check traffic allocation
            if user_id:
                user_hash = self._get_user_hash(user_id, experiment_id)
                if user_hash % 100 >= (experiment['traffic_allocation'] * 100):
                    return None
            
            # Check target audience
            if not self._matches_target_audience(experiment['target_audience'], user_id, context):
                return None
            
            # Assign variant
            if user_id in self.user_assignments.get(experiment_id, {}):
                variant = self.user_assignments[experiment_id][user_id]
            else:
                variant = self._assign_variant(experiment)
                if experiment_id not in self.user_assignments:
                    self.user_assignments[experiment_id] = {}
                self.user_assignments[experiment_id][user_id] = variant
            
            # Track experiment assignment
            self._track_experiment_assignment(experiment_id, user_id, variant, context)
            
            return variant
            
        except Exception as e:
            logging.error(f"Failed to get experiment variant: {e}")
            return None
    
    def track_experiment_event(self, experiment_id: str, event_type: str, user_id: str = None, 
                              value: float = None, metadata: Dict[str, Any] = None) -> bool:
        """Track an event for an experiment"""
        try:
            if experiment_id not in self.experiments:
                return False
            
            experiment = self.experiments[experiment_id]
            
            # Get user's variant
            variant = self.user_assignments.get(experiment_id, {}).get(user_id)
            if not variant:
                return False
            
            # Track the event
            event = {
                'event_type': event_type,
                'user_id': user_id,
                'variant': variant,
                'value': value,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow()
            }
            
            experiment['metrics']['events'][variant].append(event)
            
            # Update conversion count if it's a conversion event
            if event_type == 'conversion':
                experiment['metrics']['conversions'][variant] += 1
            
            # Update visitor count
            if event_type == 'page_view':
                experiment['metrics']['visitors'][variant] += 1
            
            logging.info(f"Tracked experiment event: {experiment_id} - {event_type}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to track experiment event: {e}")
            return False
    
    def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment results and statistical analysis"""
        try:
            if experiment_id not in self.experiments:
                return {}
            
            experiment = self.experiments[experiment_id]
            metrics = experiment['metrics']
            
            results = {
                'experiment_id': experiment_id,
                'name': experiment['name'],
                'status': experiment['status'],
                'variants': {},
                'statistical_significance': {},
                'recommendation': None
            }
            
            # Calculate metrics for each variant
            for variant in experiment['variants']:
                variant_id = variant['id']
                visitors = metrics['visitors'][variant_id]
                conversions = metrics['conversions'][variant_id]
                
                conversion_rate = (conversions / visitors * 100) if visitors > 0 else 0
                
                results['variants'][variant_id] = {
                    'name': variant['name'],
                    'visitors': visitors,
                    'conversions': conversions,
                    'conversion_rate': round(conversion_rate, 2),
                    'events': len(metrics['events'][variant_id])
                }
            
            # Calculate statistical significance
            results['statistical_significance'] = self._calculate_statistical_significance(experiment)
            
            # Generate recommendation
            results['recommendation'] = self._generate_recommendation(results)
            
            return results
            
        except Exception as e:
            logging.error(f"Failed to get experiment results: {e}")
            return {}
    
    def stop_experiment(self, experiment_id: str) -> bool:
        """Stop an experiment"""
        try:
            if experiment_id not in self.experiments:
                return False
            
            self.experiments[experiment_id]['status'] = 'stopped'
            logging.info(f"Stopped experiment: {experiment_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to stop experiment: {e}")
            return False
    
    def get_feature_flag_metrics(self, flag_id: str) -> Dict[str, Any]:
        """Get feature flag metrics"""
        try:
            if flag_id not in self.feature_flags:
                return {}
            
            flag = self.feature_flags[flag_id]
            metrics = flag['metrics']
            
            total_events = metrics['enabled_count'] + metrics['disabled_count']
            enabled_percentage = (metrics['enabled_count'] / total_events * 100) if total_events > 0 else 0
            
            return {
                'flag_id': flag_id,
                'name': flag['name'],
                'enabled': flag['enabled'],
                'rollout_percentage': flag['rollout_percentage'],
                'total_events': total_events,
                'enabled_count': metrics['enabled_count'],
                'disabled_count': metrics['disabled_count'],
                'enabled_percentage': round(enabled_percentage, 2),
                'recent_events': metrics['events'][-10:]  # Last 10 events
            }
            
        except Exception as e:
            logging.error(f"Failed to get feature flag metrics: {e}")
            return {}
    
    def _get_user_hash(self, user_id: str, salt: str) -> int:
        """Get consistent hash for user"""
        hash_input = f"{user_id}:{salt}"
        return int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    
    def _assign_variant(self, experiment: Dict[str, Any]) -> str:
        """Assign a variant to a user"""
        variants = experiment['variants']
        
        # Simple random assignment
        # In a real implementation, you might want more sophisticated assignment
        return random.choice([variant['id'] for variant in variants])
    
    def _matches_target_audience(self, target_audience: Dict[str, Any], user_id: str, context: Dict[str, Any]) -> bool:
        """Check if user matches target audience"""
        if not target_audience:
            return True
        
        # Simplified audience matching
        # In a real implementation, you'd have more sophisticated audience targeting
        return True
    
    def _track_feature_flag_usage(self, flag_id: str, user_id: str, enabled: bool, context: Dict[str, Any]):
        """Track feature flag usage"""
        try:
            flag = self.feature_flags[flag_id]
            
            if enabled:
                flag['metrics']['enabled_count'] += 1
            else:
                flag['metrics']['disabled_count'] += 1
            
            # Track event
            event = {
                'user_id': user_id,
                'enabled': enabled,
                'context': context or {},
                'timestamp': datetime.utcnow()
            }
            
            flag['metrics']['events'].append(event)
            
        except Exception as e:
            logging.error(f"Failed to track feature flag usage: {e}")
    
    def _track_experiment_assignment(self, experiment_id: str, user_id: str, variant: str, context: Dict[str, Any]):
        """Track experiment assignment"""
        try:
            experiment = self.experiments[experiment_id]
            
            # Track assignment event
            event = {
                'event_type': 'assignment',
                'user_id': user_id,
                'variant': variant,
                'context': context or {},
                'timestamp': datetime.utcnow()
            }
            
            experiment['metrics']['events'][variant].append(event)
            
        except Exception as e:
            logging.error(f"Failed to track experiment assignment: {e}")
    
    def _calculate_statistical_significance(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical significance between variants"""
        try:
            metrics = experiment['metrics']
            variants = list(metrics['conversions'].keys())
            
            if len(variants) < 2:
                return {'significant': False, 'confidence': 0}
            
            # Get conversion rates for each variant
            conversion_rates = {}
            for variant in variants:
                visitors = metrics['visitors'][variant]
                conversions = metrics['conversions'][variant]
                conversion_rates[variant] = conversions / visitors if visitors > 0 else 0
            
            # Simplified statistical significance calculation
            # In a real implementation, you'd use proper statistical tests
            max_rate = max(conversion_rates.values())
            min_rate = min(conversion_rates.values())
            
            # Calculate confidence based on sample size and difference
            total_visitors = sum(metrics['visitors'].values())
            rate_difference = max_rate - min_rate
            
            # Simplified confidence calculation
            confidence = min(95, (rate_difference * 100) + (total_visitors / 1000))
            
            return {
                'significant': confidence > 80,
                'confidence': round(confidence, 2),
                'conversion_rates': conversion_rates,
                'total_visitors': total_visitors
            }
            
        except Exception as e:
            logging.error(f"Failed to calculate statistical significance: {e}")
            return {'significant': False, 'confidence': 0}
    
    def _generate_recommendation(self, results: Dict[str, Any]) -> str:
        """Generate recommendation based on results"""
        try:
            variants = results['variants']
            if len(variants) < 2:
                return "Not enough data for recommendation"
            
            # Find best performing variant
            best_variant = max(variants.items(), key=lambda x: x[1]['conversion_rate'])
            worst_variant = min(variants.items(), key=lambda x: x[1]['conversion_rate'])
            
            best_rate = best_variant[1]['conversion_rate']
            worst_rate = worst_variant[1]['conversion_rate']
            
            improvement = ((best_rate - worst_rate) / worst_rate * 100) if worst_rate > 0 else 0
            
            if results['statistical_significance']['significant']:
                if improvement > 10:
                    return f"Implement {best_variant[0]} - shows {improvement:.1f}% improvement"
                else:
                    return "Results are significant but improvement is minimal"
            else:
                return "Results are not statistically significant - continue testing"
                
        except Exception as e:
            logging.error(f"Failed to generate recommendation: {e}")
            return "Unable to generate recommendation"
    
    def export_experiment_data(self, experiment_id: str) -> Dict[str, Any]:
        """Export experiment data"""
        try:
            if experiment_id not in self.experiments:
                return {}
            
            experiment = self.experiments[experiment_id]
            results = self.get_experiment_results(experiment_id)
            
            return {
                'experiment': experiment,
                'results': results,
                'exported_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Failed to export experiment data: {e}")
            return {}
    
    def get_all_experiments(self) -> Dict[str, Any]:
        """Get all experiments"""
        return {
            'experiments': list(self.experiments.keys()),
            'feature_flags': list(self.feature_flags.keys()),
            'total_experiments': len(self.experiments),
            'total_feature_flags': len(self.feature_flags)
        }

# Global A/B testing manager instance
ab_testing_manager = ABTestingManager()

def init_ab_testing_manager(app):
    """Initialize A/B testing manager with Flask app"""
    global ab_testing_manager
    ab_testing_manager = ABTestingManager(app)
    return ab_testing_manager