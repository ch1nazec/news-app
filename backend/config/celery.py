import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Загрузка всех задач из всех Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self}')