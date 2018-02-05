from django import forms
from django.conf.urls import *
from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
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

    def get_urls(self):
        urls = super(OrderAdmin, self).get_urls()
        urlpatterns = [
            url(
                r'^cancel/',
                self.admin_site.admin_view(self.cancel_order_view),
                name='cancel_order_view',
            ),
        ]
        return urlpatterns + urls

    def cancel_order_view(self, request):
        order = Order(request.POST)
        odr = OrderDishRelation(request.POST)
        print (odr)
        print (order)
        order.status = 3
        print(order.created_at)
        #order.save()
        return HttpResponse(
            "<h1>Cancelled</h1>"
        )


class UserAdmin(admin.ModelAdmin):
    model = SquadUser
    filter_horizontal = ('user_permissions', 'groups',)


admin.site.register(Dish)
admin.site.register(Order, OrderAdmin)
admin.site.register(SquadUser, UserAdmin)
