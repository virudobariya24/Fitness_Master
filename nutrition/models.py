from django.db import models


class DietPlan(models.Model):
    PLAN_TYPES = [
        ('Weight Loss Diet', 'Weight Loss Diet'),
        ('Muscle Gain Diet', 'Muscle Gain Diet'),
        ('Maintenance Diet', 'Maintenance Diet'),
        ('High Protein Fitness', 'High Protein Fitness'),
        ('Clean Eating & Vitality', 'Clean Eating & Vitality'),
    ]

    name = models.CharField(max_length=150)
    plan_type = models.CharField(max_length=50, choices=PLAN_TYPES, default='Maintenance Diet')
    target_calories = models.PositiveIntegerField(default=2000, help_text="Total daily calories")
    target_protein = models.PositiveIntegerField(default=140, help_text="Target protein (g)")
    target_carbs = models.PositiveIntegerField(default=220, help_text="Target carbohydrates (g)")
    target_fat = models.PositiveIntegerField(default=60, help_text="Target fat (g)")
    description = models.TextField()
    image = models.ImageField(upload_to='diet_plans/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.plan_type})"


class Meal(models.Model):
    MEAL_TYPES = [
        ('Breakfast', 'Breakfast'),
        ('Morning Snack', 'Morning Snack'),
        ('Lunch', 'Lunch'),
        ('Evening Snack', 'Evening Snack'),
        ('Dinner', 'Dinner'),
    ]

    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(max_length=30, choices=MEAL_TYPES, default='Breakfast')
    name = models.CharField(max_length=150)
    timing = models.CharField(max_length=50, default='08:00 AM')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.diet_plan.name} - {self.meal_type}: {self.name}"

    @property
    def total_calories(self):
        return sum(item.calories for item in self.food_items.all())

    @property
    def total_protein(self):
        return sum(item.protein for item in self.food_items.all())


class FoodItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='food_items')
    name = models.CharField(max_length=150)
    serving_size = models.CharField(max_length=100, default='1 portion / 150g')
    calories = models.PositiveIntegerField(default=150)
    protein = models.DecimalField(max_digits=5, decimal_places=1, default=10.0, help_text="Protein in grams")
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=1, default=20.0, help_text="Carbohydrates in grams")
    fat = models.DecimalField(max_digits=5, decimal_places=1, default=5.0, help_text="Fat in grams")
    image = models.ImageField(upload_to='food_items/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.calories} kcal)"
