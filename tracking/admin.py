from django.contrib import admin
from .models import WeightLog, WaterLog


@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'recorded_date', 'notes')
    list_filter = ('recorded_date',)
    search_fields = ('user__username', 'notes')


@admin.register(WaterLog)
class WaterLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'glasses', 'amount_ml', 'goal_ml', 'percentage')
    list_filter = ('date',)
    search_fields = ('user__username',)
