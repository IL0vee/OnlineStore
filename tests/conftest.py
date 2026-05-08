# tests/conftest.py
import pytest
import sys
import os
from dotenv import load_dotenv

# Добавляем корневую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Product, Category, CartItem, Order, OrderItem

# Загружаем переменные окружения
load_dotenv()


@pytest.fixture
def app():
    """Создание тестового приложения"""
    app = create_app()
    
    # Настройки для тестов
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # База в памяти
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain',
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Создаем контекст приложения
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
    """CLI runner для тестов"""
    return app.test_cli_runner()


@pytest.fixture
def get_token(client):
    """Фикстура для получения JWT/Flask-Login токена"""
    def _get_token(username='testuser', password='testpass123'):
        # Сначала регистрируем пользователя
        response = client.post('/register', data={
            'username': username,
            'email': f'{username}@example.com',
            'full_name': 'Test User',
            'password': password,
            'confirm_password': password
        })
        
        # Входим в систему
        response = client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
        
        # Получаем session cookie
        if response.status_code == 200:
            return True  # Авторизация успешна
        return False
    
    return _get_token


@pytest.fixture
def create_test_user(app):
    """Создание тестового пользователя"""
    def _create_user(username='testuser', email='test@example.com', password='testpass123', is_admin=False):
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(
                    username=username,
                    email=email,
                    full_name='Test User',
                    is_admin=is_admin
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
            return user
    return _create_user


@pytest.fixture
def create_test_product(app):
    """Создание тестового товара"""
    def _create_product(name='Test Product', price=1000, stock=10, is_active=True):
        with app.app_context():
            product = Product(
                name=name,
                description='This is a test product description with enough length',
                price=price,
                stock=stock,
                is_active=is_active,
                is_featured=False,
                sku=f'SKU-{name.replace(" ", "")}'
            )
            db.session.add(product)
            db.session.commit()
            return product
    return _create_product


@pytest.fixture
def create_test_category(app):
    """Создание тестовой категории"""
    def _create_category(name='Test Category', slug='test-category'):
        with app.app_context():
            category = Category(
                name=name,
                description='Test category description',
                slug=slug
            )
            db.session.add(category)
            db.session.commit()
            return category
    return _create_category


@pytest.fixture
def login_admin(client):
    """Вход как администратор"""
    def _login():
        # Создаем админа если нет
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@test.com',
                full_name='Admin User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        # Входим
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        return True
    return _login