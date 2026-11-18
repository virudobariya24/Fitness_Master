from django.db import models
from django.conf import settings
from django.utils.text import slugify


class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-dumbbell')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Exercise Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(ExerciseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='exercises')
    description = models.TextField()
    target_muscle = models.CharField(max_length=100, help_text="e.g. Chest, Quads, Back, Core, Arms, Full Body")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')
    default_sets = models.PositiveIntegerField(default=3)
    default_reps = models.CharField(max_length=50, default='10-12 reps')
    duration = models.CharField(max_length=50, default='45 seconds')
    rest_time = models.CharField(max_length=50, default='60 seconds')
    instructions = models.TextField(help_text="Step by step execution guide")
    equipment_required = models.CharField(max_length=100, default='None (Bodyweight)')
    image = models.ImageField(upload_to='exercises/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.target_muscle})"


class WorkoutPlan(models.Model):
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    GOAL_CHOICES = [
        ('Weight Loss', 'Weight Loss'),
        ('Muscle Building', 'Muscle Building'),
        ('Full Body Workout', 'Full Body Workout'),
        ('Home Workout', 'Home Workout'),
        ('Gym Workout', 'Gym Workout'),
    ]

    title = models.CharField(max_length=150)
    category = models.ForeignKey(ExerciseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='workout_plans')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, default='Full Body Workout')
    duration_weeks = models.PositiveIntegerField(default=4, help_text="Duration in weeks")
    days_per_week = models.PositiveIntegerField(default=4, help_text="Sessions per week")
    estimated_calories_burn = models.PositiveIntegerField(default=350, help_text="Calories per session")
    description = models.TextField()
    image = models.ImageField(upload_to='workout_plans/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.difficulty_level})"


class WorkoutItem(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='items')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='plan_items')
    order = models.PositiveIntegerField(default=1)
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=50, default='12 reps')
    rest_seconds = models.PositiveIntegerField(default=60)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.workout_plan.title} - {self.exercise.name} (Step {self.order})"


class WorkoutLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_logs')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True)
    workout_name = models.CharField(max_length=150)
    completed_at = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    calories_burned = models.PositiveIntegerField(default=250)
    exercises_completed = models.PositiveIntegerField(default=5)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.workout_name} ({self.completed_at.strftime('%Y-%m-%d')})"
