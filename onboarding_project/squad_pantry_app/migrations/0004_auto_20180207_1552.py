# Generated by Django 2.0 on 2018-02-07 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('squad_pantry_app', '0003_performancemetrics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performancemetrics',
            name='average_throughput',
            field=models.TimeField(editable=False),
        ),
        migrations.AlterField(
            model_name='performancemetrics',
            name='average_turnaround_time',
            field=models.TimeField(editable=False),
        ),
    ]