from django.contrib import admin
from .models import ExerciseCategory, Exercise, WorkoutPlan, WorkoutItem, WorkoutLog


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class WorkoutItemInline(admin.TabularInline):
    model = WorkoutItem
    extra = 1


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty_level', 'goal', 'duration_weeks', 'is_featured')
    list_filter = ('difficulty_level', 'goal', 'is_featured')
    search_fields = ('title', 'description')
    inlines = [WorkoutItemInline]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'target_muscle', 'difficulty', 'equipment_required')
    list_filter = ('category', 'difficulty', 'target_muscle')
    search_fields = ('name', 'target_muscle', 'instructions')


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout_name', 'completed_at', 'duration_minutes', 'calories_burned')
    list_filter = ('completed_at',)
    search_fields = ('user__username', 'workout_name')
