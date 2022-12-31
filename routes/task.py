from flask import Blueprint

from models import *
from routes import by_id

bluep = Blueprint('task', __name__, url_prefix='/task/')


@bluep.post('/<int:task_id>/complete')
@by_id(Task)
def complete_task(task: Task):
    task.completed = True
    db.session.commit()


@bluep.post('/<int:task_id>/uncomplete')
@by_id(Task)
def uncomplete_task(task: Task):
    task.completed = False
    db.session.commit()