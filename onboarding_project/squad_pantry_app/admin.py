from django import forms
from django.conf.urls import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.forms import BaseInlineFormSet
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from squad_pantry_app.models import Dish, Order, OrderDishRelation, SquadUser, ConfigurationSettings, PerformanceMetrics


class BaseOrderDishFormset(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(BaseOrderDishFormset, self).__init__(*args, **kwargs)
        self.can_delete = False

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
        return super(OrderDishInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        else:
            return self.readonly_fields + ('dish', 'quantity')


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
    list_filter = ('status', )
    list_display = ('placed_by', 'status', 'created_at', 'scheduled_time')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return not request.user.is_kitchen_staff

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
        else:
            cancelled = order.cancel_order(request.user.id)
            if cancelled == order.CANCEL_SUCCESS:
                self.message_user(request, 'Order cancelled', messages.SUCCESS)
            elif cancelled == order.WRONG_USER:
                self.message_user(request, 'You do not have permission to cancel this order', messages.ERROR)
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
        kitchen_staff = request.user.is_kitchen_staff
        make_readonly_status = kitchen_staff and obj.status in obj.CLOSED_ORDERS and obj.closed_at is not None
        # obj.closed_at should not be None so that SquadPantry should not be able to cancel the order.
        is_closed_order = not kitchen_staff or make_readonly_status
        if obj is None and is_closed_order:
            return self.readonly_fields + ('status', )
        elif obj is None and not is_closed_order:
            return self.readonly_fields
        elif is_closed_order:
            return self.readonly_fields + ('status', 'scheduled_time')
        else:
            return self.readonly_fields + ('scheduled_time', )

    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        if not request.user.is_kitchen_staff:
            return qs.filter(placed_by=request.user)
        return qs


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    password_confirmation = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput())

    class Meta:
        model = SquadUser
        fields = ('email', 'is_kitchen_staff')

    def clean_password_create(self):
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Passwords don't match")
        return password_confirmation

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Password",
                                         help_text="Raw passwords are not stored, so there is no way to see " 
                                                   "this user's password, but you can change the password " 
                                                   "using <a href=\"../password/\">this form</a>.")

    class Meta:
        model = SquadUser
        exclude = ()

    def clean_password(self):
        return self.initial["password"]


class SquadUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'is_superuser', 'is_kitchen_staff')
    list_filter = ('is_superuser', 'is_kitchen_staff')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_kitchen_staff', 'is_staff',
                                    'user_permissions', 'groups')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'password_confirmation')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('user_permissions', 'groups',)


class ConfigurationSettingsAdmin(admin.ModelAdmin):
    list_display = ('constant', 'value', )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.is_kitchen_staff


# class PerformanceMetricAdmin(admin.ModelAdmin):
#     list_display = ('created_at', 'average_throughput', 'average_turnaround_time', )
#     readonly_fields = ('average_throughput', 'average_turnaround_time', )


admin.site.register(Dish, DishAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(SquadUser, SquadUserAdmin)
#admin.site.register(PerformanceMetrics, PerformanceMetricAdmin)
admin.site.register(ConfigurationSettings, ConfigurationSettingsAdmin)
