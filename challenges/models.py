from django.db import models
from django.conf import settings
from django.utils import timezone


class Challenge(models.Model):
    CHALLENGE_TYPES = [
        ('Workout', 'Workout Challenge'),
        ('Hydration', 'Hydration Challenge'),
        ('Walking', 'Daily Walking Challenge'),
        ('Weight Loss', 'Weight Loss Challenge'),
        ('Consistency', 'Streak & Consistency'),
    ]

    title = models.CharField(max_length=150)
    challenge_type = models.CharField(max_length=50, choices=CHALLENGE_TYPES, default='Workout')
    duration_days = models.PositiveIntegerField(default=30, help_text="Total duration in days")
    target_description = models.CharField(max_length=255, help_text="e.g. Complete 1 workout session daily")
    badge_name = models.CharField(max_length=100, default='Fitness Master Champion')
    badge_icon = models.CharField(max_length=50, default='fa-award')
    description = models.TextField()
    image = models.ImageField(upload_to='challenges/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.duration_days} Days)"


class ChallengeProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_enrollments')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    joined_date = models.DateField(default=timezone.now)
    days_completed = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'challenge')
        ordering = ['-joined_date']

    @property
    def progress_percentage(self):
        if self.challenge.duration_days > 0:
            return min(int((self.days_completed / self.challenge.duration_days) * 100), 100)
        return 0

    def check_and_complete(self):
        if self.days_completed >= self.challenge.duration_days and not self.is_completed:
            self.is_completed = True
            self.completion_date = timezone.now().date()
            self.save()
            # Automatically award achievement badge
            Achievement.objects.get_or_create(
                user=self.user,
                title=f"{self.challenge.badge_name}",
                defaults={
                    'description': f"Successfully completed the {self.challenge.title}!",
                    'badge_icon': self.challenge.badge_icon,
                    'badge_color': '#C6F135'
                }
            )

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.days_completed}/{self.challenge.duration_days} days)"


class Achievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    badge_icon = models.CharField(max_length=50, default='fa-trophy')
    badge_color = models.CharField(max_length=50, default='#C6F135')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
