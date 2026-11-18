from django.urls import path
from . import views

urlpatterns = [
    path('', views.diet_plans_view, name='user_diet_plans'),
    path('plan/<int:pk>/', views.diet_plan_detail_view, name='user_diet_detail'),
]
