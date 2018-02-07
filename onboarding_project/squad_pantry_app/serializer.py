from django.utils import timezone
from rest_framework import serializers
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
        data = self.initial_data
        order = Order.objects.create(placed_by=validated_data['placed_by'], scheduled_time=data['scheduled_time'])

        for od_obj in validated_data['orderdishrelation_set']:
            order_dish = OrderDishRelation.objects.create(order_id=order.id, dish_id=od_obj['dish'].id,
                                                          quantity=od_obj['quantity'])
            order_dish.save()
        return order

    def update(self, instance, validated_data):
        print(validated_data)
        instance.status = instance.CANCELLED
        instance.closed_at = timezone.now()
        instance.save()
        return instance
