from flask import Flask, render_template, request, redirect, url_for
from db.models import init_db
from services.tasks import (
    create_task,
    get_all_tasks,
    mark_task_done,
    mark_task_notdone,
    delete_task
)

app = Flask(__name__)

@app.route("/")
def index():
    tasks = get_all_tasks(include_done=True)
    return render_template("tasks.html", tasks=tasks)

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

@app.route("/notdone/<int:task_id>")
def notdone(task_id):
    mark_task_notdone(task_id)
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete(task_id):
    delete_task(task_id)
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
