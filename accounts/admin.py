from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_blocked', 'is_staff')
    list_filter = ('role', 'is_blocked', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Status', {'fields': ('role', 'is_blocked')}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fitness_goal', 'height', 'current_weight', 'target_weight', 'daily_water_goal')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('fitness_goal', 'activity_level', 'gender')
