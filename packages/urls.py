from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('packages/', views.packages_list_view, name='packages_list'),
    path('packages/cards/', views.packages_cards_view, name='packages_cards'),
    path('packages/<int:pk>/', views.package_detail_view, name='package_detail'),
    path('packages/add/', views.package_add_view, name='package_add'),
    path('packages/<int:pk>/edit/', views.package_edit_view, name='package_edit'),
    path('packages/<int:pk>/delete/', views.package_delete_view, name='package_delete'),
]
