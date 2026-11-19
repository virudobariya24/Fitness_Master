from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('packages/add/', views.package_add_view, name='package_add'),
    path('packages/<int:pk>/edit/', views.package_edit_view, name='package_edit'),
    path('packages/<int:pk>/delete/', views.package_delete_view, name='package_delete'),
]
