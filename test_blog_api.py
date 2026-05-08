"""
Тесты для Blog API

Проверяют:
1. Регистрацию и вход пользователей
2. CRUD операции для постов
3. Работу комментариев
4. Авторизацию и права доступа
5. Валидацию входных данных
"""

import pytest
import json
from app import create_app, db
from app.models import User, Post, Category, Tag, Comment
from datetime import datetime


@pytest.fixture
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
def test_user(app):
    """Тестовый пользователь"""
    with app.app_context():
        user = User(username='testuser', full_name='Test User')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_category(app):
    """Тестовая категория"""
    with app.app_context():
        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()
        return category


@pytest.fixture
def test_tag(app):
    """Тестовый тег"""
    with app.app_context():
        tag = Tag(name='testtag')
        db.session.add(tag)
        db.session.commit()
        return tag


@pytest.fixture
def get_token(client):
    """Получить токен авторизации"""
    def _get_token(username='testuser', password='password123'):
        # Сначала создаем пользователя
        client.post('/api/auth/register', json={
            'username': username,
            'password': password,
            'full_name': 'Test User'
        })
        
        # Затем логинимся
        response = client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        return response.get_json()['access_token']
    
    return _get_token


# ======================== ТЕСТЫ АУТЕНТИФИКАЦИИ ========================

def test_health_check(client):
    """Проверка что API работает"""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Блог' in response.get_data(as_text=True)  # Проверяем что есть HTML с "Блог"


