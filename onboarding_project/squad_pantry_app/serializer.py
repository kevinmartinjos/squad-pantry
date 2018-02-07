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

        if 'schedule_time' in self.initial_data:
            scheduled_time = self.initial_data['schedule_time']
        else:
            scheduled_time = None

        logged_in_user = self._context['request']._user
        try:
            with transaction.atomic():
                order = Order.objects.create(placed_by=logged_in_user, scheduled_time=scheduled_time,
                                             created_at=timezone.now(), closed_at=None)

                order_dish_objects = [
                    OrderDishRelation(order_id=order.id, dish_id=od_obj['dish'].id, quantity=od_obj['quantity'])
                    for od_obj in validated_data['orderdishrelation_set']
                ]

                OrderDishRelation.objects.bulk_create(order_dish_objects)
        except DatabaseError:
            logging.getLogger(__name__).error('DatabaseError Exception caught!')
        else:
            return order

    def update(self, instance, validated_data):
        instance.status = instance.CANCELLED
        instance.closed_at = timezone.now()
        instance.save()
        return instance
