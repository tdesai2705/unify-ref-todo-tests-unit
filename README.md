# Unit Tests (pytest)

Comprehensive unit test suite for the backend REST API using pytest.

## Test Coverage

### Models (`test_models.py`)
- **User Model**: 5 tests
  - Create user
  - Password hashing and verification
  - Username uniqueness
  - Email uniqueness
  - Serialization (to_dict)

- **Todo Model**: 7 tests
  - Create todo
  - Default values
  - User relationship
  - Cascade delete
  - Serialization
  - Update operations

### Routes (`test_routes.py`)
- **Todo Endpoints**: 17 tests
  - Get todos (empty, with data)
  - Filter by completion status
  - Filter by priority
  - Get single todo
  - Create todo (valid, invalid)
  - Update todo
  - Delete todo
  - Statistics endpoint

- **Auth Endpoints**: 9 tests
  - User registration (success, duplicates, missing fields)
  - Login (success, invalid credentials, missing fields)

- **Health Check**: 1 test
  - Health endpoint

**Total: 39 unit tests**

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
# Basic run
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Run specific test file
pytest tests/test_routes.py

# Run specific test class
pytest tests/test_routes.py::TestTodoRoutes

# Run specific test function
pytest tests/test_routes.py::TestTodoRoutes::test_create_todo
```

### View Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html
```

## Test Structure

```
tests-unit/
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # Model tests (12 tests)
│   └── test_routes.py        # API endpoint tests (27 tests)
├── conftest.py               # Pytest fixtures
├── pytest.ini                # Pytest configuration
├── .coveragerc               # Coverage configuration
├── requirements.txt          # Test dependencies
└── README.md                 # This file
```

## Fixtures

### `app`
Flask application configured for testing with in-memory SQLite database.

### `client`
Test client for making HTTP requests. Automatically creates/drops database tables.

### `test_user`
Pre-created test user with:
- username: `testuser`
- email: `test@example.com`
- password: `testpass123`

### `test_todo`
Pre-created test todo belonging to `test_user`.

### `multiple_todos`
4 pre-created todos with different priorities and completion states.

## Test Categories

### Model Tests
Test database models, relationships, and ORM functionality.

```python
def test_create_user(client):
    user = User(username='newuser', email='new@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    assert user.id is not None
```

### API Endpoint Tests
Test REST API endpoints, request/response handling, validation.

```python
def test_create_todo(client, test_user):
    response = client.post('/api/todos',
                          json={'user_id': test_user.id, 'title': 'Task'})
    assert response.status_code == 201
    assert response.json['title'] == 'Task'
```

## Running with Smart Tests

When integrated with CloudBees Unify Smart Tests:

```yaml
# .cloudbees/workflows/build.yaml
- uses: cloudbees-io/smart-tests@v1
  with:
    test-command: pytest tests/
    mode: subsetting
```

**Benefits:**
- Only runs tests affected by code changes
- 50-80% faster CI/CD pipeline
- AI-powered test selection

## Code Coverage Goals

- **Overall**: 80%+ coverage
- **Models**: 90%+ coverage
- **Routes**: 85%+ coverage
- **Critical paths**: 100% coverage (authentication, CRUD operations)

## CI/CD Integration

### CloudBees Unify Workflow

```yaml
jobs:
  test:
    steps:
      - uses: cloudbees-io/checkout@v1
      - uses: cloudbees-io/docker-run@v1
        with:
          image: python:3.11
          run: |
            pip install -r requirements.txt
            pytest --cov=app --cov-report=xml
      - uses: cloudbees-io/publish-test-results@v1
        with:
          test-results: pytest-results.xml
          coverage-report: coverage.xml
```

## Best Practices

1. **Test Isolation**: Each test uses fresh database (via fixtures)
2. **Descriptive Names**: Test names clearly describe what they test
3. **AAA Pattern**: Arrange, Act, Assert structure
4. **Test One Thing**: Each test focuses on a single behavior
5. **Use Fixtures**: Reuse common setup via pytest fixtures
6. **Mock External Calls**: Don't make real HTTP requests or database calls to external services

## Troubleshooting

### Import Errors
```bash
# Ensure backend app is in Python path
export PYTHONPATH="${PYTHONPATH}:../backend"
```

### Database Errors
```bash
# Tests use in-memory SQLite, not PostgreSQL
# If you see PostgreSQL errors, check conftest.py configuration
```

### Coverage Not Showing
```bash
# Make sure you're in the tests-unit directory
cd tests-unit/
pytest --cov=app --cov-report=term-missing
```

## CloudBees Unify Integration

This test suite integrates with:
- ✅ Smart Tests (intelligent test subsetting)
- ✅ CI/CD workflows (automated test execution)
- ✅ Test result publishing (Unify dashboard)
- ✅ Coverage reporting (trend analysis)

Part of CloudBees Unify Reference Architecture project.

**Team**: Tejas Desai (2-tier), Dinesh Narlakanti (3-tier), Anudeep Nalla (Infrastructure)
**Lead**: Xhesi Galanxhi
