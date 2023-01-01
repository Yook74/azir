from os import path

from flask import Flask

from routes import blueprints
from models import db, DeviceStatus


class AppConfig:
    use_sqlite = True
    reset_db = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        db_path = path.abspath('azir.db')
        return 'sqlite:///' + db_path


config = AppConfig()

application = Flask(__name__)
application.config.from_object(config)
db.init_app(application)

for blueprint in blueprints:
    application.register_blueprint(blueprint)

if config.reset_db:
    with application.app_context():
        db.drop_all()
        db.create_all()

        for short_name, long_name in (
            ('Backlog', 'Waiting for me to have time'), ('To-Do', 'Gong to work on it soon'),
            ('In Progress', 'I\'ve started working on it'),
            ('Outprocessing', 'Work is completed and I\'m trying to find a home for it'),
            ('Gone', 'Shipped or given out')
        ):
            db.session.add(DeviceStatus(short_name=short_name, long_name=long_name))

        db.session.commit()


if __name__ == '__main__':
    application.run()
