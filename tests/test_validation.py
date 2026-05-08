# tests/test_validation.py
import pytest


class TestValidation:
    """Тесты валидации данных"""
    
    def test_invalid_json_format(self, client, get_token):
        """Неверный формат JSON"""
        get_token('jsonuser', 'testpass123')
        
        response = client.post('/api/cart/add', 
                              data='invalid json',
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'JSON' in str(data) or 'json' in str(data).lower()
    
    def test_missing_required_fields(self, client, get_token):
        """Отсутствие обязательных полей"""
        get_token('missinguser', 'testpass123')
        
        response = client.post('/api/cart/add', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'required' in str(data).lower()
    
    def test_invalid_data_types(self, client, get_token):
        """Неверные типы данных"""
        get_token('typeuser', 'testpass123')
        
        response = client.post('/api/cart/add', json={
            'product_id': 'not_a_number',
            'quantity': 'not_a_number'
        })
        
        assert response.status_code == 400
    
    def test_negative_quantity(self, client, get_token, create_test_product):
        """Отрицательное количество товара"""
        get_token('neguser', 'testpass123')
        product = create_test_product()
        
        response = client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': -5
        })
        
        assert response.status_code == 400
    
    def test_invalid_phone_format(self, client, get_token, create_test_product):
        """Неверный формат телефона"""
        get_token('phoneuser', 'testpass123')
        product = create_test_product(price=1000)
        
        client.post('/api/cart/add', json={
            'product_id': product.id_product,
            'quantity': 1
        })
        
        response = client.post('/checkout', data={
            'shipping_address': 'Test Address',
            'phone': 'invalid-phone'
        }, follow_redirects=True)
        
        # Должна быть ошибка валидации телефона
        assert response.status_code == 200