# Generated by Django 2.0 on 2018-02-02 12:57

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dish_name', models.CharField(max_length=256, unique=True)),
                ('dish_type', models.IntegerField(choices=[(0, 'Non-Vegetarian'), (1, 'Vegetarian'), (2, 'Contains Egg')], default=0)),
                ('is_available', models.BooleanField(default=False)),
                ('prep_time_in_minutes', models.IntegerField(help_text='Time Taken to Prepare the Dish', validators=[django.core.validators.MinValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Order Placed'), (1, 'Rejected'), (2, 'Accepted'), (3, 'Cancelled'), (4, 'Processing'), (5, 'Delivered')], default=0)),
                ('scheduled_time', models.DateTimeField(blank=True, help_text='Schedule Your Order. Leave it blank for instant delivery', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderDishRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='squad_pantry_app.Dish')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='squad_pantry_app.Order')),
            ],
        ),
        migrations.CreateModel(
            name='SquadUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_kitchen_staff', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='orderdishrelation',
            unique_together={('order', 'dish')},
        ),
    ]