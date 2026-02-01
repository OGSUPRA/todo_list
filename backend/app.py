from flask import Flask, render_template, request, redirect, url_for, session, flash
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
    restore_task
)
from services.auth import (
    validate_user
)
from services.registration import (
registration_user,
user_exists
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/tasks")
def tasks_list():
    tasks = get_all_tasks(include_done=True)
    return render_template("tasks.html", tasks=tasks)

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
        
        if validate_user(username, password):
            session['username'] = username
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

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    description = request.form.get("description")
    create_task(title, description)
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
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
