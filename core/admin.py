from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Bus, Route, Trip, LocationPing

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Bus Tracking Info', {
            'fields': ('role', 'route'),
        }),
    )

    list_display = ('username', 'role', 'route', 'is_staff')
    list_filter = ('role', 'route')

admin.site.register(Bus)
admin.site.register(Route)
admin.site.register(Trip)
admin.site.register(LocationPing)
