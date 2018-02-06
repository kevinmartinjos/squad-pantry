from django.test import TestCase
from django.utils import timezone
from squad_pantry_app.models import Order, SquadUser


class OrderTestCase(TestCase):
    def setUp(self):
        self.user1 = SquadUser.objects.create(username="prakhar", password="testdb1", is_superuser=True, is_kitchen_staff=False)
        self.user2 = SquadUser.objects.create(username="prakhar2", password="testdb2", is_superuser=True, is_kitchen_staff=False)

    def test_cancel_order(self):
        order_placed = Order.objects.create(placed_by=self.user1, status=0, created_at=timezone.now())
        rejected = Order.objects.create(placed_by=self.user2, status=2, created_at=timezone.now())
        cancelled = Order.objects.create(placed_by=self.user2, status=3, created_at=timezone.now())
        processing = Order.objects.create(placed_by=self.user1, status=4, created_at=timezone.now())

        self.assertEquals(order_placed.cancel_order(self.user1.id), Order.CANCEL_SUCCESS)
        self.assertEquals(rejected.cancel_order(self.user2.id), Order.ORDER_CLOSED_ERROR)
        self.assertEquals(cancelled.cancel_order(self.user2.id), Order.ORDER_CLOSED_ERROR)
        self.assertEquals(processing.cancel_order(self.user1.id), Order.PROCESSING_ORDER)
        self.assertEquals(order_placed.cancel_order(self.user2.id), Order.WRONG_USER)
