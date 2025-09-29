#!/usr/bin/env python3
"""
Test Service - Microservice for test management
Handles test cases, test executions, and test-related operations
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_DB_URL', 'sqlite:///test_service.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class TestCase(db.Model):
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    test_type = db.Column(db.String(50), default='manual')
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='draft')
    created_by = db.Column(db.Integer, nullable=False)
    assigned_to = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = db.Column(db.JSON)
    steps = db.Column(db.JSON)
    expected_result = db.Column(db.Text)
    preconditions = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'test_type': self.test_type,
            'priority': self.priority,
            'status': self.status,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags,
            'steps': self.steps,
            'expected_result': self.expected_result,
            'preconditions': self.preconditions
        }

class TestExecution(db.Model):
    __tablename__ = 'test_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('test_cases.id'), nullable=False)
    executed_by = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='not_executed')
    result = db.Column(db.String(20))
    executed_at = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in seconds
    notes = db.Column(db.Text)
    defects = db.Column(db.JSON)
    screenshots = db.Column(db.JSON)
    environment = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_case_id': self.test_case_id,
            'executed_by': self.executed_by,
            'status': self.status,
            'result': self.result,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'duration': self.duration,
            'notes': self.notes,
            'defects': self.defects,
            'screenshots': self.screenshots,
            'environment': self.environment
        }

class TestSet(db.Model):
    __tablename__ = 'test_sets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    test_cases = db.Column(db.JSON)  # List of test case IDs
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'test_cases': self.test_cases
        }

# Authentication decorator (simplified for microservice)
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real microservice, this would validate JWT with user service
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 401
        request.current_user_id = int(user_id)
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'service': 'test-service',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/test-cases', methods=['POST'])
@require_auth
def create_test_case():
    """Create a new test case"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        test_case = TestCase(
            title=data['title'],
            description=data.get('description'),
            test_type=data.get('test_type', 'manual'),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'draft'),
            created_by=request.current_user_id,
            assigned_to=data.get('assigned_to'),
            tags=data.get('tags', []),
            steps=data.get('steps', []),
            expected_result=data.get('expected_result'),
            preconditions=data.get('preconditions')
        )
        
        db.session.add(test_case)
        db.session.commit()
        
        return jsonify({
            'message': 'Test case created successfully',
            'test_case': test_case.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/test-cases', methods=['GET'])
@require_auth
def list_test_cases():
    """List test cases"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        test_type = request.args.get('test_type')
        
        query = TestCase.query
        
        if status:
            query = query.filter_by(status=status)
        if test_type:
            query = query.filter_by(test_type=test_type)
        
        test_cases = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'test_cases': [tc.to_dict() for tc in test_cases.items],
            'total': test_cases.total,
            'page': page,
            'per_page': per_page,
            'pages': test_cases.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-cases/<int:test_case_id>', methods=['GET'])
@require_auth
def get_test_case(test_case_id):
    """Get test case by ID"""
    try:
        test_case = TestCase.query.get(test_case_id)
        if not test_case:
            return jsonify({'error': 'Test case not found'}), 404
        
        return jsonify({'test_case': test_case.to_dict()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-cases/<int:test_case_id>', methods=['PUT'])
@require_auth
def update_test_case(test_case_id):
    """Update test case"""
    try:
        test_case = TestCase.query.get(test_case_id)
        if not test_case:
            return jsonify({'error': 'Test case not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            test_case.title = data['title']
        if 'description' in data:
            test_case.description = data['description']
        if 'test_type' in data:
            test_case.test_type = data['test_type']
        if 'priority' in data:
            test_case.priority = data['priority']
        if 'status' in data:
            test_case.status = data['status']
        if 'assigned_to' in data:
            test_case.assigned_to = data['assigned_to']
        if 'tags' in data:
            test_case.tags = data['tags']
        if 'steps' in data:
            test_case.steps = data['steps']
        if 'expected_result' in data:
            test_case.expected_result = data['expected_result']
        if 'preconditions' in data:
            test_case.preconditions = data['preconditions']
        
        test_case.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Test case updated successfully',
            'test_case': test_case.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/test-executions', methods=['POST'])
@require_auth
def create_test_execution():
    """Create test execution"""
    try:
        data = request.get_json()
        
        if not data.get('test_case_id'):
            return jsonify({'error': 'Test case ID is required'}), 400
        
        execution = TestExecution(
            test_case_id=data['test_case_id'],
            executed_by=request.current_user_id,
            status=data.get('status', 'not_executed'),
            result=data.get('result'),
            environment=data.get('environment'),
            notes=data.get('notes')
        )
        
        db.session.add(execution)
        db.session.commit()
        
        return jsonify({
            'message': 'Test execution created successfully',
            'execution': execution.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/test-executions/<int:execution_id>', methods=['PUT'])
@require_auth
def update_test_execution(execution_id):
    """Update test execution"""
    try:
        execution = TestExecution.query.get(execution_id)
        if not execution:
            return jsonify({'error': 'Test execution not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'status' in data:
            execution.status = data['status']
        if 'result' in data:
            execution.result = data['result']
        if 'notes' in data:
            execution.notes = data['notes']
        if 'defects' in data:
            execution.defects = data['defects']
        if 'screenshots' in data:
            execution.screenshots = data['screenshots']
        
        if execution.status == 'executed':
            execution.executed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Test execution updated successfully',
            'execution': execution.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/test-sets', methods=['POST'])
@require_auth
def create_test_set():
    """Create test set"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        test_set = TestSet(
            name=data['name'],
            description=data.get('description'),
            created_by=request.current_user_id,
            test_cases=data.get('test_cases', [])
        )
        
        db.session.add(test_set)
        db.session.commit()
        
        return jsonify({
            'message': 'Test set created successfully',
            'test_set': test_set.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/test-sets', methods=['GET'])
@require_auth
def list_test_sets():
    """List test sets"""
    try:
        test_sets = TestSet.query.all()
        return jsonify({
            'test_sets': [ts.to_dict() for ts in test_sets]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/coverage', methods=['GET'])
@require_auth
def get_coverage_analytics():
    """Get test coverage analytics"""
    try:
        total_cases = TestCase.query.count()
        executed_cases = TestExecution.query.filter_by(status='executed').count()
        passed_cases = TestExecution.query.filter_by(result='passed').count()
        failed_cases = TestExecution.query.filter_by(result='failed').count()
        
        coverage_percentage = (executed_cases / total_cases * 100) if total_cases > 0 else 0
        pass_rate = (passed_cases / executed_cases * 100) if executed_cases > 0 else 0
        
        return jsonify({
            'total_test_cases': total_cases,
            'executed_cases': executed_cases,
            'passed_cases': passed_cases,
            'failed_cases': failed_cases,
            'coverage_percentage': round(coverage_percentage, 2),
            'pass_rate': round(pass_rate, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5002, debug=True)