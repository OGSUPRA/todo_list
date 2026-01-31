from db.database import get_connection


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, password FROM users
    """)

    users = cursor.fetchall()
    conn.close()
    users_dict = {row[0]: row[1] for row in users}
    return users_dict