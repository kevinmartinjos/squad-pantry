from django.db import models
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
    dish_type = models.IntegerField(choices=DISH_TYPE)
    is_available = models.BooleanField(default=False, help_text="Check if the dish is available")
    prep_time_in_minutes = models.IntegerField(
        validators=[MinValueValidator(1)], help_text='Time Taken to Prepare the Dish')

    def __str__(self):
        return self.dish_name


class Order(models.Model):
    ORDER_PLACED = 0
    REJECTED = 1
    ACCEPTED = 2
    CANCELLED = 3
    PROCESSING = 4
    DELIVERY = 5
    STATUS = (
        (ORDER_PLACED, 'Order Placed'),
        (REJECTED, 'Rejected'),
        (ACCEPTED, 'Accepted'),
        (CANCELLED, 'Cancelled'),
        (PROCESSING, 'Processing'),
        (DELIVERY, 'Delivered')
    )
    status = models.IntegerField(choices=STATUS, default=ORDER_PLACED)
    dish = models.ManyToManyField(Dish, through='OrderDishRelation')
    scheduled_time = models.DateTimeField(
        blank=True, null=True,
        help_text='Schedule Your Order. Leave it blank for getting your order as soon as possible')
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

    def __str__(self):
        return str(self.user)
