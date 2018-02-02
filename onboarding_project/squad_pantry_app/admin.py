from django.contrib import admin
from django.contrib.auth.models import User
from squad_pantry_app.models import Dish, Order, OrderDishRelation, SquadUser

class OrderInline(admin.TabularInline):
    model = OrderDishRelation

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderInline,
    ]

admin.site.register(Dish)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDishRelation)
admin.site.register(SquadUser)
