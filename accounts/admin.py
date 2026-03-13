from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'role', 'class_level', 'is_active')
    list_filter = ('role', 'class_level', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & School Info', {'fields': ('role', 'class_level', 'parent_link', 'avatar_color')}),
    )
