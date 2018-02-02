from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Dish(models.Model):
    dish_name = models.CharField(max_length=256, unique=True)
    NON_VEG = 0
    VEG = 1
    EGG = 2
    DISH_TYPE = (
        (NON_VEG, 'Non-Vegetarian'),
        (VEG, 'Vegetarian'),
        (EGG, 'Contains Egg'),
    )
    dish_type = models.IntegerField(choices=DISH_TYPE, default=NON_VEG)
    is_available = models.BooleanField(default=False)
    prep_time_in_minutes = models.IntegerField(validators=[MinValueValidator(1)], help_text='Time Taken to Prepare the Dish')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    OP = 0
    REJ = 1
    ACC = 2
    CAN = 3
    PROC = 4
    DEL = 5
    STATUS = (
        (OP, 'Order Placed'),
        (REJ, 'Rejected'),
        (ACC, 'Accepted'),
        (CAN, 'Cancelled'),
        (PROC, 'Processing'),
        (DEL, 'Delivered')
    )
    status = models.IntegerField(choices=STATUS, default=OP)
    scheduled_time = models.DateTimeField(blank=True, null=True, help_text='Schedule Your Order. Leave it blank for instant delivery')
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)


class OrderDishRelation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ["order", "dish"]


class SquadUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_kitchen_staff = models.BooleanField(default=False)
