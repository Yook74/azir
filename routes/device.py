from flask import Blueprint, render_template, request, redirect
from werkzeug.exceptions import NotFound

from models import *

from routes import by_id

bluep = Blueprint('device', __name__, url_prefix='/device/')


@bluep.get('create')
def create_device_form():
    context = dict(
        copy_device=None,
        goals=Goal.query.all()
    )

    if 'copy-id' in request.args:
        context['copy_device'] = Device.query.filter_by(id=request.args['copy-id']).first()

    return render_template('device_intake.html', **context)


@bluep.post('create')
def create_device_submit():
    values = request.values.to_dict()
    new_serial_no = values['serial-number'].upper()
    if not new_serial_no:
        all_serial_nos = set([device.serial_no for device in Device.query])
        new_serial_no = 1
        while str(new_serial_no) in all_serial_nos:
            new_serial_no += 1

    new_device = Device(serial_no=new_serial_no, status_id=1)
    db.session.add(new_device)

    if len(str(new_serial_no)) == 7:
        db.session.add(DeviceProperty(
            device=new_device, key='Dell Support Page',
            value=f'https://www.dell.com/support/home/en-us/product-support/servicetag/{new_serial_no}/overview'
        ))

    properties = request.form.getlist('property')
    for i in range(0, len(properties), 2):
        if properties[i].strip():  # if the key is something
            device_property = DeviceProperty(device=new_device, key=properties[i], value=properties[i + 1])
            db.session.add(device_property)

    for key in filter(lambda key_: key_.startswith('goal'), request.form):
        goal_id = int(key.replace('goal', ''))
        goal = Goal.query.filter_by(id=goal_id).first()
        for operation in goal.operations:
            db.session.add(Task(operation=operation, device=new_device))

    db.session.commit()

    return render_template('device_created.html', device=new_device)


@bluep.get('search')
def device_search_page():
    return render_template('device_search.html')


@bluep.post('search')
def device_search_result():
    device = Device.query.filter_by(serial_no=request.form['serialNo']).first()
    if device is None:
        raise NotFound()

    return redirect(f'{device.id}')


@bluep.get('<int:id>')
@by_id(Device)
def device_ticket(device):
    return render_template(
        'device_ticket.html',
        device=device, statuses=DeviceStatus.query.all(),
        operations=Operation.query.filter(Operation.id.not_in([task.operation_id for task in device.tasks])).all()
    )


@bluep.post('<int:id>/status')
@by_id(Device)
def update_status(device):
    device.status_id = int(request.form['statusId'])
    db.session.commit()

    return "updated"
