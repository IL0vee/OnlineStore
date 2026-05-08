# app/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from flask import request, session, jsonify
from functools import wraps
import time


def setup_logging(app):
    """Настройка логирования приложения"""
    
    # Создаем папку для логов, если её нет
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"📁 Создана папка для логов: {log_dir}")
    
    # ---- Основной файл логов (все действия) ----
    main_handler = RotatingFileHandler(
        os.path.join(log_dir, 'shop_api.log'),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    main_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    ))
    main_handler.setLevel(logging.INFO)
    
    # ---- Файл для ошибок (только ошибки) ----
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=20,
        encoding='utf-8'
    )
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(pathname)s:%(lineno)d | %(message)s'
    ))
    error_handler.setLevel(logging.ERROR)
    
    # ---- Файл для авторизации (логины/выходы) ----
    auth_handler = RotatingFileHandler(
        os.path.join(log_dir, 'auth.log'),
        maxBytes=1 * 1024 * 1024,  # 1 MB
        backupCount=5,
        encoding='utf-8'
    )
    auth_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(message)s'
    ))
    auth_handler.setLevel(logging.INFO)
    
    # ---- Файл для запросов (API вызовы) ----
    request_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'requests.log'),
        when='midnight',  # Каждый день в полночь
        interval=1,
        backupCount=30,  # Хранить 30 дней
        encoding='utf-8'
    )
    request_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(message)s'
    ))
    request_handler.setLevel(logging.INFO)
    
    # Добавляем обработчики к логгеру приложения
    app.logger.addHandler(main_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
    
    # Создаем отдельные логгеры
    app.auth_logger = logging.getLogger('auth')
    app.auth_logger.addHandler(auth_handler)
    app.auth_logger.setLevel(logging.INFO)
    
    app.request_logger = logging.getLogger('request')
    app.request_logger.addHandler(request_handler)
    app.request_logger.setLevel(logging.INFO)
    
    # Отключаем ротацию для тестов
    if app.config.get('TESTING'):
        main_handler.doRollover = lambda: None
        error_handler.doRollover = lambda: None
        auth_handler.doRollover = lambda: None
        request_handler.doRollover = lambda: None
    
    app.logger.info('🚀 Application started')
    return app.logger


def log_auth_attempt(app, username, success, ip_address):
    """Логирование попыток авторизации"""
    status = "SUCCESS" if success else "FAILED"
    app.auth_logger.info(f"AUTH | {status} | User: {username} | IP: {ip_address}")


def log_user_action(app, user_id, username, action, details=None):
    """Логирование действий пользователя"""
    log_msg = f"ACTION | User: {username} (ID: {user_id}) | Action: {action}"
    if details:
        log_msg += f" | Details: {details}"
    app.auth_logger.info(log_msg)
    app.logger.info(log_msg)


def log_request(app, request, user_id=None, username=None):
    """Логирование HTTP запросов"""
    user_info = f"User: {username or 'Anonymous'} (ID: {user_id or 'N/A'})"
    log_msg = f"{request.method} | {request.path} | {user_info} | IP: {request.remote_addr}"
    
    # Логируем тело запроса для важных действий
    if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
        try:
            data = request.get_json()
            # Убираем пароли из логов
            if data and 'password' in data:
                data = {**data, 'password': '***HIDDEN***'}
            log_msg += f" | Body: {data}"
        except:
            pass
    
    app.request_logger.info(log_msg)
    app.logger.info(log_msg)


def log_error(app, error, request=None, user_id=None, username=None):
    """Логирование ошибок"""
    error_msg = f"ERROR | {type(error).__name__}: {str(error)}"
    if request:
        error_msg += f" | Path: {request.path} | Method: {request.method} | IP: {request.remote_addr}"
    if user_id:
        error_msg += f" | User ID: {user_id} | Username: {username}"
    
    app.logger.error(error_msg, exc_info=True)