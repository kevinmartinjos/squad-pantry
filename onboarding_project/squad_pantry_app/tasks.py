from celery import Celery
from celery.schedules import crontab

app = Celery('tasks', broker='pyamqp://guest@localhost//')
app.config_from_object('celeryconfig')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=11, minute=59),
        throughput.s(),
    )

    sender.add_periodic_task(
        crontab(hour=11, minute=59),
        turnaround_time.s(),
    )

@app.task
def throughput():
    return 4

@app.task
def turnaround_time():
    return 5
