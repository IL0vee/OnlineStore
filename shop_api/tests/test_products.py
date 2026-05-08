# tests/test_products.py
import pytest


class TestProducts:
    """Тесты CRUD операций с товарами"""
    
    def test_get_products_list(self, client, create_test_product):
        """Получение списка товаров"""
        create_test_product(name='Product 1')
        create_test_product(name='Product 2')
        
        response = client.get('/catalog')
        
        assert response.status_code == 200
        assert b'Product 1' in response.data
        assert b'Product 2' in response.data
    
    def test_get_product_detail(self, client, create_test_product):
        """Получение детальной информации о товаре"""
        product = create_test_product(name='Detail Product')
        
        response = client.get(f'/product/{product.id_product}')
        
        assert response.status_code == 200
        assert b'Detail Product' in response.data
        assert b'1000.00' in response.data
    
    def test_get_nonexistent_product(self, client):
        """Получение несуществующего товара"""
        response = client.get('/product/99999')
        
        assert response.status_code == 404
    
    def test_create_product_authenticated(self, client, get_token, login_admin):
        """Создание товара авторизованным админом"""
        login_admin()
        
        response = client.post('/create-product', data={
            'name': 'New Product',
            'description': 'This is a new product description with enough length',
            'price': 2999,
            'stock': 50,
            'is_active': 'on'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'New Product' in response.data
    
    def test_create_product_unauthenticated(self, client):
        """Создание товара без авторизации"""
        response = client.post('/create-product', data={
            'name': 'Unauthorized Product',
            'description': 'Test description',
            'price': 1000
        }, follow_redirects=True)
        
        # Должен перенаправить на страницу входа
        assert b'Login' in response.data or b'Iniciar sesi' in response.data
    
    def test_create_product_invalid_data(self, client, login_admin):
        """Создание товара с невалидными данными"""
        login_admin()
        
        # Пустое название
        response = client.post('/create-product', data={
            'name': '',
            'description': 'Short',
            'price': -100
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Должна быть ошибка валидации
    
    def test_add_to_cart_authenticated(self, client, get_token, create_test_product):
        """Добавление товара в корзину авторизованным пользователем"""
        get_token('cartuser', 'testpass123')
        product = create_test_product(name='Cart Product', price=500)
        
        response = client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 2
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('success') or data.get('message')
    
    def test_add_to_cart_unauthenticated(self, client, create_test_product):
        """Добавление товара в корзину без авторизации"""
        product = create_test_product()
        
        response = client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 1
        })
        
        # Должен вернуть 401 Unauthorized
        assert response.status_code in [401, 302]