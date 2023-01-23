from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import deferred

db = SQLAlchemy()


class Device(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    serial_no = db.Column(db.String(32), nullable=False, unique=True)
    status_id = db.Column(db.Integer(), db.ForeignKey('device_status.id'))

    status = db.relationship('DeviceStatus', backref='devices')
    tasks = db.relationship('Task', backref='device')
    properties = db.relationship('DeviceProperty', backref='device')

    @property
    def completed_tasks(self):
        return [task for task in self.tasks if task.completed]

    def __lt__(self, other):
        if other.status_id != self.status_id:
            return self.status_id < other.status_id
        else:
            return len(self.completed_tasks) / (len(self.tasks) or 0.1) < len(other.completed_tasks) / (len(other.tasks) or 0.1)


class DeviceStatus(db.Model):
    """Basically an enum"""
    id = db.Column(db.Integer(), primary_key=True)
    short_name = db.Column(db.String(16), nullable=False)
    long_name = db.Column(db.String(64), nullable=False)


class DeviceProperty(db.Model):
    """Like a spec or something"""
    id = db.Column(db.Integer(), primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    key = db.Column(db.String(16), nullable=True)
    value = db.Column(db.String(64), nullable=False)
    file_contents = deferred(db.Column(db.LargeBinary, nullable=True))


class Goal(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), nullable=False)


class Operation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    goal_id = db.Column(db.Integer(), db.ForeignKey('goal.id'))
    order = db.Column(db.Integer(), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text())

    goal = db.relationship('Goal', backref='operations')

    def __lt__(self, other) -> bool:
        return self.order < other.order


class Task(db.Model):
    device_id = db.Column(db.Integer(), db.ForeignKey('device.id'), primary_key=True)
    operation_id = db.Column(db.Integer(), db.ForeignKey('operation.id'), primary_key=True)
    completed = db.Column(db.Boolean(), default=False)

    operation = db.relationship('Operation', uselist=False, backref='tasks')

    def __lt__(self, other):
        return self.operation < other.operation
