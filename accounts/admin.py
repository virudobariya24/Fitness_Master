from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Admin


@admin.register(Admin)
class AdminUserAdmin(UserAdmin):
    """
    Django Admin registration for Admin model.
    Enables manually adding admin users via Django Admin with automatic password hashing.
    """
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('username',)
