from functools import wraps

from flask import Blueprint, request, redirect
from werkzeug.exceptions import BadRequest, NotFound

from models import *

bluep = Blueprint('task', __name__, url_prefix='/task/')


def task_by_ids(route):
    @wraps(route)
    def wrapper(device_id, operation_id):
        task = Task.query.filter_by(device_id=device_id, operation_id=operation_id).first()
        if task is None:
            raise NotFound()

        return route(task)
    return wrapper


@bluep.post('<int:device_id>/<int:operation_id>/complete')
@task_by_ids
def complete_task(task):
    task.completed = True
    db.session.commit()
    return 'completed'


@bluep.post('<int:device_id>/<int:operation_id>/uncomplete')
@task_by_ids
def uncomplete_task(task):
    task.completed = False
    db.session.commit()
    return 'uncompleted'


@bluep.post('<int:device_id>/<int:operation_id>/delete')
@task_by_ids
def delete_task(task):
    db.session.delete(task)
    db.session.commit()
    return 'deleted'


@bluep.post('create')
def create_task():
    operation = Operation.query.filter_by(name=request.form['operationName']).first()
    device_id = int(request.form['deviceId'])

    if Task.query.filter_by(operation=operation, device_id=device_id).count():
        raise BadRequest()

    db.session.add(Task(operation=operation, device_id=device_id))
    db.session.commit()

    return redirect(f'/device/{device_id}')
