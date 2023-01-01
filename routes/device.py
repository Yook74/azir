from flask import Blueprint, render_template, request, redirect
from werkzeug.exceptions import NotFound

from models import *

from routes import by_id

bluep = Blueprint('device', __name__, url_prefix='/device/')


@bluep.get('create')
def create_device_form():
    return render_template('device_intake.html')


@bluep.post('create')
def create_device_submit():
    values = request.values.to_dict()
    new_serial_no = values['serial-number']
    if not new_serial_no:
        all_serial_nos = set([device.serial_no for device in Device.query])
        new_serial_no = 1
        while str(new_serial_no) in all_serial_nos:
            new_serial_no += 1

    new_device = Device(serial_no=new_serial_no, status_id=0)
    db.session.add(new_device)

    if len(new_serial_no) == 7:
        db.session.add(DeviceProperty(
            device=new_device, key='Dell Support Page',
            value=f'https://www.dell.com/support/home/en-us/product-support/servicetag/{new_serial_no}/overview'
        ))

    db.session.commit()
    return render_template('device_created.html', serial_no=new_serial_no)


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
        device=device, statuses=DeviceStatus.query.all(), operations=Operation.query.all()
    )
