"""
Real-time Communication Manager for Assertly
Handles WebSocket connections, real-time updates, and live collaboration
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask import request, session
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from cache_manager import cache_manager

class RealtimeManager:
    """Manages real-time communication for Assertly"""
    
    def __init__(self, app):
        """Initialize SocketIO with the Flask app"""
        self.socketio = SocketIO(
            app, 
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            async_mode='eventlet'
        )
        self.connected_users = {}
        self.room_users = {}
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            user_id = request.sid
            self.connected_users[user_id] = {
                'connected_at': datetime.now().isoformat(),
                'rooms': set()
            }
            
            logging.info(f"Client connected: {user_id}")
            emit('connected', {'status': 'success', 'user_id': user_id})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            user_id = request.sid
            if user_id in self.connected_users:
                # Leave all rooms
                for room in self.connected_users[user_id]['rooms']:
                    self._leave_room(user_id, room)
                
                del self.connected_users[user_id]
            
            logging.info(f"Client disconnected: {user_id}")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Handle joining a room"""
            room = data.get('room')
            user_id = request.sid
            
            if room:
                self._join_room(user_id, room)
                emit('room_joined', {'room': room, 'user_id': user_id})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle leaving a room"""
            room = data.get('room')
            user_id = request.sid
            
            if room:
                self._leave_room(user_id, room)
                emit('room_left', {'room': room, 'user_id': user_id})
        
        @self.socketio.on('test_execution_update')
        def handle_test_execution_update(data):
            """Handle test execution updates"""
            room = f"test_execution_{data.get('execution_id')}"
            self._broadcast_to_room(room, 'test_execution_updated', data)
        
        @self.socketio.on('test_case_edit')
        def handle_test_case_edit(data):
            """Handle test case editing"""
            room = f"test_case_{data.get('test_case_id')}"
            self._broadcast_to_room(room, 'test_case_edited', data)
        
        @self.socketio.on('user_typing')
        def handle_user_typing(data):
            """Handle user typing indicators"""
            room = data.get('room')
            if room:
                self._broadcast_to_room(room, 'user_typing', {
                    'user_id': request.sid,
                    'typing': data.get('typing', False),
                    'field': data.get('field', '')
                })
        
        @self.socketio.on('collaboration_cursor')
        def handle_collaboration_cursor(data):
            """Handle collaborative cursor movement"""
            room = data.get('room')
            if room:
                self._broadcast_to_room(room, 'cursor_moved', {
                    'user_id': request.sid,
                    'position': data.get('position'),
                    'selection': data.get('selection')
                })
        
        @self.socketio.on('notification')
        def handle_notification(data):
            """Handle notifications"""
            user_id = data.get('user_id')
            if user_id:
                self._send_to_user(user_id, 'notification', data)
        
        @self.socketio.on('system_status')
        def handle_system_status():
            """Handle system status requests"""
            status = self._get_system_status()
            emit('system_status', status)
    
    def _join_room(self, user_id: str, room: str):
        """Join a room"""
        join_room(room)
        
        if user_id in self.connected_users:
            self.connected_users[user_id]['rooms'].add(room)
        
        if room not in self.room_users:
            self.room_users[room] = set()
        self.room_users[room].add(user_id)
        
        # Notify others in the room
        self._broadcast_to_room(room, 'user_joined', {
            'user_id': user_id,
            'room': room,
            'user_count': len(self.room_users[room])
        })
    
    def _leave_room(self, user_id: str, room: str):
        """Leave a room"""
        leave_room(room)
        
        if user_id in self.connected_users:
            self.connected_users[user_id]['rooms'].discard(room)
        
        if room in self.room_users:
            self.room_users[room].discard(user_id)
            if not self.room_users[room]:
                del self.room_users[room]
        
        # Notify others in the room
        self._broadcast_to_room(room, 'user_left', {
            'user_id': user_id,
            'room': room,
            'user_count': len(self.room_users.get(room, set()))
        })
    
    def _broadcast_to_room(self, room: str, event: str, data: Dict[str, Any]):
        """Broadcast event to all users in a room"""
        self.socketio.emit(event, data, room=room)
        
        # Store in cache for offline users
        cache_manager.set_real_time_data(room, {
            'event': event,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
    
    def _send_to_user(self, user_id: str, event: str, data: Dict[str, Any]):
        """Send event to specific user"""
        self.socketio.emit(event, data, room=user_id)
    
    def broadcast_test_execution_update(self, execution_id: str, update_data: Dict[str, Any]):
        """Broadcast test execution update"""
        room = f"test_execution_{execution_id}"
        self._broadcast_to_room(room, 'test_execution_updated', update_data)
    
    def broadcast_test_case_update(self, test_case_id: str, update_data: Dict[str, Any]):
        """Broadcast test case update"""
        room = f"test_case_{test_case_id}"
        self._broadcast_to_room(room, 'test_case_updated', update_data)
    
    def broadcast_dashboard_update(self, update_data: Dict[str, Any]):
        """Broadcast dashboard update"""
        self._broadcast_to_room('dashboard', 'dashboard_updated', update_data)
    
    def broadcast_ai_generation_progress(self, user_id: str, progress_data: Dict[str, Any]):
        """Broadcast AI generation progress"""
        self._send_to_user(user_id, 'ai_generation_progress', progress_data)
    
    def broadcast_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send notification to user"""
        self._send_to_user(user_id, 'notification', notification)
    
    def broadcast_system_alert(self, alert_data: Dict[str, Any]):
        """Broadcast system alert to all users"""
        self.socketio.emit('system_alert', alert_data)
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'connected_users': len(self.connected_users),
            'active_rooms': len(self.room_users),
            'cache_stats': cache_manager.get_cache_stats(),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_connected_users(self) -> Dict[str, Any]:
        """Get connected users information"""
        return {
            'total_users': len(self.connected_users),
            'users': list(self.connected_users.keys()),
            'rooms': {room: list(users) for room, users in self.room_users.items()}
        }
    
    def get_room_users(self, room: str) -> List[str]:
        """Get users in a specific room"""
        return list(self.room_users.get(room, set()))
    
    def run(self, app, host='0.0.0.0', port=5000, debug=False):
        """Run the SocketIO server"""
        self.socketio.run(app, host=host, port=port, debug=debug)

# Global realtime manager instance
realtime_manager = None

def init_realtime_manager(app):
    """Initialize realtime manager"""
    global realtime_manager
    realtime_manager = RealtimeManager(app)
    return realtime_manager