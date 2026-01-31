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
get_all_users
)
from services.registration import registration_user

app = Flask(__name__)
app.secret_key = os.urandom(24)

users_db = get_all_users()

@app.route("/")
def index():
    tasks = get_all_tasks(include_done=True)
    return render_template("tasks.html", tasks=tasks)

@app.route("/deleted")
def deleted_tasks():
    deleted_tasks = get_deleted_tasks(include_done=True)
    return render_template("deleted_tasks.html", deleted_tasks=deleted_tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users_db and users_db[username] == password:
            session['username'] = username
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@app.route("/registration")
def registration_users():
    return render_template("registration.html")

@app.route("/register", methods = ["POST"])
def register_user():
    login = request.form["username"]
    password = request.form["password"]
    registration_user(login, password)
    return redirect(url_for("authorization_users"))

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    description = request.form.get("description")
    create_task(title, description)
    return redirect(url_for("index"))

@app.route("/done/<int:task_id>")
def done(task_id):
    mark_task_done(task_id)
    return redirect(url_for("index"))

@app.route("/alldone")
def alldone():
    mark_all_tasks_done()
    return redirect(url_for("index"))

@app.route("/notdone/<int:task_id>")
def notdone(task_id):
    mark_task_notdone(task_id)
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for("index"))

@app.route("/deleted/restore/<int:task_id>")
def restore(task_id):
    restore_task(task_id)
    return redirect(url_for("deleted_tasks"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
