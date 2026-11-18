from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('USER', 'User'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    is_blocked = models.BooleanField(
        default=False,
        help_text="Designates whether this user is blocked from logging in."
    )

    def is_admin_user(self):
        return self.role == 'ADMIN' or self.is_superuser or self.is_staff

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    GOAL_CHOICES = [
        ('', 'Select Fitness Goal'),
        ('weight_loss', 'Weight Loss'),
        ('muscle_building', 'Muscle Building'),
        ('keep_fit', 'General Fitness & Health'),
        ('endurance', 'Endurance & Cardio'),
        ('full_body', 'Full Body Transformation'),
    ]

    ACTIVITY_CHOICES = [
        ('', 'Select Activity Level'),
        ('sedentary', 'Sedentary (Little or no exercise)'),
        ('light', 'Lightly Active (1-3 days/week)'),
        ('moderate', 'Moderately Active (3-5 days/week)'),
        ('very_active', 'Very Active (6-7 days/week)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, default='')
    age = models.PositiveIntegerField(null=True, blank=True, default=None)
    height = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, default=None, help_text="Height in cm")
    current_weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, default=None, help_text="Current weight in kg")
    target_weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, default=None, help_text="Target weight in kg")
    fitness_goal = models.CharField(max_length=30, choices=GOAL_CHOICES, blank=True, default='')
    activity_level = models.CharField(max_length=30, choices=ACTIVITY_CHOICES, blank=True, default='')
    daily_water_goal = models.PositiveIntegerField(null=True, blank=True, default=None, help_text="Daily water intake goal in ml")
    daily_calorie_goal = models.PositiveIntegerField(null=True, blank=True, default=None, help_text="Daily target calories")
    bio = models.TextField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def bmi(self):
        if self.height and self.current_weight and float(self.height) > 0:
            height_m = float(self.height) / 100.0
            return round(float(self.current_weight) / (height_m ** 2), 1)
        return None

    @property
    def bmi_category(self):
        val = self.bmi
        if val is None:
            return {'label': 'Not Available', 'color': '#667085', 'badge': 'bg-gray-100 text-gray-700', 'status': 'Enter height and weight to calculate'}
        if val < 18.5:
            return {'label': 'Underweight', 'color': '#38BDF8', 'badge': 'bg-blue-100 text-blue-700', 'status': 'Aim for a nutrient-rich caloric surplus'}
        elif 18.5 <= val < 25.0:
            return {'label': 'Healthy Weight', 'color': '#16A34A', 'badge': 'bg-green-100 text-green-700', 'status': 'Optimal body mass! Maintain your active lifestyle'}
        elif 25.0 <= val < 30.0:
            return {'label': 'Overweight', 'color': '#FF6B35', 'badge': 'bg-orange-100 text-orange-700', 'status': 'Focus on regular workouts & balanced caloric intake'}
        else:
            return {'label': 'Obese', 'color': '#E53945', 'badge': 'bg-red-100 text-red-700', 'status': 'Consult a fitness coach or doctor for a tailored roadmap'}

    @property
    def full_name(self):
        full = f"{self.user.first_name} {self.user.last_name}".strip()
        return full if full else self.user.username

    @property
    def initials(self):
        first = self.user.first_name[:1].upper() if self.user.first_name else ''
        last = self.user.last_name[:1].upper() if self.user.last_name else ''
        if not first and not last:
            return self.user.username[:2].upper()
        return f"{first}{last}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
