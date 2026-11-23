from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Admin, User


@admin.register(Admin)
class AdminUserAdmin(UserAdmin):
    """
    Django Admin registration for Admin model.
    Enables manually adding admin users via Django Admin with automatic password hashing.
    """
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('username',)


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Django Admin registration for custom User model (Task 2).
    Displays registered users with username, name, email, and registration timestamp.
    """
    list_display = ('username', 'name', 'email', 'created_at')
    search_fields = ('username', 'name', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
