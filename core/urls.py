from django.urls import path
from . import views
from accounts.views import login_view, register_view, logout_view

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('programs/', views.programs_view, name='programs'),
    path('exercises/', views.exercises_view, name='public_exercises'),
    path('nutrition/', views.nutrition_view, name='public_nutrition'),
    path('contact/', views.contact_view, name='contact'),
    path('calculators/bmi/', views.bmi_calculator_view, name='bmi_calculator'),
    path('calculators/calories/', views.calories_calculator_view, name='calories_calculator'),
    
    # Direct auth shortcuts for public website
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]
