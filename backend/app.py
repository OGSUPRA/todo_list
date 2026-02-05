from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
from db.models import init_db
from services.tasks import (
    create_task,
    get_all_tasks,
    get_deleted_tasks,
    mark_task_done,
    mark_all_tasks_done,
    mark_task_notdone,
    delete_task,
    restore_task,
    search_user
)
from services.auth import (
    validate_user
)
from services.registration import (
registration_user,
user_exists
)
from services.users import (
    set_user_avatar,
    get_user_avatar,
    delete_user_by_id,
    update_user_name_by_id,
    check_user_password,
    update_user_password_by_id
)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
app.config['ALLOWED_EXTENSIONS'] = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


def _allowed_avatar_extension(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/deleted")
def deleted_tasks():
    deleted_tasks = get_deleted_tasks(include_done=True)
    return render_template("deleted_tasks.html", deleted_tasks=deleted_tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = search_user(username)

        if validate_user(username, password):
            session['username'] = username
            session['user_id'] = user['id']
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('tasks_list'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route("/registration", methods=['GET', 'POST'])
def registration_users():
    if request.method == 'GET':
        return render_template("registration.html")
    else:
        login = request.form["username"]
        password = request.form["password"]
        
        # Нужно проверить, не существует ли уже такой пользователь
        if user_exists(login):
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template("registration.html")
        
        registration_user(login, password)
        flash('Регистрация успешна! Теперь войдите в систему', 'success')
        return redirect(url_for("login"))

@app.route("/tasks")
def tasks_list():
    user_id = session['user_id']
    tasks = get_all_tasks(user_id, include_done=True)
    avatar_path = get_user_avatar(user_id)
    avatar_url = url_for('static', filename=avatar_path) if avatar_path else None
    return render_template("tasks.html", tasks=tasks, avatar_url=avatar_url)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    description = request.form.get("description")
    user_id = session['user_id']
    create_task(user_id, title, description)
    return redirect(url_for("tasks_list"))

@app.route("/done/<int:task_id>")
def done(task_id):
    mark_task_done(task_id)
    return redirect(url_for("tasks_list"))

@app.route("/alldone")
def alldone():
    mark_all_tasks_done()
    return redirect(url_for("tasks_list"))

@app.route("/notdone/<int:task_id>")
def notdone(task_id):
    mark_task_notdone(task_id)
    return redirect(url_for("tasks_list"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for("tasks_list"))

@app.route("/deleted/restore/<int:task_id>")
def restore(task_id):
    restore_task(task_id)
    return redirect(url_for("deleted_tasks"))

@app.before_request
def check_login():
    allowed = ['login', 'static', 'registration_users', 'index']
    if request.endpoint not in allowed:
        if 'username' not in session:
            return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route("/settings", methods=["POST", "GET"])
def user_settings():
    user_id = session.get('user_id')
    avatar_path = get_user_avatar(user_id) if user_id else None
    avatar_url = url_for('static', filename=avatar_path) if avatar_path else None
    username = session.get('username')
    return render_template("user_settings.html", avatar_url=avatar_url, username=username)


@app.route("/user/avatar", methods=["POST"])
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Файл не найден в запросе', 'error')
        return redirect(url_for('user_settings'))

    file = request.files['avatar']
    if file.filename == '':
        flash('Выберите файл для загрузки', 'error')
        return redirect(url_for('user_settings'))

    if not _allowed_avatar_extension(file.filename):
        flash('Неподдерживаемый формат файла', 'error')
        return redirect(url_for('user_settings'))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    user_id = session.get('user_id')
    if not user_id:
        flash('Требуется авторизация', 'error')
        return redirect(url_for('login'))

    safe_name = secure_filename(file.filename)
    _, ext = os.path.splitext(safe_name)
    filename = f"avatar_{user_id}{ext.lower()}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    relative_path = f"images/{filename}"
    set_user_avatar(user_id, relative_path)

    flash('Аватар успешно загружен', 'success')
    return redirect(url_for('user_settings'))


@app.route("/user/delete", methods=["POST"])
def delete_user():
    user_id = session.get('user_id')
    if not user_id:
        flash('Требуется авторизация', 'error')
        return redirect(url_for('login'))

    delete_user_by_id(user_id)
    session.clear()
    flash('Пользователь успешно удален', 'success')
    return redirect(url_for('login'))


@app.route("/user/name", methods=["POST"])
def update_user_name():
    user_id = session.get('user_id')
    if not user_id:
        flash('Требуется авторизация', 'error')
        return redirect(url_for('login'))

    new_name = request.form.get('new_name')
    if not new_name:
        flash('Имя не может быть пустым', 'error')
        return redirect(url_for('user_settings'))

    update_user_name_by_id(user_id, new_name)
    session['username'] = new_name
    flash('Имя пользователя успешно обновлено', 'success')
    return redirect(url_for('user_settings'))


@app.route("/user/password", methods=["POST"])
def update_user_password():
    user_id = session.get('user_id')
    if not user_id:
        flash('Требуется авторизация', 'error')
        return redirect(url_for('login'))

    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')

    if not old_password or not new_password:
        flash('Поля не могут быть пустыми', 'error')
        return redirect(url_for('user_settings'))

    if not check_user_password(user_id, old_password):
        flash('Неверный старый пароль', 'error')
        return redirect(url_for('user_settings'))

    update_user_password_by_id(user_id, new_password)
    flash('Пароль успешно обновлен', 'success')
    return redirect(url_for('user_settings'))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
