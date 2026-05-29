"""
Unit tests for database models
"""
import pytest
from app.models import User, Todo
from app import db


class TestUserModel:
    """Tests for User model"""

    def test_create_user(self, client):
        """Test creating a new user"""
        user = User(username='newuser', email='new@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.password_hash is not None
        assert user.created_at is not None

    def test_password_hashing(self, client):
        """Test password hashing and verification"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('mypassword')

        # Password should be hashed
        assert user.password_hash != 'mypassword'

        # Correct password should verify
        assert user.check_password('mypassword') is True

        # Incorrect password should not verify
        assert user.check_password('wrongpassword') is False

    def test_unique_username(self, client, test_user):
        """Test username uniqueness constraint"""
        duplicate_user = User(username='testuser', email='different@example.com')
        duplicate_user.set_password('password')
        db.session.add(duplicate_user)

        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()

    def test_unique_email(self, client, test_user):
        """Test email uniqueness constraint"""
        duplicate_user = User(username='differentuser', email='test@example.com')
        duplicate_user.set_password('password')
        db.session.add(duplicate_user)

        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()

    def test_user_to_dict(self, client, test_user):
        """Test user serialization to dictionary"""
        user_dict = test_user.to_dict()

        assert user_dict['id'] == test_user.id
        assert user_dict['username'] == test_user.username
        assert user_dict['email'] == test_user.email
        assert 'password_hash' not in user_dict  # Should not expose password
        assert 'created_at' in user_dict


class TestTodoModel:
    """Tests for Todo model"""

    def test_create_todo(self, client, test_user):
        """Test creating a new todo"""
        todo = Todo(
            user_id=test_user.id,
            title='New Task',
            description='Task description',
            priority='medium',
            category='work'
        )
        db.session.add(todo)
        db.session.commit()

        assert todo.id is not None
        assert todo.user_id == test_user.id
        assert todo.title == 'New Task'
        assert todo.completed is False  # Default value
        assert todo.priority == 'medium'
        assert todo.category == 'work'
        assert todo.created_at is not None
        assert todo.updated_at is not None

    def test_todo_default_values(self, client, test_user):
        """Test todo default values"""
        todo = Todo(user_id=test_user.id, title='Simple Task')
        db.session.add(todo)
        db.session.commit()

        assert todo.completed is False
        assert todo.priority == 'medium'
        assert todo.description is None
        assert todo.category is None
        assert todo.due_date is None

    def test_todo_user_relationship(self, client, test_user):
        """Test todo-user relationship"""
        todo = Todo(user_id=test_user.id, title='Task')
        db.session.add(todo)
        db.session.commit()

        # Todo should have access to user
        assert todo.user.id == test_user.id
        assert todo.user.username == test_user.username

        # User should have access to todos
        assert len(test_user.todos) == 1
        assert test_user.todos[0].title == 'Task'

    def test_todo_cascade_delete(self, client, test_user):
        """Test cascade delete when user is deleted"""
        todo = Todo(user_id=test_user.id, title='Task')
        db.session.add(todo)
        db.session.commit()

        todo_id = todo.id

        # Delete user
        db.session.delete(test_user)
        db.session.commit()

        # Todo should also be deleted
        deleted_todo = Todo.query.get(todo_id)
        assert deleted_todo is None

    def test_todo_to_dict(self, client, test_todo):
        """Test todo serialization to dictionary"""
        todo_dict = test_todo.to_dict()

        assert todo_dict['id'] == test_todo.id
        assert todo_dict['user_id'] == test_todo.user_id
        assert todo_dict['title'] == test_todo.title
        assert todo_dict['description'] == test_todo.description
        assert todo_dict['completed'] == test_todo.completed
        assert todo_dict['priority'] == test_todo.priority
        assert todo_dict['category'] == test_todo.category
        assert 'created_at' in todo_dict
        assert 'updated_at' in todo_dict

    def test_todo_update(self, client, test_todo):
        """Test updating a todo"""
        original_updated_at = test_todo.updated_at

        # Update todo
        test_todo.completed = True
        test_todo.title = 'Updated Title'
        db.session.commit()

        # Refresh from database
        updated_todo = Todo.query.get(test_todo.id)
        assert updated_todo.completed is True
        assert updated_todo.title == 'Updated Title'
        # Note: SQLite doesn't auto-update updated_at, but PostgreSQL trigger will
