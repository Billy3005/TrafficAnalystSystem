import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    function to create and config object flask ap
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['PROCESSED_FOLDER'])
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)

    # make sure ap and extensions had created fully
    # before routes is defined and attached 
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()

    return app