from django.test import TestCase
from django.utils import timezone
from squad_pantry_app.models import Order, SquadUser


class OrderTestCase(TestCase):
    def setUp(self):
        SquadUser.objects.create(username="prakhar", password="testdb1", is_superuser=True, is_kitchen_staff=False)
        SquadUser.objects.create(username="prakhar2", password="testdb2", is_superuser=True, is_kitchen_staff=False)
        user1 = SquadUser.objects.get(pk=1)
        user2 = SquadUser.objects.get(pk=2)
        Order.objects.create(placed_by=user1, status=0, created_at=timezone.now())
        Order.objects.create(placed_by=user2, status=2, created_at=timezone.now())
        Order.objects.create(placed_by=user2, status=3, created_at=timezone.now())
        Order.objects.create(placed_by=user1, status=4, created_at=timezone.now())

    def test_cancel_order(self):
        order_placed = Order.objects.get(status=0)
        rejected = Order.objects.get(status=2)
        cancelled = Order.objects.get(status=3)
        processing = Order.objects.get(status=4)
        self.assertEquals(order_placed.cancel_order(), Order.CANCEL_SUCCESS)
        self.assertEquals(rejected.cancel_order(), Order.ORDER_CLOSED_ERROR)
        self.assertEquals(cancelled.cancel_order(), Order.ORDER_CLOSED_ERROR)
        self.assertEquals(processing.cancel_order(), Order.PROCESSING_ORDER)
