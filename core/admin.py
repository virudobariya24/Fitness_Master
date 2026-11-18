from django.contrib import admin
from .models import ContactMessage, Feedback


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_or_title', 'rating', 'is_featured', 'created_at')
    list_filter = ('rating', 'is_featured')
    search_fields = ('name', 'comment')
