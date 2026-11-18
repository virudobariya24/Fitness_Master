from django.db import models
from django.conf import settings
from django.utils import timezone


class WeightLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weight_logs')
    weight = models.DecimalField(max_digits=5, decimal_places=1, help_text="Weight in kg")
    recorded_date = models.DateField(default=timezone.now)
    notes = models.CharField(max_length=200, blank=True, help_text="e.g. Morning weigh-in, post workout")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.weight} kg ({self.recorded_date})"


class WaterLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='water_logs')
    date = models.DateField(default=timezone.now)
    glasses = models.PositiveIntegerField(default=0, help_text="Number of 250ml glasses consumed")
    amount_ml = models.PositiveIntegerField(default=0, help_text="Total ml consumed today")
    goal_ml = models.PositiveIntegerField(default=2500, help_text="Daily water goal in ml")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def save(self, *args, **kwargs):
        # Automatically update amount_ml if glasses changed
        if self.glasses and not self.amount_ml:
            self.amount_ml = self.glasses * 250
        super().save(*args, **kwargs)

    @property
    def percentage(self):
        if self.goal_ml > 0:
            return min(int((self.amount_ml / self.goal_ml) * 100), 100)
        return 0

    @property
    def remaining_ml(self):
        return max(self.goal_ml - self.amount_ml, 0)

    def __str__(self):
        return f"{self.user.username} - {self.amount_ml}ml on {self.date}"
