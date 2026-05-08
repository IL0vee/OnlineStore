# app/routes.py
from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Product, Category, CartItem, Order, OrderItem
from app.logging_config import log_auth_attempt, log_user_action, log_error
from datetime import datetime
import uuid
import re

main_bp = Blueprint('main', __name__)


# =====================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =====================================================

def validate_phone(phone):
    """Проверка формата телефона"""
    pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    return bool(re.match(pattern, phone))


def validate_email(email):
    """Проверка формата email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# =====================================================
# ГЛАВНАЯ СТРАНИЦА (КАТАЛОГ)
# =====================================================

@main_bp.route('/')
def index():
    """Главная страница с каталогом"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Получаем товары с пагинацией
    products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Избранные товары для слайдера
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(6).all()
    
    # Категории для боковой панели
    categories = Category.query.all()
    
    return render_template('index.html', 
                         products=products, 
                         featured_products=featured_products,
                         categories=categories)


# =====================================================
# КАТАЛОГ ТОВАРОВ
# =====================================================

@main_bp.route('/catalog')
def catalog():
    """Страница каталога с фильтрацией и сортировкой"""
    page = request.args.get('page', 1, type=int)
    per_page = 12
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    
    query = Product.query.filter_by(is_active=True)
    
    # Фильтр по категории
    if category_id:
        query = query.join(Product.categories).filter(Category.id_category == category_id)
    
    # Поиск по названию
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    # Фильтр по цене
    if price_min:
        query = query.filter(Product.price >= price_min)
    if price_max:
        query = query.filter(Product.price <= price_max)
    
    # Сортировка
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'name_asc':
        query = query.order_by(Product.name.asc())
    elif sort == 'name_desc':
        query = query.order_by(Product.name.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    
    return render_template('catalog.html', products=products, categories=categories)


# =====================================================
# КАРТОЧКА ТОВАРА
# =====================================================

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Страница товара"""
    product = Product.query.get_or_404(product_id)
    
    # Похожие товары (из тех же категорий)
    similar_products = []
    if product.categories:
        category_ids = [cat.id_category for cat in product.categories]
        similar_products = Product.query.filter(
            Product.id_product != product_id,
            Product.is_active == True,
            Product.categories.any(Category.id_category.in_(category_ids))
        ).limit(4).all()
    
    return render_template('product_detail.html', 
                         product=product, 
                         similar_products=similar_products)


# =====================================================
# АУТЕНТИФИКАЦИЯ
# =====================================================

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Валидация
        if not username or len(username) < 3:
            flash('Имя пользователя должно содержать минимум 3 символа', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Неверный формат email', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('register.html')
        
        # Проверка уникальности
        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('register.html')
        
        # Создание пользователя
        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Логируем регистрацию
        current_app.auth_logger.info(f"REGISTER | User: {username} | IP: {request.remote_addr}")
        
        flash('Регистрация прошла успешно! Теперь войдите в систему.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        success = user and user.check_password(password)
        
        # Логируем попытку входа
        log_auth_attempt(current_app, username, success, request.remote_addr)
        
        if success:
            login_user(user, remember=remember)
            log_user_action(current_app, user.id_user, user.username, 'LOGIN')
            flash('Вы успешно вошли в систему', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    log_user_action(current_app, current_user.id_user, current_user.username, 'LOGOUT')
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('main.index'))


# =====================================================
# КОРЗИНА
# =====================================================

@main_bp.route('/cart')
@login_required
def cart():
    """Страница корзины"""
    cart_items = CartItem.query.filter_by(id_user=current_user.id_user).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)


@main_bp.route('/api/cart/count')
@login_required
def get_cart_count():
    """Получить количество товаров в корзине"""
    total = db.session.query(db.func.sum(CartItem.quantity)).filter_by(
        id_user=current_user.id_user
    ).scalar() or 0
    return jsonify({'count': total})


@main_bp.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Добавление товара в корзину"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'error': 'Product ID required'}), 400
    
    if not isinstance(quantity, int) or quantity < 1:
        return jsonify({'error': 'Quantity must be positive integer'}), 400
    
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    if not product.is_active:
        return jsonify({'error': 'Product is not available'}), 400
    
    if product.stock < quantity:
        return jsonify({'error': f'Only {product.stock} items available'}), 400
    
    # Проверяем, есть ли уже товар в корзине
    cart_item = CartItem.query.filter_by(
        id_user=current_user.id_user,
        id_product=product_id
    ).first()
    
    if cart_item:
        if product.stock < cart_item.quantity + quantity:
            return jsonify({'error': f'Only {product.stock} items available'}), 400
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            id_user=current_user.id_user,
            id_product=product_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    # Логируем действие
    log_user_action(current_app, current_user.id_user, current_user.username, 
                   'ADD_TO_CART', f"Product ID: {product_id}, Quantity: {quantity}")
    
    # Получаем общее количество товаров в корзине
    total_items = db.session.query(db.func.sum(CartItem.quantity)).filter_by(
        id_user=current_user.id_user
    ).scalar() or 0
    
    return jsonify({
        'success': True,
        'message': 'Товар добавлен в корзину',
        'cart_count': total_items
    }), 200


@main_bp.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart():
    """Обновление количества товара в корзине"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    cart_item_id = data.get('cart_item_id')
    quantity = data.get('quantity')
    
    if not cart_item_id:
        return jsonify({'error': 'Cart item ID required'}), 400
    
    cart_item = CartItem.query.get(cart_item_id)
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    if cart_item.id_user != current_user.id_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        if cart_item.product.stock < quantity:
            return jsonify({'error': f'Only {cart_item.product.stock} items available'}), 400
        cart_item.quantity = quantity
    
    db.session.commit()
    
    # Пересчитываем общую сумму
    cart_items = CartItem.query.filter_by(id_user=current_user.id_user).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    return jsonify({
        'success': True,
        'total': total,
        'total_items': total_items,
        'message': 'Корзина обновлена'
    }), 200


@main_bp.route('/api/cart/remove/<int:cart_item_id>', methods=['DELETE'])
@login_required
def remove_from_cart(cart_item_id):
    """Удаление товара из корзины"""
    cart_item = CartItem.query.get(cart_item_id)
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    if cart_item.id_user != current_user.id_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    # Пересчитываем общую сумму
    cart_items = CartItem.query.filter_by(id_user=current_user.id_user).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    # Логируем действие
    log_user_action(current_app, current_user.id_user, current_user.username, 
                   'REMOVE_FROM_CART', f"Product: {cart_item.product.name}")
    
    return jsonify({
        'success': True,
        'total': total,
        'total_items': total_items,
        'message': 'Товар удален из корзины'
    }), 200


# =====================================================
# ОФОРМЛЕНИЕ ЗАКАЗА
# =====================================================

@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    cart_items = CartItem.query.filter_by(id_user=current_user.id_user).all()
    
    if not cart_items:
        flash('Корзина пуста', 'warning')
        return redirect(url_for('main.cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        phone = request.form.get('phone')
        comment = request.form.get('comment', '')
        
        # Валидация
        if not shipping_address or len(shipping_address) < 5:
            flash('Укажите полный адрес доставки', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total)
        
        if not phone or not validate_phone(phone):
            flash('Укажите корректный номер телефона', 'error')
            return render_template('checkout.html', cart_items=cart_items, total=total)
        
        # Создаем заказ
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id_user}"
        
        order = Order(
            id_user=current_user.id_user,
            order_number=order_number,
            total_amount=total,
            shipping_address=shipping_address,
            phone=phone,
            comment=comment,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()
        
        # Создаем позиции заказа
        for cart_item in cart_items:
            order_item = OrderItem(
                id_order=order.id_order,
                id_product=cart_item.id_product,
                quantity=cart_item.quantity,
                price_at_time=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Уменьшаем количество товара на складе
            cart_item.product.stock -= cart_item.quantity
        
        # Очищаем корзину
        CartItem.query.filter_by(id_user=current_user.id_user).delete()
        
        db.session.commit()
        
        # Логируем оформление заказа
        log_user_action(current_app, current_user.id_user, current_user.username, 
                       'CHECKOUT', f"Order: {order_number}, Total: {total}")
        
        flash(f'Заказ #{order_number} успешно оформлен!', 'success')
        return redirect(url_for('main.order_success', order_id=order.id_order))
    
    return render_template('checkout.html', cart_items=cart_items, total=total)


@main_bp.route('/api/checkout', methods=['POST'])
@login_required
def process_checkout_api():
    """API обработка оформления заказа"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Проверяем корзину
        cart_items = CartItem.query.filter_by(id_user=current_user.id_user).all()
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Валидация
        required_fields = ['shipping_address', 'phone', 'total']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({'error': f'Missing fields: {missing}'}), 400
        
        if not validate_phone(data['phone']):
            return jsonify({'error': 'Invalid phone format'}), 400
        
        # Создаем заказ
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id_user}"
        
        order = Order(
            id_user=current_user.id_user,
            order_number=order_number,
            total_amount=data['total'],
            shipping_address=data['shipping_address'],
            phone=data['phone'],
            comment=data.get('comment', ''),
            status='pending'
        )
        db.session.add(order)
        db.session.flush()
        
        # Создаем позиции заказа
        for cart_item in cart_items:
            order_item = OrderItem(
                id_order=order.id_order,
                id_product=cart_item.id_product,
                quantity=cart_item.quantity,
                price_at_time=cart_item.product.price
            )
            db.session.add(order_item)
            cart_item.product.stock -= cart_item.quantity
        
        # Очищаем корзину
        CartItem.query.filter_by(id_user=current_user.id_user).delete()
        
        db.session.commit()
        
        # Логируем
        log_user_action(current_app, current_user.id_user, current_user.username, 
                       'CHECKOUT_API', f"Order: {order_number}")
        
        return jsonify({
            'success': True,
            'order_id': order.id_order,
            'order_number': order_number
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_error(current_app, e, request, current_user.id_user, current_user.username)
        return jsonify({'error': str(e)}), 500


# =====================================================
# ЗАКАЗЫ
# =====================================================

@main_bp.route('/orders')
@login_required
def orders():
    """Страница с заказами пользователя"""
    user_orders = Order.query.filter_by(id_user=current_user.id_user).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)


@main_bp.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    """Страница успешного оформления заказа"""
    order = Order.query.get_or_404(order_id)
    
    if order.id_user != current_user.id_user:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('order_success.html', order=order)


# =====================================================
# ПРОФИЛЬ
# =====================================================

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Страница профиля пользователя"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        
        # Проверяем уникальность
        if username != current_user.username:
            existing = User.query.filter_by(username=username).first()
            if existing:
                flash('Имя пользователя уже занято', 'error')
                return redirect(url_for('main.profile'))
        
        if email != current_user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash('Email уже используется', 'error')
                return redirect(url_for('main.profile'))
        
        if not validate_email(email):
            flash('Неверный формат email', 'error')
            return redirect(url_for('main.profile'))
        
        current_user.username = username
        current_user.email = email
        current_user.full_name = full_name
        
        # Смена пароля
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Текущий пароль неверен', 'error')
                return redirect(url_for('main.profile'))
            
            if new_password != confirm_password:
                flash('Новый пароль и подтверждение не совпадают', 'error')
                return redirect(url_for('main.profile'))
            
            if len(new_password) < 6:
                flash('Пароль должен быть не менее 6 символов', 'error')
                return redirect(url_for('main.profile'))
            
            current_user.set_password(new_password)
            flash('Пароль успешно изменен', 'success')
        
        db.session.commit()
        
        # Логируем
        log_user_action(current_app, current_user.id_user, current_user.username, 'PROFILE_UPDATE')
        
        flash('Профиль обновлен', 'success')
        return redirect(url_for('main.profile'))
    
    # Статистика
    orders_count = Order.query.filter_by(id_user=current_user.id_user).count()
    total_spent = db.session.query(db.func.sum(Order.total_amount)).filter_by(
        id_user=current_user.id_user
    ).filter(Order.status.in_(['paid', 'delivered'])).scalar() or 0
    
    return render_template('profile.html', 
                         orders_count=orders_count, 
                         total_spent=total_spent)


# =====================================================
# ПРОМОКОДЫ (пример реализации)
# =====================================================

@main_bp.route('/api/apply-promo', methods=['POST'])
@login_required
def apply_promo():
    """Применение промокода"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    promo_code = data.get('promo_code', '').upper().strip()
    subtotal = data.get('subtotal', 0)
    
    # Пример промокодов
    promos = {
        'SALE10': {'discount_percent': 10, 'min_amount': 1000},
        'SALE20': {'discount_percent': 20, 'min_amount': 3000},
        'FREESHIP': {'discount_percent': 0, 'min_amount': 0, 'free_shipping': True},
        'WELCOME15': {'discount_percent': 15, 'min_amount': 500}
    }
    
    if promo_code not in promos:
        return jsonify({'error': 'Неверный промокод'}), 400
    
    promo = promos[promo_code]
    
    if subtotal < promo['min_amount']:
        return jsonify({
            'error': f'Промокод действует при заказе от {promo["min_amount"]} ₽'
        }), 400
    
    discount = subtotal * promo['discount_percent'] / 100 if promo['discount_percent'] > 0 else 0
    
    # Логируем применение промокода
    log_user_action(current_app, current_user.id_user, current_user.username, 
                   'APPLY_PROMO', f"Code: {promo_code}, Discount: {discount}")
    
    return jsonify({
        'success': True,
        'discount': discount,
        'message': f'Промокод {promo_code} применен!',
        'free_shipping': promo.get('free_shipping', False)
    }), 200


# =====================================================
# КАТЕГОРИИ (API)
# =====================================================

@main_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """Получить список категорий"""
    categories = Category.query.all()
    return jsonify([{
        'id_category': cat.id_category,
        'name': cat.name,
        'description': cat.description,
        'slug': cat.slug
    } for cat in categories]), 200


# =====================================================
# ТОВАРЫ (API)
# =====================================================

@main_bp.route('/api/products', methods=['GET'])
def get_products():
    """Получить список товаров (API)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    products = Product.query.filter_by(is_active=True).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'products': [p.to_dict() for p in products.items],
        'total': products.total,
        'page': products.page,
        'pages': products.pages
    }), 200


@main_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Получить товар по ID (API)"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


# =====================================================
# ЗДОРОВЬЕ ПРИЛОЖЕНИЯ
# =====================================================

@main_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности приложения"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db.session.execute('SELECT 1') else 'error'
    }), 200