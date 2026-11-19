from django.db import models
from django.contrib.auth.models import AbstractUser


class Admin(AbstractUser):
    """
    Admin model with fields:
    - username (unique)
    - password (hashed using Django's secure PBKDF2 algorithm)
    - email (unique)
    """
    email = models.EmailField(unique=True, verbose_name="Email Address")

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.email})"
