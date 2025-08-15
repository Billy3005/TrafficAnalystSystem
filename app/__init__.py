import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

#creaty extensions at level fully
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Hàm Factory để tạo và cấu hình đối tượng ứng dụng Flask.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # make sure folders needed exist
    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['PROCESSED_FOLDER'])
    except OSError:
        pass

    # attached extension in app
    db.init_app(app)
    migrate.init_app(app, db)

    # registed Blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # create database if it don't exist
    with app.app_context():
        db.create_all()

    return app


from app import models
from app.main import routes