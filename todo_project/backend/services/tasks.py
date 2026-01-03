from db.database import get_connection

def create_task(title, description=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description)
    )

    conn.commit()
    conn.close()


def get_all_tasks(include_done=True):
    conn = get_connection()
    cursor = conn.cursor()

    if include_done:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE deleted_at IS NULL
        """)
    else:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE status = 'todo' AND deleted_at IS NULL
        """)

    tasks = cursor.fetchall()
    conn.close()
    return tasks


def mark_task_done(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = 'done'
        WHERE id = ? AND deleted_at IS NULL
    """, (task_id,))

    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET deleted_at = CURRENT_TIMESTAMP
        WHERE id = ? AND deleted_at IS NULL
    """, (task_id,))

    conn.commit()
    conn.close()


def restore_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET deleted_at = NULL
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

