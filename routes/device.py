from io import BytesIO, StringIO
import csv

from flask import Blueprint, render_template, request, redirect, send_file
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
    all_serial_nos = set([device.serial_no for device in Device.query])

    if not new_serial_no:
        new_serial_no = 1
        while str(new_serial_no) in all_serial_nos:
            new_serial_no += 1

    existing_device = db.session.query(Device).filter_by(serial_no=new_serial_no).first()
    if existing_device:
        return redirect(f'/device/{existing_device.id}')

    new_serial_no = str(new_serial_no)
    for substring_length in range(len(new_serial_no)):
        short_name = new_serial_no[:substring_length]
        if not any(exg_sn.startswith(short_name) for exg_sn in all_serial_nos):
            break

    for other_device in Device.query.filter(Device.serial_no.contains(new_serial_no[:substring_length])):
        if other_device.short_serial_no in new_serial_no[:substring_length]:
            other_device.unique_name_min_length = substring_length

    new_device = Device(
        serial_no=new_serial_no, unique_name_min_length=substring_length, status_id=2, recipient=values['recipient']
    )
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
    device = Device.query.filter(Device.serial_no.contains(request.form['serialNo'].upper())).first()
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


@bluep.post('<int:id>/recipient')
@by_id(Device)
def update_recipient(device):
    device.recipient = request.form['recipient']
    db.session.commit()

    return "updated"


@bluep.get('<int:id>/csv')
@by_id(Device)
def get_csv(device):
    file_handle = StringIO()
    writer = csv.writer(file_handle)
    writer.writerow(['Fields', 'Values', 'Notes'])

    def get_property_value(property_names, default):
        property_names = list(map(str.lower, property_names))

        for property in device.properties:
            if property.key.lower() in property_names:
                return property.value
        else:
            return default

    for names in [('Permission to thank?',), ('In The Possession of', ), ('Brand',), ('Model',), ('Also Marketed As',),
                  ('Serial Number',), ('RAM', 'Memory'), ('CPU', 'Processor'), ('Current Drive', 'SSD', 'Drive'), ('Battery Cycle Count',),
                  ('Battery Condition', 'Battery'), ('Operating System Installed', 'OS'), ('Keyboard Language',)]:

        if names[0] == 'Serial Number':
            default = device.serial_no
        elif names[0] == 'Permission to thank?':
            default = 'yes'
        elif names[0] == 'In The Possession of':
            default = 'USER HERE'
        elif names[0] == 'Brand':
            if device.serial_no.startswith('5CG'):
                default = 'HP'
            elif len(device.serial_no) == 7:
                default = 'Dell'
            else:
                default = None
        elif names[0] == 'Keyboard Language':
            default = 'English (US)'
        else:
            default = None

        writer.writerow([names[0], get_property_value(names, default)])

    file_handle.seek(0)
    return send_file(
        BytesIO(file_handle.read().encode('utf-8')),
        download_name=device.serial_no + '.csv'
    )