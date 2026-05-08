# app/__init__.py
from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from config import Config
import os
import time

# Импортируем базу данных
from app.models import db

# Импортируем настройку логирования
from app.logging_config import setup_logging, log_request, log_error

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Настройка логирования
    setup_logging(app)
    
    # Инициализируем базу данных
    db.init_app(app)
    
    # Инициализируем миграции
    migrate = Migrate(app, db)
    
    # Инициализируем менеджер входа
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Регистрируем blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Регистрируем middleware для логирования
    @app.before_request
    def before_request():
        """Логируем начало запроса"""
        g.start_time = time.time()
        g.user_id = getattr(current_user, 'id_user', None)
        g.username = getattr(current_user, 'username', None)
        
        # Логируем все запросы, кроме статики
        if not request.path.startswith('/static'):
            log_request(app, request, g.user_id, g.username)
    
    @app.after_request
    def after_request(response):
        """Логируем время выполнения запроса"""
        if hasattr(g, 'start_time'):
            elapsed = (time.time() - g.start_time) * 1000
            app.logger.info(f"Response | {request.method} {request.path} | Status: {response.status_code} | Time: {elapsed:.2f}ms")
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Глобальный обработчик ошибок с логированием"""
        log_error(app, e, request, g.user_id, g.username)
        return {'error': 'Internal Server Error'}, 500
    
    app.logger.info('🚀 Shop API started')
    return app