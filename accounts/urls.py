from django.urls import path
from . import views

urlpatterns = [
    # Task (1): Admin Authentication
    path('', views.admin_login_view, name='root'),
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    path('admins/', views.admin_accounts_view, name='admin_accounts'),

    # Task (2) & (3): User Registration, Login & Logout (Django Sessions)
    path('register/', views.user_register_view, name='user_register'),
    path('user/register/', views.user_register_view, name='user_register_alias'),
    path('user/login/', views.user_login_view, name='user_login'),
    path('user/logout/', views.user_logout_view, name='user_logout'),
    path('user/dashboard/', views.user_dashboard_view, name='user_dashboard'),
]

