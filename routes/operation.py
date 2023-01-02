from flask import Blueprint, render_template, request

from routes import by_id
from models import Operation, Goal, db

bluep = Blueprint('operation', __name__, url_prefix='/operation/')


@bluep.get('create')
def operation_form():
    return render_template(
        'operation_form.html',
        goals=Goal.query.all(),
        operations=Operation.query.all(),
    )


@bluep.post('create')
def new_operation():
    new_op = Operation(
        name=request.form['name'], description=request.form['description'],
        goal_id=request.form['goal'] if request.form['goal'] != 'null' else None
    )

    if request.form['afterOperationName'] == 'First':
        for op in Operation.query:
            op.order += 1

        new_op.order = 0
    else:
        before_op = Operation.query.filter_by(name=request.form['afterOperationName']).first()
        for op in Operation.query.filter(Operation.order > before_op.order):
            op.order += 1

        new_op.order = before_op.order + 1

    db.session.add(new_op)
    db.session.commit()

    return operation_form()


@bluep.get('<int:id>')
@by_id(Operation)
def operation_detail(operation):
    return render_template('operation_description.html', operation=operation)