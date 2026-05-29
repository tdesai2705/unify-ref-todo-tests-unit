"""
Pytest configuration and fixtures for unit tests
"""
import pytest
import os
import sys

# Add backend app to Python path for imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import create_app, db
from app.models import User, Todo


@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application"""
    # Use in-memory SQLite for tests
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'

    return app


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the Flask app"""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope='function')
def test_user(client):
    """Create a test user"""
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def test_todo(client, test_user):
    """Create a test todo"""
    todo = Todo(
        user_id=test_user.id,
        title='Test Todo',
        description='Test Description',
        priority='high',
        category='work'
    )
    db.session.add(todo)
    db.session.commit()
    return todo


@pytest.fixture(scope='function')
def multiple_todos(client, test_user):
    """Create multiple test todos"""
    todos = [
        Todo(user_id=test_user.id, title='High Priority Task', priority='high', completed=False),
        Todo(user_id=test_user.id, title='Medium Priority Task', priority='medium', completed=False),
        Todo(user_id=test_user.id, title='Low Priority Task', priority='low', completed=True),
        Todo(user_id=test_user.id, title='Completed Task', priority='high', completed=True),
    ]
    for todo in todos:
        db.session.add(todo)
    db.session.commit()
    return todos
