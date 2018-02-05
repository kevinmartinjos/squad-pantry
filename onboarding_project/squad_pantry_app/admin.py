from django import forms
from django.conf.urls import *
from django.forms import BaseInlineFormSet
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "dish":
            kwargs["queryset"] = Dish.objects.filter(is_available=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        try:
            if obj.placed_by:
                return self.readonly_fields + ('dish', 'quantity')
        except AttributeError:
            return self.readonly_fields


class DishAdmin(admin.ModelAdmin):
    list_display = ['dish_name', 'dish_type', 'is_available', 'prep_time_in_minutes']

    def has_add_permission(self, request):
        return request.user.is_kitchen_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_kitchen_staff


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderDishInline, ]
    exclude = ('placed_by', )
    readonly_fields = ('closed_at', )
    list_display = ('placed_by', 'status', 'created_at')

    def get_urls(self):
        return [
            url(
                r'^(.+)/change/cancel-order/$',
                self.admin_site.admin_view(self.cancel_order_view),
                name='cancel_order_view',
            ),
        ] + super(OrderAdmin, self).get_urls()

    def cancel_order_view(self, request, object_id, extra_context=None):

        try:
            order = Order.objects.get(pk=object_id)
        except Order.DoesNotExist:
            self.message_user(request, 'Mentioned Order ID does not exists', messages.ERROR)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/squad_pantry_app/order'))

        cancelled = order.cancel_order(request.user)
        if cancelled == order.CANCEL_SUCCESS:
            self.message_user(request, 'Order cancelled', messages.SUCCESS)
        elif cancelled == order.WRONG_USER:
            self.message_user(request, 'You did not place this order', messages.ERROR)
        elif cancelled == order.PROCESSING_ORDER:
            self.message_user(request, 'Could not cancel, The order is already being processed', messages.ERROR)
        elif cancelled == order.ORDER_CLOSED_ERROR:
            self.message_user(request, 'The order is already closed', messages.ERROR)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    def save_model(self, request, obj, form, change):
        if not change:
            obj.placed_by = request.user
        return super(OrderAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        user = request.user
        if not user.is_kitchen_staff or (user.is_kitchen_staff and obj.status in obj.CLOSED_ORDERS):
            return self.readonly_fields + ('status', )
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        if not request.user.is_kitchen_staff:
            return qs.filter(placed_by=request.user)
        return qs.filter()


class UserAdmin(admin.ModelAdmin):
    model = SquadUser
    filter_horizontal = ('user_permissions', 'groups',)


admin.site.register(Dish, DishAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(SquadUser, UserAdmin)
