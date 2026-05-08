# tests/test_cart.py
import pytest


class TestCart:
    """Тесты операций с корзиной"""
    
    def test_view_cart_empty(self, client, get_token):
        """Просмотр пустой корзины"""
        get_token('emptycart', 'testpass123')
        
        response = client.get('/cart')
        
        assert response.status_code == 200
        assert b'корзина пуста' in response.data.lower()
    
    def test_add_to_cart(self, client, get_token, create_test_product):
        """Добавление товара в корзину"""
        get_token('addcart', 'testpass123')
        product = create_test_product(name='Cart Item', price=1500)
        
        response = client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 1
        })
        
        assert response.status_code == 200
        
        # Проверяем, что товар появился в корзине
        cart_response = client.get('/cart')
        assert b'Cart Item' in cart_response.data
    
    def test_update_cart_quantity(self, client, get_token, create_test_product):
        """Обновление количества товара в корзине"""
        get_token('updatecart', 'testpass123')
        product = create_test_product(name='Update Item', price=2000)
        
        # Добавляем товар
        client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 1
        })
        
        # Получаем ID элемента корзины
        cart_response = client.get('/cart')
        
        # Обновляем количество
        response = client.post('/api/cart/update', json={
            'cart_item_id': 1,
            'quantity': 3
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_remove_from_cart(self, client, get_token, create_test_product):
        """Удаление товара из корзины"""
        get_token('removecart', 'testpass123')
        product = create_test_product(name='Remove Item', price=500)
        
        # Добавляем товар
        client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 1
        })
        
        # Удаляем товар
        response = client.delete('/api/cart/remove/1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('total_items') == 0
    
    def test_add_to_cart_insufficient_stock(self, client, get_token, create_test_product):
        """Добавление товара с недостаточным количеством на складе"""
        get_token('stockuser', 'testpass123')
        product = create_test_product(stock=1)
        
        response = client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 100
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Недостаточно' in str(data)