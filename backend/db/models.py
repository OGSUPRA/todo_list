from db.database import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK(status IN ('todo','done')) DEFAULT 'todo',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deleted_at DATETIME NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL,
        password TEXT NOT NULL,
        status_user TEXT CHECK(status_user IN ('admin','past_user')) DEFAULT 'past_user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        deleted_at DATETIME NULL
    );
    """)

    conn.commit()
    conn.close()
