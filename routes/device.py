from flask import Blueprint, jsonify

bluep = Blueprint('device', __name__, url_prefix='/device/')


@bluep.route('<int:device_id>/tasks')
def device_tasks(device_id: int):
    return jsonify([])