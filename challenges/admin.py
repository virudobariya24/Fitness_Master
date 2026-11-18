from django.contrib import admin
from .models import Challenge, ChallengeProgress, Achievement


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'duration_days', 'badge_name')
    list_filter = ('challenge_type',)
    search_fields = ('title', 'target_description')


@admin.register(ChallengeProgress)
class ChallengeProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'joined_date', 'days_completed', 'is_completed')
    list_filter = ('is_completed', 'joined_date')
    search_fields = ('user__username', 'challenge__title')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'unlocked_at')
    search_fields = ('user__username', 'title')
