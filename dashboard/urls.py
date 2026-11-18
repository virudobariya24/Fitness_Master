from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_overview_view, name='user_dashboard'),
    path('', views.dashboard_overview_view, name='user_dashboard_root'),
]
