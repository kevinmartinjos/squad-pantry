from django.contrib import admin
from squad_pantry_app.models import Dish, Order, OrderDishRelation, SquadUser

admin.site.register(Dish)
admin.site.register(Order)
admin.site.register(OrderDishRelation)
admin.site.register(SquadUser)
