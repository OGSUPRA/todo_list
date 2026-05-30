import os
import sqlite3
from flask import current_app
from db.database import get_connection

def init_db():
    """Инициализирует базу данных с правильным путём из конфига Flask"""
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица tasks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK(status IN ('todo','done')) DEFAULT 'todo',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deleted_at DATETIME NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE NO ACTION
    );
    """)

    # Таблица users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        avatar_path TEXT,
        status_user TEXT CHECK(status_user IN ('admin','past_user')) DEFAULT 'past_user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deleted_at DATETIME NULL
    );
    """)

    # Проверка и добавление колонки avatar_path (если её нет)
    cursor.execute("PRAGMA table_info(users);")
    existing_columns = {row[1] for row in cursor.fetchall()}  # row[1] - имя колонки
    if "avatar_path" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN avatar_path TEXT;")

    conn.commit()
    conn.close()
    
    # Проверяем, что БД создана
    db_path = current_app.config.get('DATABASE_PATH', 'todo.db')
    print(f"База данных инициализирована: {db_path}")
