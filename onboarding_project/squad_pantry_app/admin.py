from django import forms
from django.conf.urls import *
from django.forms import BaseInlineFormSet
from django.contrib import admin, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from squad_pantry_app.models import Dish, Order, OrderDishRelation, SquadUser, cancel_order


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
        exclude = ('dish', 'placed_by')


class OrderUserForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('status', 'dish', 'placed_by')


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDishInline, ]

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_kitchen_staff:
            return OrderKitchenForm
        else:
            return OrderUserForm

    def get_urls(self):
        return [
            url(
                r'^(.+)/change/cancel-order/$',
                self.admin_site.admin_view(self.cancel_order_view),
                name='cancel_order_view',
            ),
        ] + super(OrderAdmin, self).get_urls()

    def cancel_order_view(self, request, object_id, extra_context=None):
        order = Order.objects.get(pk=object_id)
        cancelled = cancel_order(order, request)
        if cancelled == 1:
            order.closed_at = timezone.now()
            self.message_user(request, 'Order cancelled', messages.SUCCESS)
        elif cancelled == -1:
            self.message_user(request, 'You did not place this order', messages.ERROR)
        else:
            self.message_user(request, 'Could not cancel, It has started processing', messages.ERROR)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    def save_model(self, request, obj, form, change):
        if not change:
            obj.placed_by = request.user
        form.save()


class UserAdmin(admin.ModelAdmin):
    model = SquadUser
    filter_horizontal = ('user_permissions', 'groups',)


admin.site.register(Dish)
admin.site.register(Order, OrderAdmin)
admin.site.register(SquadUser, UserAdmin)
