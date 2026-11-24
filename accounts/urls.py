from django.urls import path
from . import views

urlpatterns = [
    # Website Root: Directly opens User Panel (Packages catalog / User Dashboard)
    path('', views.user_portal_root_view, name='root'),
    path('user/', views.user_portal_root_view, name='user_root'),

    # Admin Panel Gateway: Triggered when typing .../admin or .../admin/
    path('admin/', views.admin_gateway_view, name='admin_gateway'),
    path('admin', views.admin_gateway_view, name='admin_gateway_no_slash'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    path('admins/', views.admin_accounts_view, name='admin_accounts'),
    path('registered-users/', views.admin_registered_users_view, name='admin_registered_users'),
    path('contact-inquiries/', views.admin_contact_messages_view, name='admin_contact_messages'),
    path('contact-inquiries/<int:pk>/toggle-read/', views.admin_contact_toggle_read_view, name='admin_contact_toggle_read'),
    path('contact-inquiries/<int:pk>/delete/', views.admin_contact_delete_view, name='admin_contact_delete'),

    # User Panel (Registration, Session Login & Logout, Member Dashboard)
    path('register/', views.user_register_view, name='user_register'),
    path('user/register/', views.user_register_view, name='user_register_alias'),
    path('user/login/', views.user_login_view, name='user_login'),
    path('user/logout/', views.user_logout_view, name='user_logout'),
    path('user/dashboard/', views.user_dashboard_view, name='user_dashboard'),

    # Password Reset via Email OTP (Task: Forgot Password & OTP flow)
    path('user/forgot-password/', views.user_forgot_password_view, name='user_forgot_password'),
    path('user/verify-otp/', views.user_verify_otp_view, name='user_verify_otp'),
    path('user/resend-otp/', views.user_resend_otp_view, name='user_resend_otp'),
    path('user/reset-password/', views.user_reset_password_view, name='user_reset_password'),

    # Public & Member Information Pages
    path('about/', views.about_us_view, name='about_us'),
    path('contact/', views.contact_us_view, name='contact_us'),
]


