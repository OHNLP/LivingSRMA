
from celery import Celery
from lnma import create_app

def make_celery(app_name):
    redis_uri = 'redis://localhost:6379'
    celery = Celery(
        app_name,
        backend=redis_uri,
        broker=redis_uri
    )
    return celery

def init_celery(celery_app, flask_app):
    celery_app.conf.update(flask_app.config["CELERY_CONFIG"])

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask

celery_app = make_celery('LNMA Celery Worker')
flask_app = create_app()
flask_app.app_context().push()
init_celery(celery_app, flask_app)