from django.urls import path
from . import views

urlpatterns = [
    # Website Root: Directly opens User Panel (Packages catalog / User Dashboard)
    path('', views.user_portal_root_view, name='root'),
    path('user/', views.user_portal_root_view, name='user_root'),

    # Admin Panel Gateway: Triggered when typing .../admin or .../admin/
    path('admin/', views.admin_gateway_view, name='admin_gateway'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    path('admins/', views.admin_accounts_view, name='admin_accounts'),
    path('registered-users/', views.admin_registered_users_view, name='admin_registered_users'),

    # User Panel (Registration, Session Login & Logout, Member Dashboard)
    path('register/', views.user_register_view, name='user_register'),
    path('user/register/', views.user_register_view, name='user_register_alias'),
    path('user/login/', views.user_login_view, name='user_login'),
    path('user/logout/', views.user_logout_view, name='user_logout'),
    path('user/dashboard/', views.user_dashboard_view, name='user_dashboard'),
]


