from db.database import get_connection
from services.auth import hash_password

def set_user_avatar(user_id, avatar_path):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET avatar_path = ? WHERE id = ?",
        (avatar_path, user_id)
    )
    conn.commit()
    conn.close()

def get_user_avatar(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT avatar_path FROM users WHERE id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result['avatar_path'] if result else None

def delete_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Мягкое удаление
    cursor.execute(
        "UPDATE users SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

def update_user_name_by_id(user_id, new_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET username = ? WHERE id = ?",
        (new_name, user_id)
    )
    conn.commit()
    conn.close()

def check_user_password(user_id, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT id FROM users WHERE id = ? AND password = ? AND deleted_at IS NULL",
        (user_id, hashed_password)
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None

def update_user_password_by_id(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(new_password)
    cursor.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (hashed_password, user_id)
    )
    conn.commit()
    conn.close()