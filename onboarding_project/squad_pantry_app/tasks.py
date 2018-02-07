from celery import Celery
from celery.schedules import crontab
from onboarding_project.squad_pantry_app.models import PerformanceMetrics

app = Celery('tasks', broker='pyamqp://guest@localhost//')
app.config_from_object('celeryconfig')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=11, minute=59),
        get_avg_performance_metrics.s(),
    )

@app.task
def get_avg_performance_metrics():
    throughput = PerformanceMetrics.calculate_throughput()
    return throughput
