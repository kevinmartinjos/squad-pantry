from django.shortcuts import render
from django.views import View
from squad_pantry_app.models import Order, OrderDishRelation
from squad_pantry_app.serializer import OrderSerializer
from squad_pantry_app.permissions import IsUserWhoPlacedOrder
from rest_framework import permissions, viewsets


class OrderViewSet(viewsets.ModelViewSet):
    """
    Create Order, Cancel Order
    """
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsUserWhoPlacedOrder)

    def get_queryset(self):
        return Order.objects.filter(placed_by=self.request.user)


class MetricView(View):
    def get(self, request):

        return render(request, 'admin/metrics.html')