from django.contrib import admin
from .models import DietPlan, Meal, FoodItem


class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 1


class MealInline(admin.StackedInline):
    model = Meal
    extra = 1


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'target_calories', 'target_protein', 'is_featured')
    list_filter = ('plan_type', 'is_featured')
    search_fields = ('name', 'description')
    inlines = [MealInline]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('name', 'diet_plan', 'meal_type', 'timing')
    list_filter = ('meal_type', 'diet_plan')
    inlines = [FoodItemInline]


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'meal', 'calories', 'protein', 'carbohydrates', 'fat')
    search_fields = ('name',)
