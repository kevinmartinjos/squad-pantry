import logging
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models, transaction, DatabaseError


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

    class Meta:
        indexes = [
            models.Index(fields=['created_at'], name='created_at_idx')
        ]

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
        if self.status in self.CLOSED_ORDERS and self.closed_at is None:
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

    @classmethod
    def place_order(cls, scheduled_time, logged_in_user, order_dish_relation_set):
        try:
            with transaction.atomic():
                order = Order.objects.create(placed_by=logged_in_user, scheduled_time=scheduled_time,
                                             created_at=timezone.now(), closed_at=None)

                order_dish_objects = [
                    OrderDishRelation(order_id=order.id, dish_id=od_obj['dish'].id, quantity=od_obj['quantity'])
                    for od_obj in order_dish_relation_set
                ]

                OrderDishRelation.objects.bulk_create(order_dish_objects)
        except DatabaseError:
            logging.exception("message")
        else:
            return order


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


class PerformanceMetrics(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, unique=True)
    average_throughput = models.IntegerField(editable=False)
    average_turnaround_time = models.DurationField(editable=False)

    @classmethod
    def calculate_avg_performance_metrics(cls):
        """
        Calculate the performance metrics as per scheduled, from last entered entry in database to now.

        """
        if PerformanceMetrics.objects.all().count() < 1:
            completed_orders_curr_range = Order.objects.filter(
                status=Order.DELIVERED
            )
        else:
            start_date_time = PerformanceMetrics.objects.latest('id').created_at
            completed_orders_curr_range = Order.objects.filter(
                status=Order.DELIVERED,
                created_at__range=(start_date_time, timezone.now())
            )
        throughput = len(completed_orders_curr_range)

        if throughput == 0:
            return timedelta(seconds=0), 0

        total_turnaround_time = 0
        for obj in completed_orders_curr_range:
            total_turnaround_time += (obj.closed_at - obj.created_at).total_seconds()

        average_turnaround_time = total_turnaround_time/throughput
        return timedelta(seconds=average_turnaround_time), throughput

    @classmethod
    def create_avg_performance_metrics(cls):
        """
        Insert the calculated metrics into Database

        """
        turnaround_time, throughput = PerformanceMetrics.calculate_avg_performance_metrics()
        PerformanceMetrics.objects.create(average_throughput=throughput, average_turnaround_time=turnaround_time)

    @classmethod
    def get_metrics_data(cls, start_date, end_date):
        """
        Get average metrics for the given interval

        Keyword arguments:
        start_date - Metrics needed from this date
        end_date - Metrics needed till this date
        """
        metrics = PerformanceMetrics.objects.filter(created_at__range=(start_date, end_date))
        num_metric_records = len(metrics)
        total_throughput = metrics.aggregate(Sum('average_throughput'))['average_throughput__sum']
        total_turnaround_time = 0
        for obj in metrics:
            total_turnaround_time += obj.average_turnaround_time.total_seconds()

        if total_throughput == 0:
            return 0, 0
        throughput = total_throughput/num_metric_records
        turnaround_time = total_turnaround_time/num_metric_records

        return throughput, str(timedelta(seconds=turnaround_time))

    def __str__(self):
        return str(self.created_at)
