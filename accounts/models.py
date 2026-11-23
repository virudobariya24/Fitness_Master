from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password


class Admin(AbstractUser):
    """
    Task (2): Admin model with fields:
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


class User(models.Model):
    """
    Task (2): Custom User model with fields:
    - name: Full name of the user
    - username: Unique username for registration and login
    - email: Unique email address
    - password: Securely hashed password (PBKDF2 SHA-256)
    - created_at: Timestamp when user registered
    """
    name = models.CharField(max_length=150, verbose_name="Full Name", blank=True)
    username = models.CharField(max_length=150, unique=True, verbose_name="Username")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=255, verbose_name="Password (Hashed)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Registration Date")

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def set_password(self, raw_password):
        """Hash and set user's password using Django PBKDF2."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password against hashed password."""
        return check_password(raw_password, self.password)

    def __str__(self):
        display_name = self.name if self.name else self.username
        return f"{display_name} ({self.username}) - {self.email}"


# Alias for explicit custom user model references
CustomUser = User


class ContactMessage(models.Model):
    """
    Model to store inquiries submitted via the Contact Us form.
    Displays in the Admin Panel for administrator review and response.
    """
    name = models.CharField(max_length=150, verbose_name="Sender Name")
    email = models.EmailField(verbose_name="Sender Email")
    phone = models.CharField(max_length=25, blank=True, verbose_name="Phone Number")
    subject = models.CharField(max_length=200, verbose_name="Inquiry Subject")
    message = models.TextField(verbose_name="Message Content")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Submission Date")
    is_read = models.BooleanField(default=False, verbose_name="Read Status")

    class Meta:
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%b %d, %Y')})"
