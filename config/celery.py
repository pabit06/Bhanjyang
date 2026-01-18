import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'fetch-nrb-exchange-rates-daily': {
        'task': 'services.fetch_nrb_exchange_rates_daily',
        'schedule': crontab(hour=6, minute=0),  # Run daily at 6:00 AM Nepal time
        'options': {'expires': 3600}  # Task expires after 1 hour if not executed
    },
    'publish-scheduled-content': {
        'task': 'home.tasks.publish_scheduled_content',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'expires': 300}  # Task expires after 5 minutes if not executed
    },
    'expire-content': {
        'task': 'home.tasks.expire_content',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes (same as publish)
        'options': {'expires': 300}  # Task expires after 5 minutes if not executed
    },
    'publish-scheduled-about-content': {
        'task': 'about.tasks.publish_scheduled_content',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'expires': 300}  # Task expires after 5 minutes if not executed
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
