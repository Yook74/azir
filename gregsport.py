from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session

from application import AppConfig
from models import *

sess = Session(create_engine(AppConfig().SQLALCHEMY_DATABASE_URI))
all_serial_nos = set([device.serial_no for device in sess.query(Device)])

for device in sess.query(Device):
    for substring_length in range(len(device.serial_no)):
        short_name = device.serial_no[:substring_length]
        if not any(exg_sn.startswith(short_name) and exg_sn != device.serial_no for exg_sn in all_serial_nos):
            break

    device.unique_name_min_length = substring_length

    for other_device in sess.query(Device).filter(Device.serial_no.contains(device.serial_no[:substring_length])):
        if other_device.short_serial_no in device.serial_no[:substring_length]:
            other_device.unique_name_min_length = substring_length


sess.commit()
