from flask import Blueprint, jsonify, render_template, request

from models import db, Device

bluep = Blueprint('device', __name__, url_prefix='/device/')

@bluep.get('create')
def create_device_form():
    return render_template('device_intake.html')

@bluep.post('create')
def create_device_submit():
    values = request.values.to_dict()
    new_serial_no = values['serial-number']
    if (not new_serial_no):
        all_serial_nos = set([device.serial_no for device in Device.query])
        new_serial_no = 1
        while str(new_serial_no) in all_serial_nos:
            new_serial_no += 1
    new_device = Device(serial_no=new_serial_no)
    db.session.add(new_device)
    db.session.commit()
    return render_template('device_created.html', serial_no=new_serial_no)

@bluep.route('<int:device_id>/tasks')
def device_tasks(device_id: int):
    return jsonify([])