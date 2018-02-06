from django.core.exceptions import ValidationError
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
    WRONG_USER = -100
    PROCESSING_ERROR = 200
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

    def clean(self):
        if self.scheduled_time is not None and self.scheduled_time < timezone.now():
            raise ValidationError('Past dates are not allowed')
        if self.status == self.CANCELLED and self.closed_at is None:
            raise ValidationError('As a SquadPantry you can not cancel an Order')
        if not self.pk:
            is_limit_exceeded = self.check_limit()
            if is_limit_exceeded:
                raise ValidationError('Due to heavy traffic, Squad Pantry can not accept your order.')

    def save(self, *args, **kwargs):
        if self.status in self.CLOSED_ORDERS:
            self.closed_at = timezone.now()
        super(Order, self).save(*args, **kwargs)

    @classmethod
    def check_limit(cls):
        """
        check if the number of open order has reached the limit"

        Keyword arguments:
        cls - class order
        """
        IS_EXCEEDED = True
        NOT_EXCEEDED = False

        limit = int(ConfigurationSettings.objects.get(constant='ORDER_LIMIT').value)
        open_orders = Order.objects.filter(status__in=[cls.ORDER_PLACED, cls.ACCEPTED, cls.PROCESSING]).count()

        if open_orders >= limit:
            return IS_EXCEEDED
        return NOT_EXCEEDED

    def cancel_order(self, user_id):
        """
        Cancel the order placed by the user and give appropriate error messages on failure

        Keyword arguments:
        self - object of the class order
        user_id - id of logged in user
        """
        if user_id != self.placed_by_id:
            return self.WRONG_USER
        elif self.status == self.ORDER_PLACED or self.status == self.ACCEPTED:
            self.status = self.CANCELLED
            self.closed_at = timezone.now()
            self.save()
            return self.CANCEL_SUCCESS
        elif self.status == self.PROCESSING:
            return self.PROCESSING_ERROR
        elif self.status in self.CLOSED_ORDERS:
            return self.ORDER_CLOSED_ERROR


class OrderDishRelation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ["order", "dish"]


class ConfigurationSettings(models.Model):
    constant = models.CharField(max_length=256, unique=True)
    value = models.CharField(max_length=256)

    def __str__(self):
        return self.constant
