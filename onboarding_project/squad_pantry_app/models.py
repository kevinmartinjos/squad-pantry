from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.


class Dish(models.Model):
    dish_name = models.CharField(max_length=256, unique=True)
    DISH_TYPE = (
        ('NV', 'Non-Vegetarian'),
        ('V', 'Vegetarian'),
        ('E', 'Contains Egg'),
    )
    dish_type = models.CharField(max_length=2, choices=DISH_TYPE, default=DISH_TYPE[0][0])
    is_available = models.BooleanField(default=False, blank=False)
    estimated_preparation_time_in_minutes = models.IntegerField(validators=[MinValueValidator(1)])


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS = (
        ('OP', 'Order Placed'),
        ('REJ', 'Rejected'),
        ('ACC', 'Accepted'),
        ('CAN', 'Cancelled'),
        ('PROC', 'Processing'),
        ('DEL', 'Delivered')
    )
    status = models.CharField(max_length=4, choices=STATUS, default=STATUS[0][0])
    scheduled_time = models.DateTimeField(blank=True, null=True)
    order_placed_at = models.DateTimeField(default=datetime.now())
    order_closed_at = models.DateTimeField(blank=True, null=True)


class OrderDishRelation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ["order", "dish"]


class SquadUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_kitchen_staff = models.BooleanField(default=False)
