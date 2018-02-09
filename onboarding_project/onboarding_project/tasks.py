from onboarding_project.celery import app
from squad_pantry_app.models import PerformanceMetrics


@app.task
def calc_performance_metrics():
    PerformanceMetrics.create_avg_performance_metrics()
