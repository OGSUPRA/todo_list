from db.database import get_connection

def create_task(user_id, title, description=None):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Create task: {title} description: {description} user_id: {user_id}")

    cursor.execute(
        "INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)",
        (title, description, user_id)
    )

    rows_updated = cursor.rowcount
    print(f"DEBUG: Updated {rows_updated} rows")

    conn.commit()
    conn.close()


def search_user(username):
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Start search: {username}")

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))

    user = cursor.fetchone()
    conn.close
    return user

def get_all_tasks(user_id, include_done=True):
    conn = get_connection()
    cursor = conn.cursor()

    if include_done:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE user_id = ? AND deleted_at IS NULL
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE user_id = ? AND status = 'todo' AND deleted_at IS NULL
        """, (user_id,))

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


def mark_all_tasks_done():
    conn = get_connection()
    cursor = conn.cursor()

    print(f"DEBUG: Marking all tasks as done")

    cursor.execute("""
        UPDATE tasks
        SET status = 'done'
        WHERE deleted_at IS NULL
    """)

    rows_updated = cursor.rowcount
    print(f"DEBUG: Updated {rows_updated} rows")

    conn.commit()
    conn.close()


def mark_task_notdone(task_id):
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

    

