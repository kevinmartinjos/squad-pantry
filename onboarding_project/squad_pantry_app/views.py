from squad_pantry_app.models import Order, OrderDishRelation
from squad_pantry_app.serializer import OrderSerializer
from squad_pantry_app.permissions import IsUser
from rest_framework import permissions, viewsets
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics


class OrderViewSet(viewsets.ModelViewSet):
    """
    Create Order, Cancel Order
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsUser)
