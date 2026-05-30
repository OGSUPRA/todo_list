from db.database import get_connection
import hashlib

def hash_password(password):
    """Простое хэширование пароля (лучше использовать bcrypt в production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ? AND deleted_at IS NULL",
        (username, hashed_password)
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND deleted_at IS NULL",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None