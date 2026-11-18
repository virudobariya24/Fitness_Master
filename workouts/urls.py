from django.urls import path
from . import views

urlpatterns = [
    path('', views.workout_plans_list_view, name='user_workout_plans'),
    path('plan/<int:pk>/', views.workout_plan_detail_view, name='user_workout_detail'),
    path('plan/<int:pk>/start/', views.start_workout_view, name='user_start_workout'),
    path('log-workout/', views.log_workout_view, name='user_log_workout'),
    path('history/', views.workout_history_view, name='user_workout_history'),
    path('exercises/', views.exercise_library_view, name='user_exercise_library'),
]
