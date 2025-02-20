from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group

admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'order_number', 'is_confirmed', 'is_staff', 'is_denied')
    list_filter = ('username', 'email', 'number', 'order_number', 'is_staff', 'is_denied')
    search_fields = ['username', 'email', 'number', 'order_number', 'login']

    def get_fields(self, request, obj=None):
        if obj:
            if obj.is_staff:
                return ('username', 'avatar', 'login', 'email', 'password', 'is_staff', 'is_active')
            else:
                return ('avatar', 'username', 'login', 'email', 'password', 'number', 'address',
                        'apartment_number', 'order_number', 'is_confirmed', 'code', 'is_active', 'is_denied')
        return super().get_fields(request, obj)

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            if obj.is_superuser:
                obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
