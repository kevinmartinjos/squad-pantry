from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onboarding_project.settings')
django.setup()
app = Celery('onboarding_project', broker='pyamqp://guest@localhost//', include=['onboarding_project.tasks'])

app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     timezone='Asia/Calcutta',
# )

# app.config_from_object('celeryconfig')

#app.autodiscover_tasks()

app.conf.update(
    result_expires=10,
)

if __name__ == '__main__':
    app.start()
