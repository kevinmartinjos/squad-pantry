from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from squad_pantry_app.models import Dish, Order, OrderDishRelation, SquadUser

# class OrderDishRelationForm(forms.ModelForm):
#     class Meta:
#         model = OrderDishRelation
#         exclude = ()
#
#     def clean(self):
#         #dish_list = self.cleaned_data.get('dish')
#         print (self.data)
#         return self.cleaned_data

class OrderDishInline(admin.TabularInline):
    model = OrderDishRelation

class OrderAdmin(admin.ModelAdmin):
    # form = OrderDishRelationForm
    inlines = [
        OrderDishInline
    ]

admin.site.register(Dish)
admin.site.register(Order, OrderAdmin)
#admin.site.register(OrderDishRelation)
admin.site.register(SquadUser)
