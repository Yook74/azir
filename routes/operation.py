from flask import Blueprint, render_template, request

from routes import by_id
from models import Operation, db

bluep = Blueprint('operation', __name__, url_prefix='/operation/')


@bluep.get('create')
def operation_form():
    return render_template('operation_form.html')


@bluep.post('create')
def new_operation():
    db.session.add(Operation(**{key: request.form[key] for key in ('description', 'name')}))
    db.session.commit()

    return operation_form()


@bluep.get('<int:id>')
@by_id(Operation)
def operation_detail(operation):
    return render_template('operation_description.html', operation=operation)