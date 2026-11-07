import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')

app = Celery('bookstore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Налаштування Celery Beat (Періодичні задачі)
app.conf.beat_schedule = {
    'clear-expired-sessions-every-night': {
        'task': 'catalog.tasks.clear_sessions',
        'schedule': crontab(hour=0, minute=0),
    },
    'generate-daily-report': {
        'task': 'catalog.tasks.generate_report',
        'schedule': crontab(hour=8, minute=0),
    },
}