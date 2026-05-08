# tests/test_auth.py
import pytest


class TestAuth:
    """Тесты авторизации и регистрации"""
    
    def test_register_success(self, client):
        """Успешная регистрация пользователя"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Регистрация прошла успешно' in response.data
    
    def test_register_duplicate_username(self, client, create_test_user):
        """Регистрация с уже существующим username"""
        create_test_user(username='existing')
        
        response = client.post('/register', data={
            'username': 'existing',
            'email': 'new@example.com',
            'full_name': 'New User',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        assert b'Пользователь с таким именем уже существует' in response.data
    
    def test_register_password_mismatch(self, client):
        """Регистрация с несовпадающими паролями"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': 'password123',
            'confirm_password': 'different'
        }, follow_redirects=True)
        
        assert b'Пароли не совпадают' in response.data
    
    def test_login_success(self, client, create_test_user):
        """Успешный вход в систему"""
        create_test_user(username='loginuser', password='testpass123')
        
        response = client.post('/login', data={
            'username': 'loginuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Вы успешно вошли в систему' in response.data
    
    def test_login_wrong_password(self, client, create_test_user):
        """Вход с неверным паролем"""
        create_test_user(username='wrongpass', password='correct123')
        
        response = client.post('/login', data={
            'username': 'wrongpass',
            'password': 'wrong123'
        }, follow_redirects=True)
        
        assert b'Неверное имя пользователя или пароль' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Вход с несуществующим пользователем"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password'
        }, follow_redirects=True)
        
        assert b'Неверное имя пользователя или пароль' in response.data
    
    def test_logout(self, client, create_test_user, get_token):
        """Выход из системы"""
        get_token('logoutuser', 'testpass123')
        
        response = client.get('/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Вы вышли из системы' in response.data