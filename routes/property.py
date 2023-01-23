from io import BytesIO

from flask import Blueprint, request, redirect, send_file

from models import DeviceProperty, db
from routes import by_id

bluep = Blueprint('property', __name__, url_prefix='/property/')


@bluep.post('create')
def create_operation():
    device_id = int(request.form['deviceId'])

    db.session.add(DeviceProperty(
        device_id=device_id, key=request.form['key'],
        value=request.files['file'].filename if request.files and not request.form['value'] else request.form['value'],
        file_contents=request.files['file'].read() if request.files else None
    ))
    db.session.commit()

    return redirect(f'/device/{device_id}')


@bluep.get('/<int:id>/file')
@by_id(DeviceProperty)
def get_file(dev_prop):
    return send_file(BytesIO(dev_prop.file_contents), download_name=dev_prop.value)
