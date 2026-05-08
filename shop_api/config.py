# app/config.py
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    # Секретный ключ для сессий
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Настройки базы данных
    # SQLite (проще всего для начала)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///shop.db'
    
    # ИЛИ для MySQL:
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/shop_db'
    
    # ИЛИ для PostgreSQL:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/shop_db'
    
    # Отключаем отслеживание изменений (для производительности)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки загрузки файлов
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')