from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.admin_login_view, name='custom_admin_login'),
    path('logout/', views.admin_logout_view, name='custom_admin_logout'),
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    
    # User Management
    path('users/', views.admin_users_view, name='admin_users'),
    path('users/add/', views.admin_user_add_view, name='admin_user_add'),
    path('users/<int:pk>/edit/', views.admin_user_edit_view, name='admin_user_edit'),
    path('users/<int:pk>/toggle-block/', views.admin_user_toggle_block_view, name='admin_user_toggle_block'),
    path('users/<int:pk>/delete/', views.admin_user_delete_view, name='admin_user_delete'),
    
    # Exercise Management
    path('exercises/', views.admin_exercises_view, name='admin_exercises'),
    path('exercises/add/', views.admin_exercise_add_view, name='admin_exercise_add'),
    path('exercises/<int:pk>/edit/', views.admin_exercise_edit_view, name='admin_exercise_edit'),
    path('exercises/<int:pk>/delete/', views.admin_exercise_delete_view, name='admin_exercise_delete'),
    
    # Workout Plans Management
    path('workouts/', views.admin_workouts_view, name='admin_workouts'),
    path('workouts/add/', views.admin_workout_add_view, name='admin_workout_add'),
    path('workouts/<int:pk>/edit/', views.admin_workout_edit_view, name='admin_workout_edit'),
    path('workouts/<int:pk>/delete/', views.admin_workout_delete_view, name='admin_workout_delete'),
    
    # Diet Plans Management
    path('diets/', views.admin_diets_view, name='admin_diets'),
    path('diets/add/', views.admin_diet_add_view, name='admin_diet_add'),
    path('diets/<int:pk>/edit/', views.admin_diet_edit_view, name='admin_diet_edit'),
    path('diets/<int:pk>/delete/', views.admin_diet_delete_view, name='admin_diet_delete'),
    
    # Challenges Management
    path('challenges/', views.admin_challenges_view, name='admin_challenges'),
    path('challenges/add/', views.admin_challenge_add_view, name='admin_challenge_add'),
    path('challenges/<int:pk>/edit/', views.admin_challenge_edit_view, name='admin_challenge_edit'),
    path('challenges/<int:pk>/delete/', views.admin_challenge_delete_view, name='admin_challenge_delete'),
    
    # Messages & Feedback
    path('messages/', views.admin_messages_view, name='admin_messages'),
    path('messages/<int:pk>/toggle-read/', views.admin_message_toggle_read_view, name='admin_message_toggle_read'),
    path('messages/<int:pk>/delete/', views.admin_message_delete_view, name='admin_message_delete'),
    
    # Analytics & Settings
    path('analytics/', views.admin_analytics_view, name='admin_analytics'),
    path('profile/', views.admin_profile_view, name='admin_profile'),
]
