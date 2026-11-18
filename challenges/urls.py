from django.urls import path
from . import views

urlpatterns = [
    path('', views.challenges_list_view, name='user_challenges'),
    path('join/<int:pk>/', views.join_challenge_view, name='user_join_challenge'),
    path('check-in/<int:pk>/', views.checkin_challenge_day_view, name='user_checkin_challenge'),
    path('achievements/', views.achievements_view, name='user_achievements'),
]
