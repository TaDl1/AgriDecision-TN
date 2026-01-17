import pytest
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.base import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Use an in-memory SQLite database for testing
    app = create_app('testing')
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "BCRYPT_LOG_ROUNDS": 4 # Speed up tests
    })

    with app.app_context():
        # Enable Foreign Key support for SQLite
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            from sqlalchemy import event
            event.listen(db.engine, 'connect', lambda c, _: c.execute('PRAGMA foreign_keys=ON'))
            
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()