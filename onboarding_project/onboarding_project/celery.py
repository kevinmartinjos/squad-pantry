from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onboarding_project.settings')
django.setup()

app = Celery('onboarding_project', broker='pyamqp://guest@localhost//', include=['onboarding_project.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')

from squad_pantry_app.models import ConfigurationSettings
schedule_interval = int(ConfigurationSettings.objects.get(constant='INTERVAL').value)


app.conf.beat_schedule = {
    'add-every-10-seconds': {
        'task': 'onboarding_project.tasks.calc_performance_metrics',
        'schedule': schedule_interval
    },
}
