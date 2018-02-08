from celery import Celery
from onboarding_project.celery import app
from celery.schedules import crontab
from squad_pantry_app.models import PerformanceMetrics

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(
    #     crontab(hour=11, minute=59),
    #     set_avg_performance_metrics.s(),
    # )
    sender.add_periodic_task(10.0, set_avg_performance_metrics.s(), name='add every 10')


@app.task
def set_avg_performance_metrics():
    PerformanceMetrics.create_avg_performance_metrics()
