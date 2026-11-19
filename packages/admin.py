from django.contrib import admin
from .models import Packages


@admin.register(Packages)
class PackagesAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'price', 'duration', 'access_hours',
        'classes_per_week', 'membership_duration',
        'drinking_package', 'personal_instructor'
    )
    search_fields = ('title', 'instruments', 'membership_duration')
    list_filter = ('membership_duration',)
    ordering = ('price',)
