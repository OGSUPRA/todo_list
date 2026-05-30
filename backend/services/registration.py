from db.database import get_connection
from services.auth import hash_password

def user_exists(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND deleted_at IS NULL",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None

def registration_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute(
        "INSERT INTO users (username, password, status_user) VALUES (?, ?, 'past_user')",
        (username, hashed_password)
    )
    conn.commit()
    conn.close()