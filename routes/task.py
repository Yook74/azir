from flask import Blueprint, request, redirect
from werkzeug.exceptions import BadRequest, NotFound

from models import *
from routes import by_id

bluep = Blueprint('task', __name__, url_prefix='/task/')


@bluep.post('<int:device_id>/<int:operation_id>/complete')
def complete_task(device_id, operation_id):
    task = Task.query.filter_by(device_id=device_id, operation_id=operation_id).first()
    if task is None:
        raise NotFound()

    task.completed = True
    db.session.commit()
    return 'completed'


@bluep.post('<int:device_id>/<int:operation_id>/uncomplete')
def uncomplete_task(device_id, operation_id):
    task = Task.query.filter_by(device_id=device_id, operation_id=operation_id).first()
    if task is None:
        raise NotFound()

    task.completed = False
    db.session.commit()
    return 'uncompleted'


@bluep.post('create')
def create_task():
    operation = Operation.query.filter_by(name=request.form['operationName']).first()
    device_id = int(request.form['deviceId'])

    if Task.query.filter_by(operation=operation, device_id=device_id).count():
        raise BadRequest()

    db.session.add(Task(operation=operation, device_id=device_id))
    db.session.commit()

    return redirect(f'/device/{device_id}')
