from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone


class SquadUser(AbstractUser):
    is_kitchen_staff = models.BooleanField(default=False)


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
        return "{0} ({1} Min)".format(self.dish_name, self.prep_time_in_minutes)


class Order(models.Model):
    CANCEL_SUCCESS = 100
    PROCESSING_ORDER = 200
    ORDER_CLOSED_ERROR = -200

    ORDER_PLACED = 0
    ACCEPTED = 1
    REJECTED = 2
    CANCELLED = 3
    PROCESSING = 4
    DELIVERED = 5

    CLOSED_ORDERS = [REJECTED, CANCELLED, DELIVERED]

    STATUS = (
        (ORDER_PLACED, 'Order Placed'),
        (REJECTED, 'Rejected'),
        (ACCEPTED, 'Accepted'),
        (CANCELLED, 'Cancelled'),
        (PROCESSING, 'Processing'),
        (DELIVERED, 'Delivered')
    )
    placed_by = models.ForeignKey(SquadUser, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS, default=ORDER_PLACED)
    dish = models.ManyToManyField(Dish, through='OrderDishRelation')
    scheduled_time = models.DateTimeField(
        blank=True, null=True,
        help_text='Schedule Your Order. Leave it blank for getting your order as soon as possible')
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.status in self.CLOSED_ORDERS:
            self.closed_at = timezone.now()
        super(Order, self).save(*args, **kwargs)

    def cancel_order(self):
        """
        Cancel the order placed by the user and give appropriate error messages on failure

        Keyword arguments:
        self - object of the class order
        """
        if self.status == self.ORDER_PLACED or self.status == self.ACCEPTED:
            self.status = self.CANCELLED
            self.closed_at = timezone.now()
            self.save()
            return self.CANCEL_SUCCESS
        elif self.status == self.PROCESSING:
            return self.PROCESSING_ORDER
        elif self.status in self.CLOSED_ORDERS:
            return self.ORDER_CLOSED_ERROR


class OrderDishRelation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ["order", "dish"]
