# app/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Создаем объект базы данных
db = SQLAlchemy()

# Таблица для связи товаров и категорий (многие ко многим)
product_category = db.Table('product_category',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id_product'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id_category'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    orders = db.relationship('Order', backref='customer', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id_user)
    
    def to_dict(self):
        return {
            'id_user': self.id_user,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    __tablename__ = 'category'
    id_category = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    slug = db.Column(db.String(100), unique=True)
    
    # Связи
    products = db.relationship('Product', secondary=product_category, back_populates='categories')
    
    def to_dict(self):
        return {
            'id_category': self.id_category,
            'name': self.name,
            'description': self.description,
            'slug': self.slug
        }

class Product(db.Model):
    __tablename__ = 'product'
    id_product = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    sku = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    categories = db.relationship('Category', secondary=product_category, back_populates='products')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    
    def to_dict(self):
        return {
            'id_product': self.id_product,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'old_price': self.old_price,
            'stock': self.stock,
            'image_url': self.image_url,
            'sku': self.sku,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'categories': [cat.to_dict() for cat in self.categories]
        }

class CartItem(db.Model):
    __tablename__ = 'cart_item'
    id_cart_item = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    id_product = db.Column(db.Integer, db.ForeignKey('product.id_product'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id_cart_item': self.id_cart_item,
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'subtotal': self.product.price * self.quantity
        }

class Order(db.Model):
    __tablename__ = 'order'
    id_order = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    
    # Связи
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id_order': self.id_order,
            'order_number': self.order_number,
            'status': self.status,
            'total_amount': self.total_amount,
            'shipping_address': self.shipping_address,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id_order_item = db.Column(db.Integer, primary_key=True)
    id_order = db.Column(db.Integer, db.ForeignKey('order.id_order'), nullable=False)
    id_product = db.Column(db.Integer, db.ForeignKey('product.id_product'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id_order_item': self.id_order_item,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': self.price_at_time,
            'subtotal': self.price_at_time * self.quantity
        }