from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login_view, name='root'),
    path('login/', views.admin_login_view, name='login'),
    path('logout/', views.admin_logout_view, name='logout'),
    path('admins/', views.admin_accounts_view, name='admin_accounts'),
]
