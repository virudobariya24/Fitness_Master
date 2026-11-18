from django.urls import path
from . import views

urlpatterns = [
    path('', views.progress_overview_view, name='user_progress_overview'),
    path('water/', views.water_tracker_view, name='user_water_tracker'),
    path('water/add/', views.add_water_quick_view, name='user_add_water'),
    path('water/quick/', views.add_water_quick_view, name='user_water_quick'),
    path('weight/', views.weight_tracker_view, name='user_weight_tracker'),
]
