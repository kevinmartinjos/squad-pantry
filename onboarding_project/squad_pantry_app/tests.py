from django.test import TestCase
from django.utils import timezone
from squad_pantry_app.models import Order, SquadUser, ConfigurationSettings, PerformanceMetrics


class OrderTestCase(TestCase):
    def setUp(self):
        self.user1 = SquadUser.objects.create(username="prakhar", password="testdb1",
                                              is_superuser=True, is_kitchen_staff=False)
        self.user2 = SquadUser.objects.create(username="prakhar2", password="testdb2",
                                              is_superuser=True, is_kitchen_staff=False)

    def test_cancel_order(self):
        order_placed = Order.objects.create(placed_by=self.user1, status=Order.ORDER_PLACED, created_at=timezone.now())
        rejected = Order.objects.create(placed_by=self.user2, status=Order.REJECTED, created_at=timezone.now())
        cancelled = Order.objects.create(placed_by=self.user2, status=Order.CANCELLED, created_at=timezone.now())
        processing = Order.objects.create(placed_by=self.user1, status=Order.PROCESSING, created_at=timezone.now())

        self.assertEquals(order_placed.cancel_order(self.user1.id), Order.CANCEL_SUCCESS)
        self.assertEquals(rejected.cancel_order(self.user2.id), Order.ORDER_CLOSED_ERROR)
        self.assertEquals(cancelled.cancel_order(self.user2.id), Order.ORDER_CLOSED_ERROR)
        self.assertEquals(processing.cancel_order(self.user1.id), Order.PROCESSING_ERROR)
        self.assertEquals(order_placed.cancel_order(self.user2.id), Order.WRONG_USER)

    def test_check_limit(self):
        ConfigurationSettings.objects.create(constant='ORDER_LIMIT', value=2)
        Order.objects.create(placed_by=self.user1, status=0, created_at=timezone.now())

        self.assertEquals(Order.check_limit(), False)

        Order.objects.create(placed_by=self.user1, status=0, created_at=timezone.now())

        self.assertEquals(Order.check_limit(), True)

    def test_calculate_avg_metrics(self):
        Order.objects.create(placed_by=self.user1, status=Order.DELIVERED, created_at=timezone.now(),
                             closed_at=timezone.now())
        Order.objects.create(placed_by=self.user1, status=Order.DELIVERED, created_at=timezone.now(),
                             closed_at=timezone.now())

        self.assertEquals(PerformanceMetrics.calculate_avg_performance_metrics(), 2, 0)
        self.assertEquals(PerformanceMetrics.calculate_avg_performance_metrics(), 0, 0)
