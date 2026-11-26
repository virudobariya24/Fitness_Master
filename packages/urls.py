from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('packages/', views.packages_list_view, name='packages_list'),
    path('packages/cards/', views.packages_cards_view, name='packages_cards'),
    path('packages/<int:pk>/', views.package_detail_view, name='package_detail'),
    path('packages/<int:pk>/book/', views.package_book_view, name='package_book'),
    path('packages/payment/razorpay-verify/', views.razorpay_verify_payment_view, name='razorpay_verify_payment'),
    path('packages/order/<int:order_id>/confirmation/', views.booking_confirmation_view, name='booking_confirmation'),
    path('user/orders/', views.user_orders_view, name='user_orders'),
    path('user/orders/<int:order_id>/', views.user_order_detail_view, name='user_order_detail'),
    path('admin-orders/', views.admin_orders_list_view, name='admin_orders'),
    path('packages/add/', views.package_add_view, name='package_add'),
    path('packages/<int:pk>/edit/', views.package_edit_view, name='package_edit'),
    path('packages/<int:pk>/delete/', views.package_delete_view, name='package_delete'),
]
