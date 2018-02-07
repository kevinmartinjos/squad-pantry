import logging
from django.utils import timezone
from rest_framework import serializers
from django.db import transaction, DatabaseError
from rest_framework.exceptions import ValidationError
from squad_pantry_app.models import Order, OrderDishRelation


class OrderDishRelationSerializer(serializers.ModelSerializer):

    name = serializers.ReadOnlyField(source='dish.dish_name')

    class Meta:
        model = OrderDishRelation
        exclude = ('id', 'order', )


class OrderSerializer(serializers.ModelSerializer):
    dishes = OrderDishRelationSerializer(source='orderdishrelation_set', many=True)
    placed_by = serializers.ReadOnlyField(source='placed_by.username')

    class Meta:
        model = Order
        exclude = ('dish', )
        read_only_fields = ('status', 'scheduled_time', 'closed_at')

    def validate(self, attrs):
        if len(attrs['orderdishrelation_set']) < 1:
            raise ValidationError('Order at least one dish')
        return attrs

    def create(self, validated_data):
        scheduled_time = self.initial_data.get('scheduled_time')
        logged_in_user = self._context['request']._user
        order = Order.place_order(scheduled_time, logged_in_user, validated_data)
        return order

    def update(self, instance, validated_data):
        instance.status = instance.CANCELLED
        instance.closed_at = timezone.now()
        instance.save()
        return instance
