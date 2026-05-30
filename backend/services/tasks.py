from db.database import get_connection
from flask import current_app

def create_task(user_id, title, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title, description, status) VALUES (?, ?, ?, 'todo')",
        (user_id, title, description)
    )
    conn.commit()
    conn.close()

def get_all_tasks(user_id, include_done=True):
    conn = get_connection()
    cursor = conn.cursor()
    
    if include_done:
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND deleted_at IS NULL ORDER BY created_at DESC",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND status = 'todo' AND deleted_at IS NULL ORDER BY created_at DESC",
            (user_id,)
        )
    
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_deleted_tasks(include_done=True):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tasks WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC"
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def mark_task_done(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'done' WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

def mark_all_tasks_done():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'done' WHERE status = 'todo' AND deleted_at IS NULL"
    )
    conn.commit()
    conn.close()

def mark_task_notdone(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'todo' WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

def restore_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET deleted_at = NULL WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

def search_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND deleted_at IS NULL",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None