from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Device(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    serial_no = db.Column(db.String(32), nullable=False)
    status_id = db.Column(db.Integer(), db.ForeignKey('device_status.id'))

    status = db.relationship('DeviceStatus', backref='devices')
    tasks = db.relationship('Task', backref='device')


class DeviceStatus(db.Model):
    """Basically an enum"""
    id = db.Column(db.Integer(), primary_key=True)
    short_name = db.Column(db.String(16), nullable=False)
    long_name = db.Column(db.String(64), nullable=False)


class Operation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text())


class Task(db.Model):
    device_id = db.Column(db.Integer(), db.ForeignKey('device.id'), primary_key=True)
    operation_id = db.Column(db.Integer(), db.ForeignKey('operation.id'), primary_key=True)
    completed = db.Column(db.Boolean(), default=False)

    operation = db.relationship('Operation', uselist=False, backref='tasks')
