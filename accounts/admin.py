from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Admin, User, ContactMessage, PasswordResetOTP


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


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Django Admin registration for ContactMessage model.
    Allows administrators to view, filter, and mark user inquiries as read.
    """
    list_display = ('name', 'email', 'phone', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    """
    Django Admin registration for PasswordResetOTP model.
    Allows administrators to audit password reset attempts and OTP validity.
    """
    list_display = ('email', 'otp', 'created_at', 'is_verified', 'is_used')
    list_filter = ('is_verified', 'is_used', 'created_at')
    search_fields = ('email', 'otp')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


