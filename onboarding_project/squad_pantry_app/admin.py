from django import forms
from django.forms import BaseInlineFormSet
from django.contrib import admin
from squad_pantry_app.models import Dish, Order, OrderDishRelation, SquadUser


class BaseOrderDishFormset(BaseInlineFormSet):
    def clean(self):
        filled_forms = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    filled_forms += 1
            except AttributeError:
                pass
        if filled_forms < 1:
            raise forms.ValidationError('Enter atleast One Dish')


class OrderDishInline(admin.StackedInline):
    model = OrderDishRelation
    formset = BaseOrderDishFormset
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDishInline,]


admin.site.register(Dish)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDishRelation)
admin.site.register(SquadUser)
