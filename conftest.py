"""
Конфигурация pytest и глобальные fixtures
"""

import pytest
from app import create_app, db
from app.models import User


@pytest.fixture(scope='function')
def app():
    """Создание приложения для тестов"""
    app = create_app(config_name='testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Клиент для тестирования"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Сессия БД для тестов"""
    with app.app_context():
        yield db
        db.session.rollback()


def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