def test_user_registration_success(client):
    """Успешная регистрация пользователя"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'password': 'password123',
        'full_name': 'New User'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['user']['username'] == 'newuser'
    assert data['user']['full_name'] == 'New User'


def test_user_registration_invalid_username(client):
    """Регистрация с невалидным username"""
    response = client.post('/api/auth/register', json={
        'username': 'ab',  # Слишком короткий
        'password': 'password123'
    })
    
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_user_registration_invalid_password(client):
    """Регистрация с невалидным паролем"""
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': '123'  # Слишком короткий
    })
    
    assert response.status_code == 400


def test_user_registration_duplicate_username(client):
    """Попытка регистрации с существующим username"""
    # Первая регистрация
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Вторая попытка с тем же username
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    assert response.status_code == 409
    assert 'already exists' in response.get_json()['error']


def test_user_login_success(client):
    """Успешный вход пользователя"""
    # Регистрация
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Логин
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['user']['username'] == 'testuser'


def test_user_login_invalid_credentials(client):
    """Вход с неверными учетными данными"""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'Invalid credentials' in response.get_json()['error']


# ======================== ТЕСТЫ ПОСТОВ (CRUD) ========================

def test_create_post_authenticated(client, get_token):
    """Создание поста авторизованным пользователем"""
    token = get_token()
    
    response = client.post('/api/posts', json={
        'title': 'Test Post Title',
        'content': 'This is test post content with enough characters',
        'status': 'published'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['post']['title'] == 'Test Post Title'
    assert data['post']['status'] == 'published'


def test_create_post_unauthenticated(client):
    """Попытка создания поста без авторизации"""
    response = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': 'Test content with enough text'
    })
    
    assert response.status_code == 401


def test_create_post_invalid_data(client, get_token):
    """Создание поста с невалидными данными"""
    token = get_token()
    
    # Слишком короткое содержание
    response = client.post('/api/posts', json={
        'title': 'T',  # Слишком короткое название
        'content': 'short',  # Слишком короткое содержание
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 400


def test_get_all_posts(client, get_token):
    """Получение списка всех постов"""
    token = get_token()
    
    # Создаем несколько постов
    for i in range(3):
        client.post('/api/posts', json={
            'title': f'Post {i}',
            'content': f'Content for post {i} with enough characters'
        }, headers={'Authorization': f'Bearer {token}'})
    
    response = client.get('/api/posts')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['posts']) == 3
    assert data['total'] == 3


def test_get_post_by_id(client, get_token):
    """Получение поста по ID"""
    token = get_token()
    
    # Создаем пост
    create_response = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': 'Content for test post with enough characters'
    }, headers={'Authorization': f'Bearer {token}'})
    
    post_id = create_response.get_json()['post']['post_id']
    
    # Получаем пост
    response = client.get(f'/api/posts/{post_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Post'


def test_update_post_by_author(client, get_token):
    """Обновление поста автором"""
    token = get_token()
    
    # Создаем пост
    create_response = client.post('/api/posts', json={
        'title': 'Original Title',
        'content': 'Original content with enough characters'
    }, headers={'Authorization': f'Bearer {token}'})
    
    post_id = create_response.get_json()['post']['post_id']
    
    # Обновляем пост
    response = client.put(f'/api/posts/{post_id}', json={
        'title': 'Updated Title',
        'content': 'Updated content with enough characters'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['post']['title'] == 'Updated Title'


def test_update_post_unauthorized(client, get_token):
    """Попытка обновления поста другим пользователем"""
    token1 = get_token('user1', 'password123')
    token2 = get_token('user2', 'password123')
    
    # Создаем пост первым пользователем
    create_response = client.post('/api/posts', json={
        'title': 'User1 Post',
        'content': 'Content created by user1 with enough text'
    }, headers={'Authorization': f'Bearer {token1}'})
    
    post_id = create_response.get_json()['post']['post_id']
    
    # Пытаемся обновить вторым пользователем
    response = client.put(f'/api/posts/{post_id}', json={
        'title': 'Hacked Title'
    }, headers={'Authorization': f'Bearer {token2}'})
    
    assert response.status_code == 403


def test_delete_post_by_author(client, get_token):
    """Удаление поста автором"""
    token = get_token()
    
    # Создаем пост
    create_response = client.post('/api/posts', json={
        'title': 'To Delete',
        'content': 'This post will be deleted with enough content'
    }, headers={'Authorization': f'Bearer {token}'})
    
    post_id = create_response.get_json()['post']['post_id']
    
    # Удаляем пост
    response = client.delete(f'/api/posts/{post_id}', 
                           headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    
    # Проверяем что пост удален
    get_response = client.get(f'/api/posts/{post_id}')
    assert get_response.status_code == 404


def test_delete_post_unauthorized(client, get_token):
    """Попытка удаления поста другим пользователем"""
    token1 = get_token('user1', 'password123')
    token2 = get_token('user2', 'password123')
    
    # Создаем пост первым пользователем
    create_response = client.post('/api/posts', json={
        'title': 'User1 Post',
        'content': 'Cannot be deleted by user2 with enough text'
    }, headers={'Authorization': f'Bearer {token1}'})
    
    post_id = create_response.get_json()['post']['post_id']
    
    # Пытаемся удалить вторым пользователем
    response = client.delete(f'/api/posts/{post_id}',
                           headers={'Authorization': f'Bearer {token2}'})
    
    assert response.status_code == 403


# ======================== ТЕСТЫ КОММЕНТАРИЕВ ========================

def test_create_comment(client, get_token):
    """Создание комментария"""
    token = get_token()
    
    # Создаем пост
    post_response = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': 'Content for testing comments with enough text'
    }, headers={'Authorization': f'Bearer {token}'})
    
    post_id = post_response.get_json()['post']['post_id']
    
    # Добавляем комментарий
    response = client.post(f'/api/posts/{post_id}/comments', json={
        'text': 'This is a test comment'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['comment']['text'] == 'This is a test comment'


def test_get_post_comments(client, get_token):
    """Получение комментариев к посту"""
    token = get_token()
    
    # Создаем пост
    post_response = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': 'Content for testing comments with enough text'
    }, headers={'Authorization': f'Bearer {token}'})
    
    post_id = post_response.get_json()['post']['post_id']
    
    # Добавляем несколько комментариев
    for i in range(3):
        client.post(f'/api/posts/{post_id}/comments', json={
            'text': f'Comment {i}'
        }, headers={'Authorization': f'Bearer {token}'})
    
    # Получаем комментарии
    response = client.get(f'/api/posts/{post_id}/comments')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3


def test_delete_comment_by_author(client, get_token):
    """Удаление комментария автором"""
    token = get_token()
    
    # Создаем пост
    post_response = client.post('/api/posts', json={
        'title': 'Test Post',
        'content': 'Content for testing comment deletion'
    }, headers={'Authorization': f'Bearer {token}'})
    
    post_id = post_response.get_json()['post']['post_id']
    
    # Добавляем комментарий
    comment_response = client.post(f'/api/posts/{post_id}/comments', json={
        'text': 'This comment will be deleted'
    }, headers={'Authorization': f'Bearer {token}'})
    
    comment_id = comment_response.get_json()['comment']['id_comment']
    
    # Удаляем комментарий
    response = client.delete(f'/api/comments/{comment_id}',
                           headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200


# ======================== ТЕСТЫ КАТЕГОРИЙ И ТЕГОВ ========================

def test_get_categories(client):
    """Получение списка категорий"""
    response = client.get('/api/categories')
    assert response.status_code == 200


def test_create_category(client, get_token):
    """Создание категории"""
    token = get_token()
    
    response = client.post('/api/categories', json={
        'name': 'New Category'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['category']['name'] == 'New Category'


def test_get_tags(client):
    """Получение списка тегов"""
    response = client.get('/api/tags')
    assert response.status_code == 200


def test_create_tag(client, get_token):
    """Создание тега"""
    token = get_token()
    
    response = client.post('/api/tags', json={
        'name': 'newtag'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['tag']['name'] == 'newtag'


# ======================== ИТОГОВЫЕ ТЕСТЫ ========================

def test_full_blog_workflow(client, get_token):
    """Полный сценарий работы блога"""
    token = get_token('author', 'password123')
    
    # 1. Создаем категорию
    cat_response = client.post('/api/categories', json={
        'name': 'Tutorial'
    }, headers={'Authorization': f'Bearer {token}'})
    category_id = cat_response.get_json()['category']['id_category']
    
    # 2. Создаем теги
    tag_response = client.post('/api/tags', json={
        'name': 'python'
    }, headers={'Authorization': f'Bearer {token}'})
    tag_id = tag_response.get_json()['tag']['id_tag']
    
    # 3. Создаем пост
    post_response = client.post('/api/posts', json={
        'title': 'Python Tutorial',
        'content': 'Here is a comprehensive Python tutorial for beginners',
        'id_category': category_id,
        'id_tag': tag_id,
        'status': 'published'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert post_response.status_code == 201
    post_id = post_response.get_json()['post']['post_id']
    
    # 4. Добавляем комментарии
    comment_response = client.post(f'/api/posts/{post_id}/comments', json={
        'text': 'Great tutorial!'
    }, headers={'Authorization': f'Bearer {token}'})
    
    assert comment_response.status_code == 201
    
    # 5. Получаем пост со всеми деталями
    get_response = client.get(f'/api/posts/{post_id}')
    post_data = get_response.get_json()
    
    assert post_data['title'] == 'Python Tutorial'
    assert len(post_data['comments']) == 1
    assert post_data['comments'][0]['text'] == 'Great tutorial!'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
