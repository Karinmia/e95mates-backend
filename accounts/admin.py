from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'full_name',)
    search_fields = ('full_name', 'phone')
    list_filter = ['is_staff', 'is_active']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'phone',)}
         ),
    )
    fieldsets = (
        ('Personal info', {'fields': ('full_name', 'phone',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ('phone',)


admin.site.register(User, CustomUserAdmin)
