import sqlite3
import os
from flask import current_app, g

def get_db_path():
    """Возвращает путь к файлу базы данных"""
    # Используем путь из конфига Flask, если он есть
    if current_app:
        db_path = current_app.config.get('DATABASE_PATH')
        if db_path:
            return db_path
    
    # Fallback для случаев, когда Flask не доступен (например, скрипты миграции)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    instance_dir = os.path.join(base_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    return os.path.join(instance_dir, 'todo.db')

def get_connection():
    """Возвращает соединение с базой данных SQLite"""
    db_path = get_db_path()
    
    # Убеждаемся, что директория для БД существует
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Чтобы можно было обращаться по именам колонок
    return conn

def get_db():
    """Возвращает соединение с БД с использованием контекста Flask (для запросов)"""
    if 'db' not in g:
        g.db = get_connection()
    return g.db

def close_db(e=None):
    """Закрывает соединение с БД"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Регистрирует функцию закрытия БД"""
    app.teardown_appcontext(close_db)