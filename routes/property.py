from flask import Blueprint, request, redirect

from models import DeviceProperty, db

bluep = Blueprint('property', __name__, url_prefix='/property/')


@bluep.post('create')
def create_operation():
    device_id = int(request.form['deviceId'])

    db.session.add(DeviceProperty(device_id=device_id, key=request.form['key'], value=request.form['value']))
    db.session.commit()

    return redirect(f'/device/{device_id}')
