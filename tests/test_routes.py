"""
Unit tests for API routes
"""
import pytest
import json
from datetime import datetime, timedelta


class TestTodoRoutes:
    """Tests for Todo API endpoints"""

    def test_get_todos_empty(self, client, test_user):
        """Test getting todos when none exist"""
        response = client.get(f'/api/todos?user_id={test_user.id}')
        assert response.status_code == 200
        assert response.json == []

    def test_get_todos_with_data(self, client, multiple_todos):
        """Test getting all todos for a user"""
        user_id = multiple_todos[0].user_id
        response = client.get(f'/api/todos?user_id={user_id}')

        assert response.status_code == 200
        data = response.json
        assert len(data) == 4

    def test_get_todos_filter_by_completed(self, client, multiple_todos):
        """Test filtering todos by completion status"""
        user_id = multiple_todos[0].user_id

        # Get completed todos
        response = client.get(f'/api/todos?user_id={user_id}&completed=true')
        assert response.status_code == 200
        completed_todos = response.json
        assert len(completed_todos) == 2
        assert all(todo['completed'] for todo in completed_todos)

        # Get pending todos
        response = client.get(f'/api/todos?user_id={user_id}&completed=false')
        assert response.status_code == 200
        pending_todos = response.json
        assert len(pending_todos) == 2
        assert all(not todo['completed'] for todo in pending_todos)

    def test_get_todos_filter_by_priority(self, client, multiple_todos):
        """Test filtering todos by priority"""
        user_id = multiple_todos[0].user_id

        response = client.get(f'/api/todos?user_id={user_id}&priority=high')
        assert response.status_code == 200
        high_priority = response.json
        assert len(high_priority) == 2
        assert all(todo['priority'] == 'high' for todo in high_priority)

    def test_get_single_todo(self, client, test_todo):
        """Test getting a single todo by ID"""
        response = client.get(f'/api/todos/{test_todo.id}')

        assert response.status_code == 200
        data = response.json
        assert data['id'] == test_todo.id
        assert data['title'] == test_todo.title

    def test_get_single_todo_not_found(self, client):
        """Test getting a non-existent todo"""
        response = client.get('/api/todos/99999')
        assert response.status_code == 404

    def test_create_todo(self, client, test_user):
        """Test creating a new todo"""
        todo_data = {
            'user_id': test_user.id,
            'title': 'New Task',
            'description': 'Task description',
            'priority': 'high',
            'category': 'work'
        }

        response = client.post('/api/todos',
                              data=json.dumps(todo_data),
                              content_type='application/json')

        assert response.status_code == 201
        data = response.json
        assert data['title'] == 'New Task'
        assert data['priority'] == 'high'
        assert data['completed'] is False

    def test_create_todo_missing_title(self, client, test_user):
        """Test creating todo without required title"""
        todo_data = {
            'user_id': test_user.id,
            'priority': 'high'
        }

        response = client.post('/api/todos',
                              data=json.dumps(todo_data),
                              content_type='application/json')

        assert response.status_code == 400
        assert 'error' in response.json

    def test_create_todo_missing_user_id(self, client):
        """Test creating todo without user_id"""
        todo_data = {
            'title': 'Task without user'
        }

        response = client.post('/api/todos',
                              data=json.dumps(todo_data),
                              content_type='application/json')

        assert response.status_code == 400
        assert 'error' in response.json

    def test_create_todo_invalid_user(self, client):
        """Test creating todo with non-existent user"""
        todo_data = {
            'user_id': 99999,
            'title': 'Task'
        }

        response = client.post('/api/todos',
                              data=json.dumps(todo_data),
                              content_type='application/json')

        assert response.status_code == 404
        assert 'error' in response.json

    def test_create_todo_with_due_date(self, client, test_user):
        """Test creating todo with due date"""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        todo_data = {
            'user_id': test_user.id,
            'title': 'Task with deadline',
            'due_date': due_date
        }

        response = client.post('/api/todos',
                              data=json.dumps(todo_data),
                              content_type='application/json')

        assert response.status_code == 201
        data = response.json
        assert data['due_date'] is not None

    def test_update_todo(self, client, test_todo):
        """Test updating an existing todo"""
        update_data = {
            'title': 'Updated Title',
            'completed': True,
            'priority': 'low'
        }

        response = client.put(f'/api/todos/{test_todo.id}',
                             data=json.dumps(update_data),
                             content_type='application/json')

        assert response.status_code == 200
        data = response.json
        assert data['title'] == 'Updated Title'
        assert data['completed'] is True
        assert data['priority'] == 'low'

    def test_update_todo_not_found(self, client):
        """Test updating a non-existent todo"""
        update_data = {'title': 'Updated'}

        response = client.put('/api/todos/99999',
                             data=json.dumps(update_data),
                             content_type='application/json')

        assert response.status_code == 404

    def test_delete_todo(self, client, test_todo):
        """Test deleting a todo"""
        todo_id = test_todo.id

        response = client.delete(f'/api/todos/{todo_id}')
        assert response.status_code == 204

        # Verify todo is deleted
        get_response = client.get(f'/api/todos/{todo_id}')
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client):
        """Test deleting a non-existent todo"""
        response = client.delete('/api/todos/99999')
        assert response.status_code == 404

    def test_get_stats_empty(self, client, test_user):
        """Test getting stats when no todos exist"""
        response = client.get(f'/api/todos/stats?user_id={test_user.id}')

        assert response.status_code == 200
        data = response.json
        assert data['total'] == 0
        assert data['completed'] == 0
        assert data['pending'] == 0
        assert data['completion_rate'] == 0

    def test_get_stats_with_data(self, client, multiple_todos):
        """Test getting statistics with data"""
        user_id = multiple_todos[0].user_id
        response = client.get(f'/api/todos/stats?user_id={user_id}')

        assert response.status_code == 200
        data = response.json
        assert data['total'] == 4
        assert data['completed'] == 2
        assert data['pending'] == 2
        assert data['completion_rate'] == 50.0
        assert data['by_priority']['high'] == 2
        assert data['by_priority']['medium'] == 1
        assert data['by_priority']['low'] == 1


