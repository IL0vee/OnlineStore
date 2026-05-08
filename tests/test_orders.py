# tests/test_orders.py
import pytest


class TestOrders:
    """Тесты операций с заказами"""
    
    def test_create_order_authenticated(self, client, get_token, create_test_product):
        """Создание заказа авторизованным пользователем"""
        get_token('orderuser', 'testpass123')
        product = create_test_product(name='Order Product', price=3000)
        
        # Добавляем товар в корзину
        client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 1
        })
        
        # Оформляем заказ
        response = client.post('/checkout', data={
            'shipping_address': 'Test Address, 123',
            'phone': '+7 999 123-45-67',
            'comment': 'Test comment'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'заказ' in response.data.lower()
    
    def test_create_order_empty_cart(self, client, get_token):
        """Создание заказа с пустой корзиной"""
        get_token('emptyorder', 'testpass123')
        
        response = client.post('/checkout', data={
            'shipping_address': 'Test Address',
            'phone': '+7 999 123-45-67'
        }, follow_redirects=True)
        
        assert b'корзина пуста' in response.data.lower()
    
    def test_create_order_unauthenticated(self, client):
        """Создание заказа без авторизации"""
        response = client.get('/checkout', follow_redirects=True)
        
        # Должен перенаправить на страницу входа
        assert b'Login' in response.data or b'Sign in' in response.data
    
    def test_view_orders_list(self, client, get_token):
        """Просмотр списка заказов"""
        get_token('vieworders', 'testpass123')
        
        response = client.get('/orders')
        
        assert response.status_code == 200
    
    def test_create_order_invalid_address(self, client, get_token, create_test_product):
        """Создание заказа с невалидным адресом"""
        get_token('invalidorder', 'testpass123')
        product = create_test_product(price=1000)
        
        client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 1
        })
        
        response = client.post('/checkout', data={
            'shipping_address': '',  # Пустой адрес
            'phone': ''
        }, follow_redirects=True)
        
        assert b'заполните' in response.data.lower() or b'required' in response.data.lower()