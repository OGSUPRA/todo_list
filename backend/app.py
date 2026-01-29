from flask import Flask, render_template, request, redirect, url_for
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

app = Flask(__name__)

@app.route("/")
def index():
    tasks = get_all_tasks(include_done=True)
    return render_template("tasks.html", tasks=tasks)

@app.route("/deleted")
def deleted_tasks():
    deleted_tasks = get_deleted_tasks(include_done=True)
    return render_template("deleted_tasks.html", deleted_tasks=deleted_tasks)

@app.route("/authorization")
def authorization_users():
    return render_template("authorization.html")

@app.route("/registration")
def registration_users():
    return render_template("registration.html")

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
