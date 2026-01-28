from db.database import get_connection

def create_task(title, description=None):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Create task: {title} description: {description}")

    cursor.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description)
    )

    rows_updated = cursor.rowcount
    print(f"DEBUG: Updated {rows_updated} rows")

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


def get_deleted_tasks(include_done=True):
    conn = get_connection()
    cursor = conn.cursor()

    if include_done:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE deleted_at IS NOT NULL
        """)
    else:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE status = 'todo' AND deleted_at IS NOT NULL
        """)

    deleted_tasks = cursor.fetchall()
    conn.close()
    return deleted_tasks


def mark_task_done(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Marking task {task_id} as done")

    cursor.execute("""
        UPDATE tasks
        SET status = 'done'
        WHERE id = ? AND deleted_at IS NULL
    """, (task_id,))

    rows_updated = cursor.rowcount
    print(f"DEBUG: Updated {rows_updated} rows")

    conn.commit()
    conn.close()


def mark_task_notdone(task_id):  #На данный момент реализация данного сервиса отсутствует
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Marking task {task_id} as notdone")

    cursor.execute("""
        UPDATE tasks
        SET status = 'todo'
        WHERE id = ? AND deleted_at IS NULL
    """, (task_id,))

    rows_updated = cursor.rowcount
    print(f"DEBUG: Updated {rows_updated} rows")

    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Marking task {task_id} as deleted_at")

    cursor.execute("""
        UPDATE tasks
        SET deleted_at = CURRENT_TIMESTAMP
        WHERE id = ? AND deleted_at IS NULL
    """, (task_id,))

    rows_updated = cursor.rowcount
    print(f"DEBUG: Updated {rows_updated} rows")

    conn.commit()
    conn.close()


def restore_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Marking task {task_id} as restore_task")

    cursor.execute("""
        UPDATE tasks
        SET deleted_at = NULL
        WHERE id = ? AND deleted_at IS NOT NULL
    """, (task_id,))

    rows_updated = cursor.rowcount
    print(f"DEBUG: Updated {rows_updated} rows")

    conn.commit()
    conn.close()

