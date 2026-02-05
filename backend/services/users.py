from db.database import get_connection


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
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None
    return row["avatar_path"]


def delete_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
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

    cursor.execute(
        "SELECT password FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False
    return row["password"] == password


def update_user_password_by_id(user_id, new_password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (new_password, user_id)
    )

    conn.commit()
    conn.close()