from django.contrib import admin
from .models import Packages, Order


@admin.register(Packages)
class PackagesAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'price', 'duration', 'access_hours',
        'classes_per_week', 'membership_duration',
        'drinking_package', 'personal_instructor'
    )
    search_fields = ('title', 'instruments', 'membership_duration')
    list_filter = ('membership_duration',)
    ordering = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'package_title', 'package_price',
        'status', 'payment_status', 'payment_method', 'razorpay_payment_id', 'booking_date'
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'booking_date')
    search_fields = ('order_number', 'user__username', 'user__email', 'package_title', 'razorpay_payment_id', 'razorpay_order_id')
    ordering = ('-booking_date',)

