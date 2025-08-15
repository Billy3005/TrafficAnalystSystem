from app import create_app
from celery import Celery
from config import Config

#create a object celery, read directly config from class Config
celery = Celery(
    'video_tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=['tasks.video_tasks'] # index for celery know where is tasks
)

#create a flask app temporary provice context for tasks
flask_app = create_app()
celery.flask_app = flask_app

#overwrite task class default let it run inside context of flask
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with celery.flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask