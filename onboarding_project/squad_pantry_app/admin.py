from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.forms import BaseInlineFormSet, fields
from django.contrib.auth.admin import UserAdmin
from squad_pantry_app.models import Dish, Order, OrderDishRelation, SquadUser


class BaseOrderDishFormset(BaseInlineFormSet):
    def clean(self):
        try:
            filled_form = [form for form in self.forms if form.cleaned_data]
        except AttributeError:
            # if a subform is invalid Django explicity raises
            # an AttributeError for cleaned_data
            pass
        else:
            if len(filled_form) < 1:
                raise forms.ValidationError('Enter at least One Dish')


class OrderDishInline(admin.StackedInline):
    model = OrderDishRelation
    formset = BaseOrderDishFormset
    extra = 1


class OrderKitchenForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('dish', )


class OrderUserForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('status', 'dish', )


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDishInline, ]

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_kitchen_staff:
            return OrderKitchenForm
        else:
            return OrderUserForm


class UserAdmin(admin.ModelAdmin):
    model = SquadUser
    filter_horizontal = ('user_permissions', 'groups',)


admin.site.register(Dish)
admin.site.register(Order, OrderAdmin)
admin.site.register(SquadUser, UserAdmin)