class TestAuthRoutes:
    """Tests for authentication endpoints"""

    def test_register_user(self, client):
        """Test user registration"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }

        response = client.post('/api/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')

        assert response.status_code == 201
        data = response.json
        assert data['username'] == 'newuser'
        assert data['email'] == 'newuser@example.com'
        assert 'password' not in data
        assert 'password_hash' not in data

    def test_register_duplicate_username(self, client, test_user):
        """Test registering with duplicate username"""
        user_data = {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123'
        }

        response = client.post('/api/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')

        assert response.status_code == 409
        assert 'error' in response.json

    def test_register_duplicate_email(self, client, test_user):
        """Test registering with duplicate email"""
        user_data = {
            'username': 'differentuser',
            'email': 'test@example.com',
            'password': 'password123'
        }

        response = client.post('/api/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')

        assert response.status_code == 409
        assert 'error' in response.json

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        user_data = {'username': 'newuser'}

        response = client.post('/api/auth/register',
                              data=json.dumps(user_data),
                              content_type='application/json')

        assert response.status_code == 400
        assert 'error' in response.json

    def test_login_success(self, client, test_user):
        """Test successful login"""
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = client.post('/api/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')

        assert response.status_code == 200
        data = response.json
        assert 'message' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'

    def test_login_invalid_username(self, client, test_user):
        """Test login with invalid username"""
        login_data = {
            'username': 'nonexistent',
            'password': 'password123'
        }

        response = client.post('/api/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')

        assert response.status_code == 401
        assert 'error' in response.json

    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password"""
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = client.post('/api/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')

        assert response.status_code == 401
        assert 'error' in response.json

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        login_data = {'username': 'testuser'}

        response = client.post('/api/auth/login',
                              data=json.dumps(login_data),
                              content_type='application/json')

        assert response.status_code == 400
        assert 'error' in response.json


class TestHealthCheck:
    """Tests for health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')

        assert response.status_code == 200
        data = response.json
        assert data['status'] == 'healthy'
        assert data['service'] == 'todo-backend'
