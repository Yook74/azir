from flask import Blueprint, render_template

from models import *

bluep = Blueprint('root', __name__, url_prefix='/')


@bluep.get('')
def home():
    return render_template('device_statuses.html', devices=Device.query.order_by(Device.status_id).all())
